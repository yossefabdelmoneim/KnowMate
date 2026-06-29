"""Long-term memory models — STUB for future preference extraction.

Two parallel concepts:
1. `UserPreference` — semi-static key/value facts about a user
   ("prefers dark mode", "favorite chart type: bar", "currency: EGP",
   "industry: retail"). Cross-session. Updated incrementally as
   evidence accumulates.
2. `LongTermMemory` — free-form episodic facts and summaries
   ("User asked 5 questions about Q3 sales", "User cares most about
   top-performing regions"). Cross-session. Surfaces as context to
   future agent calls.

Both tables exist as a schema-only stub for now — the extraction
service (services/memory_service.py) leaves the populate/extract
methods empty per the user's "long-term memory not now" decision.
When ready:
1. Implement `MemoryService.extract_preferences()` and
   `.extract_facts()` to scan recent sessions and populate these rows.
2. Inject the stored prefs/facts into the agent's prompt in
   services/analyst_agent.py's prompt builder.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from KnowMate.app.Back_End.db.data_analysis.base import Base
from KnowMate.app.Back_End.db.data_analysis.types import JSONB
from KnowMate.app.Back_End.models.data_analysis._mixins import TimestampMixin, UUIDPkMixin


class UserPreference(Base, UUIDPkMixin, TimestampMixin):
    """Key/value user preference, cross-session.

    `category` is a coarse bucket ("ui", "domain", "formatting") so
    the UI / agent can pull a slice without scanning all prefs.
    `confidence` (0-1) reflects how strongly we believe this pref
    is real — useful when surfacing prefs that conflict.
    """

    __tablename__ = "user_preferences"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    category: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    key: Mapped[str] = mapped_column(String(128), nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False)

    confidence: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)

    # When this pref was last confirmed by new evidence (resets
    # staleness calculations).
    last_confirmed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )

    # Optional provenance — which session/message caused us to record
    # this pref. Useful for debugging "why did the agent think I
    # prefer bar charts?"
    source_session_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("chat_sessions.id", ondelete="SET NULL"),
        nullable=True,
    )

    user: Mapped["User"] = relationship(  # noqa: F821
        back_populates="preferences",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<UserPreference user_id={self.user_id} {self.category}.{self.key}={self.value!r}>"


class LongTermMemory(Base, UUIDPkMixin, TimestampMixin):
    """Free-form fact extracted from chat history, cross-session.

    `kind` discriminates between fact types ("preference_inferred",
    "topic_of_interest", "skill_gap", "summary"). `content` is the
    human/LLM-readable text; `meta` holds structured details if any.
    """

    __tablename__ = "long_term_memories"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    kind: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    importance: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)
    meta: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    source_session_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("chat_sessions.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Memories decay over time so the agent doesn't drag ancient
    # context forever. `last_accessed_at` updates when a memory is
    # surfaced to the agent; old, low-importance, never-accessed
    # memories can be garbage-collected later.
    last_accessed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )

    user: Mapped["User"] = relationship(  # noqa: F821
        back_populates="memories",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<LongTermMemory user_id={self.user_id} kind={self.kind!r}>"
