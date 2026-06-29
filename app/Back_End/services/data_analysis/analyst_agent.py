"""AnalystAgent — the data-analyst agent, ported from standalone KnowMate.

This is the V3 of agent.py — same pipeline, but session-aware:

    load cached dataset → load cached profile → detect intents →
    extract entities → resolve columns → build code-gen prompt (WITH
    conversation history) → call LLM → execute code → generate insight
    → assemble response + persist the message to the DB
"""

from __future__ import annotations

import logging
import time
import uuid
from typing import Any

import pandas as pd
from sqlalchemy.orm import Session

from KnowMate.app.Back_End.core.config import settings
from KnowMate.app.Back_End.core.data_analysis.exceptions import DatasetNotAttachedError, LLMError, NotFoundError
from KnowMate.app.Back_End.core.llm import get_llm_client
from execution.executor import ExecutionOutcome, execute_code
from KnowMate.app.Back_End.models.data_analysis.message import Message
from KnowMate.app.Back_End.prompts.data_analysis.code_generation import build_code_generation_prompt
from KnowMate.app.Back_End.prompts.data_analysis.code_retry import build_code_retry_prompt
from KnowMate.app.Back_End.prompts.data_analysis.insight_generation import build_insight_generation_prompt
from KnowMate.app.Back_End.prompts.data_analysis.nlu.column_resolver import resolve_columns
from KnowMate.app.Back_End.prompts.data_analysis.nlu.entity_extractor import extract_entities
from KnowMate.app.Back_End.prompts.data_analysis.nlu.intent_detector import detect_intents
from KnowMate.app.Back_End.prompts.data_analysis.system_prompts import SYSTEM_PROMPT
from KnowMate.app.Back_End.repositories.data_analysis.message_repository import MessageRepository
from KnowMate.app.Back_End.schemas.data_analysis.message import (
    AnalysisResult, AnalyzeResponse, ChartData, ColumnResolution,
    DatasetProfile, ExtractedEntities, Intent, MessageCreateRequest,
)
from services.agent_service import AgentContext, AgentService
from KnowMate.app.Back_End.services.data_analysis.dataset_service import DatasetService
from KnowMate.app.Back_End.services.data_analysis.memory_service import MemoryService

logger = logging.getLogger(__name__)

INSIGHT_TABLE_PREVIEW_ROWS = 10
MAX_STATS_COLUMNS = 6


