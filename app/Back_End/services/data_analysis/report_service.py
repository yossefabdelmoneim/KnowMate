"""ReportService — orchestrates multi-section report generation.

Flow:
1. Persist the user's high-level question as a Message (role=user).
2. Call the LLM with the OUTLINE_PROMPT to get a structured outline
   (report title + list of sections, each with a sub-question + intent).
3. For each section, run the existing AnalystAgent.analyze() pipeline
   on the sub-question. Each section gets its own code/table/charts/insight.
4. For each section, call the LLM with the SECTION_SUMMARY_PROMPT to
   produce a 2-4 sentence section summary.
5. Call the LLM with the REPORT_ASSEMBLY_PROMPT to produce an executive
   summary + recommendations from all the section summaries.
6. Persist the final report as a single Message (role=assistant) with
   the full ReportResponse structure stored as JSON in `meta`.

Cost note: a 5-section report makes approximately:
  - 1 outline call
  - 5 × (1 code-gen call + 1 insight call) = 10 calls
  - 5 section-summary calls
  - 1 assembly call
  - 2 long-term memory extraction calls (if enabled)
  ≈ 19 LLM calls total. This is intentional — reports are expensive.
"""

from __future__ import annotations

import json
import logging
import time
import uuid
from typing import Any

import pandas as pd
from sqlalchemy.orm import Session

from app.Back_End.core.config import settings
from app.Back_End.core.data_analysis.exceptions import DatasetNotAttachedError, LLMError, NotFoundError
from app.Back_End.core.llm import get_llm_client
from app.Back_End.models.data_analysis.message import Message
from app.Back_End.prompts.data_analysis.code_generation import _format_dataset_profile
from app.Back_End.prompts.data_analysis.report_generation import (
    build_outline_prompt, build_report_assembly_prompt,
    build_section_summary_prompt,
)
from app.Back_End.repositories.data_analysis.message_repository import MessageRepository
from app.Back_End.schemas.data_analysis.message import (
    AnalysisResult, ChartData, DatasetProfile, ExtractedEntities, Intent,
    MessageCreateRequest, ReportCreateRequest, ReportResponse, ReportSection,
)
from app.Back_End.services.data_analysis.analyst_agent import AnalystAgent
from app.Back_End.services.data_analysis.dataset_service import DatasetService
from app.Back_End.services.data_analysis.memory_service import MemoryService

logger = logging.getLogger(__name__)


