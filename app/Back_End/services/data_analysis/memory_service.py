"""MemoryService — short-term memory (in-chat) + long-term memory (cross-chat).

Short-term memory: the last N messages in the same session, fed into
the agent's prompt as "Conversation so far" so follow-up questions
("now sort that descending") resolve correctly.

Long-term memory: IMPLEMENTED. After every successful analysis, the
service triggers two LLM calls to extract:
1. User preferences (chart_type, currency, language, industry, etc.)
   → upserted into UserPreference rows.
2. Durable facts (topics of interest, skill gaps, context) → inserted
   into LongTermMemory rows.

Before every agent run, the service pulls the user's top N preferences
and top M memories and returns them as a formatted "User context"
string for injection into the code-gen prompt.

Performance note: long-term memory extraction adds 2 LLM calls per
analysis. Disable via `settings.long_term_memory_enabled = False` if
you need max speed (e.g. during load testing).
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.Back_End.core.config import settings
from app.Back_End.core.data_analysis.exceptions import LLMError
from app.Back_End.core.llm import get_llm_client
from app.Back_End.models.data_analysis.long_term_memory import LongTermMemory, UserPreference
from app.Back_End.repositories.data_analysis.memory_repository import (
    LongTermMemoryRepository, UserPreferenceRepository,
)
from app.Back_End.repositories.data_analysis.message_repository import MessageRepository

logger = logging.getLogger(__name__)


# Hard caps to prevent a runaway extractor from flooding the DB.
_MAX_PREFERENCES_PER_TURN = 5
_MAX_FACTS_PER_TURN = 3


class MemoryService:
    """Short-term chat memory + cross-chat long-term memory."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.message_repo = MessageRepository(db)
        self.prefs_repo = UserPreferenceRepository(db)
        self.memory_repo = LongTermMemoryRepository(db)
        self.llm_client = get_llm_client()

    # --- Short-term memory (in-chat context) -------------------------------

    def get_recent_history(
        self,
        session_id: uuid.UUID,
        *,
        limit: int | None = None,
    ) -> list[dict[str, str]]:
        """Return the most recent N prior turns as {"role":..., "content":...}.

        limit defaults to settings.short_term_memory_window. The list
        is oldest-first so the LLM sees them in chronological order.
        """
        limit = limit or settings.short_term_memory_window
        messages = self.message_repo.recent_for_session(session_id, limit=limit)
        return [
            {"role": m.role, "content": m.content}
            for m in messages
            if m.content
        ]

    # --- Long-term memory: extraction --------------------------------------

    def extract_preferences(
        self,
        *,
        user_id: uuid.UUID,
        session_id: uuid.UUID,
        question: str,
        response_summary: str,
    ) -> int:
        """Extract user preferences from a single Q&A turn.

        Returns the number of preferences upserted. Failures are logged
        and return 0 — extraction never raises.
        """
        if not settings.long_term_memory_enabled:
            return 0

        # Lazy import to avoid circular at module load.
        from app.Back_End.prompts.data_analysis.memory_extraction import build_preference_extraction_prompt

        prompt = build_preference_extraction_prompt(question, response_summary)

        try:
            raw = self.llm_client.chat(
                user_prompt=prompt,
                model=settings.llm_model,
            )
        except LLMError as exc:
            logger.warning("Preference extraction LLM call failed: %s", exc)
            return 0

        prefs_data = self._safe_parse_json(raw, key="preferences")
        if not prefs_data:
            return 0

        count = 0
        for pref in prefs_data[:_MAX_PREFERENCES_PER_TURN]:
            try:
                category = str(pref["category"])
                key = str(pref["key"])
                value = str(pref["value"])
                confidence = float(pref.get("confidence", 0.5))
            except (KeyError, TypeError, ValueError) as exc:
                logger.debug("Skipping malformed preference %r: %s", pref, exc)
                continue

            if confidence < 0.5:
                continue

            self._upsert_preference(
                user_id=user_id,
                session_id=session_id,
                category=category,
                key=key,
                value=value,
                confidence=confidence,
            )
            count += 1

        if count:
            self.db.commit()
            logger.info("Extracted %d preferences from session %s", count, session_id)
        return count

    def extract_facts(
        self,
        *,
        user_id: uuid.UUID,
        session_id: uuid.UUID,
        question: str,
        response_summary: str,
    ) -> int:
        """Extract durable facts from a single Q&A turn.

        Returns the number of facts inserted. Failures are logged and
        return 0 — extraction never raises.
        """
        if not settings.long_term_memory_enabled:
            return 0

        from app.Back_End.prompts.data_analysis.memory_extraction import build_fact_extraction_prompt

        prompt = build_fact_extraction_prompt(question, response_summary)

        try:
            raw = self.llm_client.chat(
                user_prompt=prompt,
                model=settings.llm_model,
            )
        except LLMError as exc:
            logger.warning("Fact extraction LLM call failed: %s", exc)
            return 0

        facts_data = self._safe_parse_json(raw, key="facts")
        if not facts_data:
            return 0

        count = 0
        for fact in facts_data[:_MAX_FACTS_PER_TURN]:
            try:
                kind = str(fact["kind"])
                content = str(fact["content"])
                importance = float(fact.get("importance", 0.5))
            except (KeyError, TypeError, ValueError) as exc:
                logger.debug("Skipping malformed fact %r: %s", fact, exc)
                continue

            if importance < 0.5:
                continue

            # Dedup: skip if an identical fact already exists for this user.
            existing = self.db.query(LongTermMemory).filter(
                LongTermMemory.user_id == user_id,
                LongTermMemory.content == content,
            ).first()
            if existing is not None:
                # Bump importance if the new one is higher; otherwise skip.
                if importance > existing.importance:
                    existing.importance = importance
                    self.db.flush()
                continue

            memory = LongTermMemory(
                user_id=user_id,
                kind=kind,
                content=content,
                importance=importance,
                source_session_id=session_id,
            )
            self.memory_repo.add(memory)
            count += 1

        if count:
            self.db.commit()
            logger.info("Extracted %d facts from session %s", count, session_id)
        return count

    # --- Long-term memory: injection into agent prompt ---------------------

    def get_context_for_agent(self, user_id: uuid.UUID) -> str:
        """Return a formatted "User context" block for the agent prompt.

        Empty string when there's no stored memory yet (so the prompt
        builder can just skip the section). Pulls:
        - Top N preferences (above the confidence threshold)
        - Top M memories (by importance, then recency)
        """
        if not settings.long_term_memory_enabled:
            return ""

        prefs = self.prefs_repo.list_for_user(user_id)
        # Filter by confidence threshold + take top N.
        prefs = [
            p for p in prefs
            if p.confidence >= settings.memory_min_confidence_to_inject
        ][:settings.memory_inject_top_preferences]

        memories = self.memory_repo.list_for_user(
            user_id, limit=settings.memory_inject_top_memories,
        )

        if not prefs and not memories:
            return ""

        lines: list[str] = ["User context (cross-chat memory):"]

        if prefs:
            lines.append("Known preferences:")
            for p in prefs:
                lines.append(f"  - [{p.category}] {p.key} = {p.value} (confidence: {p.confidence:.2f})")

        if memories:
            lines.append("Things to remember about this user:")
            for m in memories:
                lines.append(f"  - ({m.kind}, importance: {m.importance:.2f}) {m.content}")

        # Touch last_accessed_at on the surfaced memories so they don't
        # get garbage-collected by future decay sweeps.
        for m in memories:
            m.last_accessed_at = datetime.now(timezone.utc)
        if memories:
            self.db.flush()

        return "\n".join(lines)

    # --- Internals ---------------------------------------------------------

    def _upsert_preference(
        self,
        *,
        user_id: uuid.UUID,
        session_id: uuid.UUID,
        category: str,
        key: str,
        value: str,
        confidence: float,
    ) -> None:
        """Insert or update a user preference.

        If a pref with the same (user, category, key) exists, update
        its value + confidence + last_confirmed_at. Otherwise insert.
        """
        existing = self.prefs_repo.get_by_key(user_id, category, key)
        if existing is not None:
            existing.value = value
            # Confidence ratchets up only — never let a lower-confidence
            # extraction overwrite a higher one we already had.
            if confidence > existing.confidence:
                existing.confidence = confidence
            existing.last_confirmed_at = datetime.now(timezone.utc)
            existing.source_session_id = session_id
            self.db.flush()
            return

        pref = UserPreference(
            user_id=user_id,
            category=category,
            key=key,
            value=value,
            confidence=confidence,
            last_confirmed_at=datetime.now(timezone.utc),
            source_session_id=session_id,
        )
        self.prefs_repo.add(pref)

    @staticmethod
    def _safe_parse_json(raw: str, *, key: str) -> list[dict[str, Any]]:
        """Parse the LLM's JSON response defensively.

        Strips markdown fences if present, then parses. Returns the
        list under `key` (e.g. "preferences" or "facts"). On any
        failure, returns an empty list.
        """
        if not raw or not raw.strip():
            return []

        text = raw.strip()
        # Strip ```json ... ``` fences if the LLM added them despite
        # the instruction not to.
        if text.startswith("```"):
            lines = text.splitlines()
            if len(lines) >= 2:
                # Drop first line (```json) and last line (```).
                text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            logger.warning("Failed to parse LLM JSON response: %s", exc)
            return []

        items = data.get(key, []) if isinstance(data, dict) else []
        if not isinstance(items, list):
            return []
        return [item for item in items if isinstance(item, dict)]
