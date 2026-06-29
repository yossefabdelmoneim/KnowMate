"""Report generation prompts.

Three distinct prompts used by ReportService:

1. OUTLINE_PROMPT — given the user's high-level ask + dataset profile,
   returns a JSON list of sections to generate. Each section has a
   title, a sub-question, and a primary intent.

2. SECTION_SUMMARY_PROMPT — for each generated section, takes the
   executed result + insight text and returns a 2-3 sentence section
   summary suitable for inclusion in the final report.

3. REPORT_ASSEMBLY_PROMPT — takes all section summaries + the original
   question and produces:
   - An executive summary (3-5 sentences)
   - A recommendations block (actionable, grounded in the section data)

All prompts expect strict JSON output (no markdown fences) so the
service can `json.loads()` the response directly.
"""

from __future__ import annotations


OUTLINE_PROMPT = """You are a report planning assistant. Given a high-level question and a dataset profile, your job is to break the question down into 3-{max_sections} discrete analysis sections that together would constitute a comprehensive report.

HIGH-LEVEL QUESTION:
{question}

DATASET PROFILE:
{dataset_profile}

USER CONTEXT (cross-chat memory, may be empty):
{user_context}

Rules for the outline:
- Each section should answer a SUB-QUESTION that, when answered, contributes to the high-level question.
- Sections should be MECE (mutually exclusive, collectively exhaustive) — no overlap, full coverage.
- Each section's sub-question should be answerable from the dataset's columns alone (don't ask for external data).
- Prefer sections that produce charts/tables over sections that produce only prose.
- Section titles should be short (3-6 words) and descriptive.
- Use these intent values only: "summary", "aggregation", "filtering", "sorting", "comparison", "visualization", "correlation", "statistics", "distribution", "trend_analysis", "outlier_detection".

Output ONLY a JSON object (no markdown fences, no prose):
{{
  "report_title": "<short title for the whole report>",
  "sections": [
    {{
      "title": "<short section title>",
      "sub_question": "<the specific question this section answers>",
      "intent": "<primary intent for this section>"
    }},
    ...
  ]
}}

The first section should be a high-level overview ("summary" or "statistics" intent). The last section should typically be "outlier_detection" or "trend_analysis" to surface non-obvious findings.
"""


SECTION_SUMMARY_PROMPT = """You are writing one section of a data analysis report. Take the executed analysis output below and write a concise (2-4 sentence) section summary that a non-technical stakeholder can understand.

SECTION TITLE: {section_title}
SECTION INTENT: {section_intent}
SUB-QUESTION: {sub_question}

EXECUTION OUTPUT (the only source of factual numbers):
{execution_output}

Code-generated insight (cross-check against the stats above):
{insight_text}

Rules:
- Lead with the key finding in plain business language.
- Cite 1-2 specific numbers from the execution output.
- If a chart was generated, reference what it shows ("the bar chart shows...").
- Do NOT invent numbers that aren't in the execution output.
- Do NOT use markdown headers or bullets — plain sentences only.

Output plain text only (no JSON, no markdown fences).
"""


REPORT_ASSEMBLY_PROMPT = """You are assembling the executive summary and recommendations for a data analysis report. Below are the section-by-section summaries. Your job is to synthesize them into a coherent opening + actionable closing.

REPORT TITLE: {report_title}
ORIGINAL HIGH-LEVEL QUESTION: {question}

SECTION SUMMARIES:
{section_summaries}

Write TWO blocks:

1. EXECUTIVE SUMMARY (3-5 sentences):
   - The single most important finding from the whole report.
   - 2-3 supporting findings from the sections.
   - The overall shape/pattern of the data.
   Every claim must trace back to a specific section's numbers.

2. RECOMMENDATIONS (3-5 bullets, each 1-2 sentences):
   - Each recommendation must be grounded in a specific section's finding.
   - Be concrete and actionable — not "consider investigating X" but "investigate X because Y".
   - If a section's data clearly doesn't support any recommendation, skip it — don't force one.

Output ONLY a JSON object (no markdown fences, no prose):
{{
  "executive_summary": "<3-5 sentence string>",
  "recommendations": "<bullet string with \\\\n between bullets, each starting with '• '>"
}}
"""


def build_outline_prompt(
    question: str,
    dataset_profile_text: str,
    user_context: str,
    max_sections: int,
) -> str:
    return OUTLINE_PROMPT.format(
        question=question,
        dataset_profile=dataset_profile_text,
        user_context=user_context or "(no known user context yet)",
        max_sections=max_sections,
    )


def build_section_summary_prompt(
    section_title: str,
    section_intent: str,
    sub_question: str,
    execution_output: str,
    insight_text: str,
) -> str:
    return SECTION_SUMMARY_PROMPT.format(
        section_title=section_title,
        section_intent=section_intent,
        sub_question=sub_question,
        execution_output=execution_output,
        insight_text=insight_text or "(no insight generated)",
    )


def build_report_assembly_prompt(
    report_title: str,
    question: str,
    section_summaries: str,
) -> str:
    return REPORT_ASSEMBLY_PROMPT.format(
        report_title=report_title,
        question=question,
        section_summaries=section_summaries,
    )


__all__ = [
    "build_outline_prompt",
    "build_section_summary_prompt",
    "build_report_assembly_prompt",
]