class ReportService:
    """Orchestrates multi-section report generation."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.message_repo = MessageRepository(db)
        self.dataset_service = DatasetService(db)
        self.memory_service = MemoryService(db)
        self.analyst_agent = AnalystAgent(db)
        self.llm_client = get_llm_client()

    def generate(
        self,
        *,
        user_id: uuid.UUID,
        session_id: uuid.UUID,
        request: ReportCreateRequest,
    ) -> ReportResponse:
        """Generate a full multi-section report. Never raises."""
        start_time = time.perf_counter()

        def _elapsed() -> float:
            return time.perf_counter() - start_time

        user_message = self._persist_message(
            session_id=session_id,
            role="user",
            content=request.question,
            meta={"kind": "report_request", "max_sections": request.max_sections},
        )

        try:
            dataset = self.dataset_service.get_for_session(
                user_id=user_id, session_id=session_id,
            )
            df = self.dataset_service.load_dataframe(dataset)
            profile = self.dataset_service.get_cached_profile(dataset)
            user_context = self.memory_service.get_context_for_agent(user_id)
            profile_text = _format_dataset_profile(profile)

            outline = self._generate_outline(
                question=request.question,
                profile_text=profile_text,
                user_context=user_context,
                max_sections=request.max_sections,
            )

            report_title = outline.get("report_title", "Data Analysis Report")
            sections_plan = outline.get("sections", [])[:request.max_sections]

            if not sections_plan:
                sections_plan = [{
                    "title": "Overview",
                    "sub_question": request.question,
                    "intent": "summary",
                }]

            sections: list[ReportSection] = []
            for idx, plan in enumerate(sections_plan, start=1):
                logger.info(
                    "Report %s: generating section %d/%d (%s)",
                    session_id, idx, len(sections_plan), plan.get("title"),
                )
                section = self._generate_section(
                    user_id=user_id,
                    session_id=session_id,
                    plan=plan,
                    df=df,
                    profile=profile,
                    user_context=user_context,
                    conversation_history=self._build_section_history(
                        request.question, sections,
                    ),
                    debug=request.debug,
                )
                sections.append(section)

            executive_summary, recommendations = self._assemble_report(
                report_title=report_title,
                question=request.question,
                sections=sections,
            )

            response = ReportResponse(
                success=True,
                session_id=session_id,
                message_id=uuid.uuid4(),
                title=report_title,
                executive_summary=executive_summary,
                sections=sections,
                recommendations=recommendations,
                total_execution_time=_elapsed(),
                errors=None,
            )

            assistant_message = self._persist_message(
                session_id=session_id,
                role="assistant",
                content=executive_summary or report_title,
                meta={"kind": "report", "report": response.model_dump(mode="json")},
                processing_time_seconds=_elapsed(),
            )
            response.message_id = assistant_message.id

            try:
                self.memory_service.extract_preferences(
                    user_id=user_id, session_id=session_id,
                    question=request.question,
                    response_summary=executive_summary or report_title,
                )
                self.memory_service.extract_facts(
                    user_id=user_id, session_id=session_id,
                    question=request.question,
                    response_summary=executive_summary or report_title,
                )
            except Exception:  # noqa: BLE001
                logger.warning("Memory extraction failed (non-fatal).", exc_info=True)

            return response

        except DatasetNotAttachedError as exc:
            return self._build_failure_response(
                session_id, user_message, _elapsed(),
                report_title="Report Generation Failed",
                error=str(exc),
            )
        except NotFoundError as exc:
            return self._build_failure_response(
                session_id, user_message, _elapsed(),
                report_title="Report Generation Failed",
                error=str(exc),
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception("Unexpected failure in ReportService.generate().")
            return self._build_failure_response(
                session_id, user_message, _elapsed(),
                report_title="Report Generation Failed",
                error=f"Unexpected failure: {type(exc).__name__}: {exc}",
            )

    def _generate_outline(
        self,
        *,
        question: str,
        profile_text: str,
        user_context: str,
        max_sections: int,
    ) -> dict[str, Any]:
        prompt = build_outline_prompt(question, profile_text, user_context, max_sections)
        try:
            raw = self.llm_client.chat(
                user_prompt=prompt, model=settings.llm_model,
            )
        except LLMError as exc:
            logger.warning("Outline generation failed: %s — falling back to single section.", exc)
            return {
                "report_title": "Data Analysis Report",
                "sections": [{
                    "title": "Overview",
                    "sub_question": question,
                    "intent": "summary",
                }],
            }
        return self._safe_parse_json(raw)

    def _generate_section(
        self,
        *,
        user_id: uuid.UUID,
        session_id: uuid.UUID,
        plan: dict[str, Any],
        df: pd.DataFrame,
        profile: DatasetProfile,
        user_context: str,
        conversation_history: list[dict[str, str]],
        debug: bool,
    ) -> ReportSection:
        section_start = time.perf_counter()
        sub_question = plan.get("sub_question", plan.get("title", "Overview"))
        section_title = plan.get("title", "Section")
        section_intent = plan.get("intent", "summary")

        from app.Back_End.prompts.data_analysis.nlu.column_resolver import resolve_columns
        from app.Back_End.prompts.data_analysis.nlu.entity_extractor import extract_entities
        from app.Back_End.prompts.data_analysis.nlu.intent_detector import detect_intents
        from app.Back_End.prompts.data_analysis.code_generation import build_code_generation_prompt
        from app.Back_End.prompts.data_analysis.code_retry import build_code_retry_prompt
        from app.Back_End.prompts.data_analysis.system_prompts import SYSTEM_PROMPT
        from app.Back_End.prompts.data_analysis.insight_generation import build_insight_generation_prompt
        from execution.executor import execute_code
        from app.Back_End.services.data_analysis.analyst_agent import _compute_table_statistics

        intent_values = detect_intents(sub_question)
        intents = [Intent(value=v) for v in intent_values]
        entities: ExtractedEntities = extract_entities(sub_question, profile)
        resolved_columns = resolve_columns(entities, list(df.columns))

        code_prompt = build_code_generation_prompt(
            profile=profile,
            question=sub_question,
            intents=intents,
            entities=entities,
            resolved_columns=resolved_columns,
            conversation_history=conversation_history,
            user_context=user_context,
        )

        insight_text: str | None = None
        generated_code: str | None = None
        result: AnalysisResult | None = None

        try:
            raw_code = self.llm_client.chat(
                user_prompt=code_prompt,
                system_prompt=SYSTEM_PROMPT,
                model=settings.llm_model,
            )
            generated_code = raw_code

            outcome = execute_code(raw_code, df)

            # Self-healing retries — same pattern as AnalystAgent.
            retry_count = 0
            max_retries = settings.code_retry_max_attempts
            while not outcome.success and retry_count < max_retries:
                retry_count += 1
                logger.info(
                    "Section %s: code failed (attempt %d/%d). Asking LLM to fix...",
                    section_title, retry_count, max_retries,
                )
                try:
                    retry_prompt = build_code_retry_prompt(
                        question=sub_question,
                        previous_code=raw_code,
                        error=outcome.error or "unknown error",
                    )
                    raw_code = self.llm_client.chat(
                        user_prompt=retry_prompt,
                        system_prompt=SYSTEM_PROMPT,
                        model=settings.llm_model,
                    )
                    generated_code = raw_code
                    outcome = execute_code(raw_code, df)
                except LLMError as exc:
                    logger.warning("Retry LLM call failed: %s", exc)
                    break

            if outcome.success and outcome.result is not None:
                result = outcome.result

                execution_output = self._render_execution_output(result)
                if execution_output:
                    insight_prompt = build_insight_generation_prompt(
                        sub_question, execution_output, intents,
                    )
                    try:
                        insight_text = self.llm_client.chat(
                            user_prompt=insight_prompt, model=settings.llm_model,
                        ).strip()
                    except LLMError as exc:
                        logger.warning("Section insight generation failed: %s", exc)
                        insight_text = None
        except LLMError as exc:
            logger.warning("Section %s code generation failed: %s", section_title, exc)

        section_summary = self._generate_section_summary(
            section_title=section_title,
            section_intent=section_intent,
            sub_question=sub_question,
            result=result,
            insight_text=insight_text,
        )

        charts: list[ChartData] = []
        if result is not None:
            if result.figures:
                charts = result.figures
            elif result.figure is not None:
                charts = [result.figure]

        return ReportSection(
            title=section_title,
            intent=section_intent,
            content=section_summary,
            summary=result.summary if result else None,
            table=result.table if result else None,
            charts=charts,
            generated_code=generated_code,
            execution_time_seconds=time.perf_counter() - section_start,
        )

    def _generate_section_summary(
        self,
        *,
        section_title: str,
        section_intent: str,
        sub_question: str,
        result: AnalysisResult | None,
        insight_text: str | None,
    ) -> str:
        if result is None:
            return f"Analysis for this section could not be completed."

        execution_output = self._render_execution_output(result)
        if not execution_output:
            return result.summary or "No data was produced for this section."

        prompt = build_section_summary_prompt(
            section_title=section_title,
            section_intent=section_intent,
            sub_question=sub_question,
            execution_output=execution_output,
            insight_text=insight_text or "",
        )

        try:
            return self.llm_client.chat(
                user_prompt=prompt, model=settings.llm_model,
            ).strip()
        except LLMError as exc:
            logger.warning("Section summary generation failed: %s", exc)
            return insight_text or result.summary or "Section summary unavailable."

    def _assemble_report(
        self,
        *,
        report_title: str,
        question: str,
        sections: list[ReportSection],
    ) -> tuple[str | None, str | None]:
        summaries_block = "\n\n".join(
            f"## {s.title}\n{s.content}" for s in sections
        )

        prompt = build_report_assembly_prompt(
            report_title=report_title,
            question=question,
            section_summaries=summaries_block,
        )

        try:
            raw = self.llm_client.chat(
                user_prompt=prompt, model=settings.llm_model,
            )
        except LLMError as exc:
            logger.warning("Report assembly failed: %s", exc)
            return None, None

        data = self._safe_parse_json(raw)
        return (
            data.get("executive_summary"),
            data.get("recommendations"),
        )

    @staticmethod
    def _render_execution_output(result: AnalysisResult) -> str:
        lines: list[str] = []

        if result.table:
            stats_block = _compute_table_statistics(result.table)
            if stats_block:
                lines.append(stats_block)
            preview = result.table[:10]
            lines.append(f"Raw row sample ({len(result.table)} total rows): {preview}")

        if result.kpis:
            kpi_str = ", ".join(f"{k}={v}" for k, v in result.kpis.items())
            lines.append(f"KPIs: {kpi_str}")

        if result.summary:
            lines.append(f"Code-generated summary: {result.summary}")

        if result.figures:
            chart_types = [c.type for c in result.figures]
            lines.append(f"Charts generated: {len(result.figures)} ({', '.join(chart_types)})")
        elif result.figure:
            lines.append(f"A {result.figure.type} chart was also generated.")

        return "\n".join(lines) if lines else ""

    @staticmethod
    def _build_section_history(
        original_question: str,
        completed_sections: list[ReportSection],
    ) -> list[dict[str, str]]:
        history: list[dict[str, str]] = [
            {"role": "user", "content": original_question},
        ]
        for s in completed_sections:
            history.append({"role": "assistant", "content": f"[{s.title}] {s.content}"})
        return history

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
        report_title: str,
        error: str,
    ) -> ReportResponse:
        assistant_message = self._persist_message(
            session_id=session_id,
            role="assistant",
            content=f"(report generation failed: {error})",
            meta={"kind": "report", "success": False, "error": error},
            processing_time_seconds=elapsed,
        )
        return ReportResponse(
            success=False,
            session_id=session_id,
            message_id=assistant_message.id,
            title=report_title,
            executive_summary=None,
            sections=[],
            recommendations=None,
            total_execution_time=elapsed,
            errors=error,
        )

    @staticmethod
    def _safe_parse_json(raw: str) -> dict[str, Any]:
        if not raw or not raw.strip():
            return {}

        text = raw.strip()
        if text.startswith("```"):
            lines = text.splitlines()
            if len(lines) >= 2:
                text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            logger.warning("Failed to parse LLM JSON response: %s", exc)
            return {}

        return data if isinstance(data, dict) else {}