class AnalystAgent:
    """The data-analyst agent. Implements the AgentService protocol."""

    name: str = "analyst"
    description: str = (
        "Answers natural-language questions about an uploaded dataset by "
        "generating and executing pandas code via a local LLM."
    )

    def __init__(self, db: Session) -> None:
        self.db = db
        self.dataset_service = DatasetService(db)
        self.memory_service = MemoryService(db)
        self.message_repo = MessageRepository(db)
        self.llm_client = get_llm_client()

    def can_handle(self, context: AgentContext) -> float:
        return 1.0

    def handle(self, context: AgentContext) -> AnalyzeResponse:
        return self.analyze(
            user_id=context.user_id,
            session_id=context.session_id,
            request=context.request,
        )

    def analyze(
        self,
        *,
        user_id: uuid.UUID,
        session_id: uuid.UUID,
        request: MessageCreateRequest,
    ) -> AnalyzeResponse:
        """Run the full pipeline. Never raises."""
        start_time = time.perf_counter()

        def _elapsed() -> float:
            return time.perf_counter() - start_time

        user_message = self._persist_message(
            session_id=session_id,
            role="user",
            content=request.question,
        )

        try:
            dataset = self.dataset_service.get_for_session(
                user_id=user_id, session_id=session_id,
            )
            df = self.dataset_service.load_dataframe(dataset)
            profile = self.dataset_service.get_cached_profile(dataset)

            history = self.memory_service.get_recent_history(session_id)
            user_context = self.memory_service.get_context_for_agent(user_id)

            intent_values = detect_intents(request.question)
            intents = [Intent(value=v) for v in intent_values]
            entities: ExtractedEntities = extract_entities(request.question, profile)
            resolved_columns: list[ColumnResolution] = resolve_columns(
                entities, list(df.columns),
            )

            code_prompt = build_code_generation_prompt(
                profile=profile,
                question=request.question,
                intents=intents,
                entities=entities,
                resolved_columns=resolved_columns,
                conversation_history=history,
                user_context=user_context,
            )

            try:
                raw_code = self.llm_client.chat(
                    user_prompt=code_prompt,
                    system_prompt=SYSTEM_PROMPT,
                    model=settings.llm_model,
                )
            except LLMError as exc:
                return self._build_failure_response(
                    session_id, user_message, _elapsed(),
                    error=f"Code generation failed: {exc}",
                    raw_code=None,
                    intents=intents, entities=entities,
                    resolved_columns=resolved_columns,
                    debug=request.debug,
                )

            # --- Stage 8: validate + execute code (with self-healing retries) ---
            outcome: ExecutionOutcome = execute_code(raw_code, df)

            retry_count = 0
            max_retries = settings.code_retry_max_attempts
            while not outcome.success and retry_count < max_retries:
                retry_count += 1
                logger.info(
                    "Code execution failed (attempt %d/%d). Error: %s. Asking LLM to fix...",
                    retry_count, max_retries, outcome.error,
                )
                try:
                    retry_prompt = build_code_retry_prompt(
                        question=request.question,
                        previous_code=raw_code,
                        error=outcome.error or "unknown error",
                    )
                    raw_code = self.llm_client.chat(
                        user_prompt=retry_prompt,
                        system_prompt=SYSTEM_PROMPT,
                        model=settings.llm_model,
                    )
                    outcome = execute_code(raw_code, df)
                except LLMError as exc:
                    logger.warning("Retry LLM call failed: %s", exc)
                    break

            if not outcome.success:
                return self._build_failure_response(
                    session_id, user_message, _elapsed(),
                    error=outcome.error,
                    raw_code=raw_code,
                    intents=intents, entities=entities,
                    resolved_columns=resolved_columns,
                    debug=request.debug,
                )

            result: AnalysisResult = outcome.result  # type: ignore[assignment]

            insight_text = self._generate_insight(
                request.question, result, intents,
            )
            final_insight = insight_text or result.summary

            charts: list[ChartData] = []
            if result.figures:
                charts = result.figures
            elif result.figure is not None:
                charts = [result.figure]

            response = AnalyzeResponse(
                success=True,
                session_id=session_id,
                message_id=uuid.uuid4(),
                summary=result.summary,
                generated_code=raw_code,
                insights=final_insight,
                table=result.table,
                chart=charts[0] if charts else None,
                charts=charts if charts else None,
                execution_time=_elapsed(),
                errors=None,
                **self._debug_fields(request.debug, intents, entities, resolved_columns),
            )

            assistant_message = self._persist_message(
                session_id=session_id,
                role="assistant",
                content=final_insight or result.summary or "",
                meta=response.model_dump(mode="json"),
                processing_time_seconds=_elapsed(),
            )
            response.message_id = assistant_message.id

            try:
                response_summary = (
                    result.summary or final_insight or "(no summary)"
                )
                self.memory_service.extract_preferences(
                    user_id=user_id,
                    session_id=session_id,
                    question=request.question,
                    response_summary=response_summary,
                )
                self.memory_service.extract_facts(
                    user_id=user_id,
                    session_id=session_id,
                    question=request.question,
                    response_summary=response_summary,
                )
            except Exception:  # noqa: BLE001
                logger.warning("Memory extraction failed (non-fatal).", exc_info=True)

            return response

        except DatasetNotAttachedError as exc:
            return self._build_failure_response(
                session_id, user_message, _elapsed(),
                error=str(exc), raw_code=None,
                intents=[], entities=ExtractedEntities(),
                resolved_columns=[], debug=request.debug,
            )
        except NotFoundError as exc:
            return self._build_failure_response(
                session_id, user_message, _elapsed(),
                error=str(exc), raw_code=None,
                intents=[], entities=ExtractedEntities(),
                resolved_columns=[], debug=request.debug,
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception("Unexpected failure in AnalystAgent.analyze().")
            return self._build_failure_response(
                session_id, user_message, _elapsed(),
                error=f"Unexpected failure: {type(exc).__name__}: {exc}",
                raw_code=None,
                intents=[], entities=ExtractedEntities(),
                resolved_columns=[], debug=request.debug,
            )

    def _generate_insight(
        self,
        question: str,
        result: AnalysisResult,
        intents: list[Intent],
    ) -> str | None:
        execution_output = self._render_execution_output_for_insight(result)
        if not execution_output:
            return None

        insight_prompt = build_insight_generation_prompt(question, execution_output, intents)
        try:
            text = self.llm_client.chat(
                user_prompt=insight_prompt,
                model=settings.llm_model,
            )
            return text.strip()
        except LLMError as exc:
            logger.warning("Insight generation failed, falling back to summary only: %s", exc)
            return None

    def _render_execution_output_for_insight(self, result: AnalysisResult) -> str:
        lines: list[str] = []

        if result.table:
            stats_block = _compute_table_statistics(result.table)
            if stats_block:
                lines.append(stats_block)
            preview = result.table[:INSIGHT_TABLE_PREVIEW_ROWS]
            lines.append(f"Raw row sample ({len(result.table)} total rows): {preview}")

        if result.kpis:
            kpi_str = ", ".join(f"{key}={value}" for key, value in result.kpis.items())
            lines.append(f"KPIs: {kpi_str}")

        if result.summary:
            lines.append(
                "Code-generated summary (cross-check against the stats above, "
                f"do not trust blindly): {result.summary}"
            )

        all_charts = result.figures or ([result.figure] if result.figure else [])
        if all_charts:
            chart_types = [c.type for c in all_charts]
            lines.append(
                f"{len(all_charts)} chart(s) generated ({', '.join(chart_types)}) "
                f"from this data."
            )

        if not lines:
            lines.append("No table, KPIs, or summary was produced by the analysis.")

        return "\n".join(lines)

    def _persist_message(
        self,
        *,
        session_id: uuid.UUID,
        role: str,
        content: str,
        meta: dict | None = None,
        processing_time_seconds: float | None = None,
    ) -> Message:
        seq = self.message_repo.next_seq(session_id)
        message = Message(
            session_id=session_id,
            seq=seq,
            role=role,
            content=content,
            meta=meta,
            processing_time_seconds=processing_time_seconds,
        )
        self.message_repo.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message

    def _build_failure_response(
        self,
        session_id: uuid.UUID,
        user_message: Message,
        elapsed: float,
        *,
        error: str,
        raw_code: str | None,
        intents: list[Intent],
        entities: ExtractedEntities,
        resolved_columns: list[ColumnResolution],
        debug: bool,
    ) -> AnalyzeResponse:
        assistant_message = self._persist_message(
            session_id=session_id,
            role="assistant",
            content=f"(analysis failed: {error})",
            meta={"success": False, "error": error},
            processing_time_seconds=elapsed,
        )
        return AnalyzeResponse(
            success=False,
            session_id=session_id,
            message_id=assistant_message.id,
            summary=None,
            generated_code=raw_code,
            insights=None,
            table=None,
            chart=None,
            charts=None,
            execution_time=elapsed,
            errors=error,
            **self._debug_fields(debug, intents, entities, resolved_columns),
        )

    @staticmethod
    def _debug_fields(
        debug: bool,
        intents: list[Intent],
        entities: ExtractedEntities,
        resolved_columns: list[ColumnResolution],
    ) -> dict:
        if not debug:
            return {}
        return {
            "detected_intents": [i.value for i in intents],
            "entities": entities,
            "resolved_columns": resolved_columns,
        }


def _compute_table_statistics(table: list[dict[str, Any]]) -> str:
    if not table:
        return ""

    result_df = pd.DataFrame(table)
    lines: list[str] = [
        f"Result table: {len(result_df)} rows, {len(result_df.columns)} columns "
        f"({', '.join(str(c) for c in result_df.columns)})"
    ]

    numeric_cols = result_df.select_dtypes(include="number").columns.tolist()
    other_cols = [c for c in result_df.columns if c not in numeric_cols]

    for col in numeric_cols[:MAX_STATS_COLUMNS]:
        series = result_df[col].dropna()
        if series.empty:
            continue
        lines.append(f"- {col}: min={series.min():.2f}, mean={series.mean():.2f}, max={series.max():.2f}")

    for col in other_cols[:MAX_STATS_COLUMNS]:
        counts = result_df[col].value_counts().head(3)
        if counts.empty:
            continue
        formatted = ", ".join(f"{value!r}: {count}" for value, count in counts.items())
        lines.append(f"- {col} (top values): {formatted}")

    if numeric_cols:
        primary = numeric_cols[0]
        label_col = other_cols[0] if other_cols else None
        valid_rows = result_df.dropna(subset=[primary])

        if not valid_rows.empty:
            max_row = valid_rows.loc[valid_rows[primary].idxmax()]
            min_row = valid_rows.loc[valid_rows[primary].idxmin()]

            def _label(row: pd.Series) -> str:
                return str(row[label_col]) if label_col else f"row {row.name}"

            lines.append(f"- Highest {primary}: {_label(max_row)} ({max_row[primary]:.2f})")
            lines.append(f"- Lowest {primary}: {_label(min_row)} ({min_row[primary]:.2f})")

    return "\n".join(lines)


def _register_default_agent() -> None:
    from services.agent_service import register_agent

    class _AnalystAgentRegistration:
        name = AnalystAgent.name
        description = AnalystAgent.description
        def can_handle(self, context: AgentContext) -> float:  # pragma: no cover
            return 1.0
        def handle(self, context: AgentContext) -> AnalyzeResponse:  # pragma: no cover
            raise RuntimeError("Use AnalystAgent(db) directly; orchestrator not implemented yet.")

    register_agent(_AnalystAgentRegistration())


_register_default_agent()