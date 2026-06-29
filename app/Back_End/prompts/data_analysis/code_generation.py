"""Code-generation prompt builder.

Renders a DatasetProfile + NLU pipeline output + the user's question
into the user-message prompt sent to the LLM alongside SYSTEM_PROMPT.

V3 change vs standalone KnowMate: now also renders an optional
"conversation so far" section so the LLM can resolve references in
follow-up questions ("now sort that descending").
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from prompts.data_analysis.system_prompts import SYSTEM_PROMPT

if TYPE_CHECKING:
    from schemas.data_analysis.message import (
        ColumnResolution, DatasetProfile, ExtractedEntities, Intent,
    )


# --- Dataset profile rendering ---------------------------------------------

def _format_dataset_profile(profile: DatasetProfile) -> str:
    """Render a DatasetProfile into a compact, LLM-readable text block."""
    lines: list[str] = [
        f"Rows: {profile.row_count}",
        f"Columns: {profile.column_count}",
        "",
        "Column details:",
    ]

    for column in profile.columns:
        line = (
            f"- {column.name} (dtype: {column.dtype}, "
            f"nulls: {column.null_count}, unique: {column.unique_count})"
        )

        if column.numeric_stats is not None:
            stats = column.numeric_stats
            line += (
                f"\n    stats: mean={stats.mean}, std={stats.std}, "
                f"min={stats.min}, q25={stats.q25}, median={stats.median}, "
                f"q75={stats.q75}, max={stats.max}"
            )
        elif column.categorical_stats is not None:
            top_values = column.categorical_stats.top_values
            formatted_values = ", ".join(
                f"{value!r}: {count}" for value, count in top_values.items()
            )
            line += f"\n    top values: {formatted_values}"

        lines.append(line)

    lines.append("")
    lines.append(f"Numeric columns: {', '.join(profile.numeric_columns) or 'none'}")
    lines.append(f"Categorical columns: {', '.join(profile.categorical_columns) or 'none'}")

    return "\n".join(lines)


# --- Intent / entity / column rendering ------------------------------------

_INTENT_HINTS: dict[str, str] = {
    "summary": (
        "Use df.describe() directly for numeric columns (do not transpose it "
        "before selecting columns — its columns are already the original "
        "column names). For a categorical overview, use "
        "df[col].value_counts() per categorical column separately. Put the "
        "numeric describe() output in 'table' and mention row/column counts "
        "and any standout columns in 'summary'."
    ),
    "aggregation": "Use groupby() with the relevant aggregation function(s) (mean/sum/count/etc.).",
    "filtering": "Apply boolean indexing (df[df[...] ...]) before any further analysis.",
    "sorting": "Use sort_values(); apply head()/tail() if a top/bottom N is implied.",
    "comparison": "Compute the relevant metric for each group/value being compared and report the difference.",
    "visualization": "You must populate result['figure'] with a matplotlib or plotly figure.",
    "correlation": "Use .corr() between the relevant numeric columns, or a scatter plot; report the coefficient in 'summary'.",
    "statistics": "Use .describe() or targeted stats (std/var/median/quantile) on the relevant column(s).",
    "distribution": "Use value_counts() for categorical columns, or a histogram for numeric columns.",
    "trend_analysis": "If a date/time column exists, sort by it first, then aggregate by the relevant time period.",
    "outlier_detection": (
        "Use the IQR method on each numeric column individually: "
        "q1, q3 = df[col].quantile([0.25, 0.75]); iqr = q3 - q1; "
        "flag rows where df[col] < q1 - 1.5*iqr or df[col] > q3 + 1.5*iqr. "
        "Build a boolean mask per column with simple comparisons (no .any(axis=1) on a Series). "
        "Combine masks across columns using df[mask1 | mask2 | ...] only at the DataFrame level. "
        "List the flagged rows in 'table'."
    ),
}


def _format_intent_section(intents: list[Intent]) -> str:
    """Render detected intents + their hints into a text block."""
    lines = ["Detected intent(s):"]
    for intent in intents:
        hint = _INTENT_HINTS.get(intent.value, "")
        lines.append(f"- {intent.value}: {hint}")
    return "\n".join(lines)


def _format_entities_section(entities: ExtractedEntities) -> str:
    """Render extracted entities into a compact text block. Omits empty fields."""
    lines: list[str] = ["Extracted entities:"]

    if entities.metrics:
        lines.append(f"- metrics mentioned: {', '.join(entities.metrics)}")
    if entities.dimensions:
        lines.append(f"- dimensions/grouping terms mentioned: {', '.join(entities.dimensions)}")
    if entities.aggregations:
        lines.append(f"- aggregation function(s) implied: {', '.join(entities.aggregations)}")
    if entities.filters:
        filter_strs = [f"{f.column} {f.operator} {f.value!r}" for f in entities.filters]
        lines.append(f"- filter condition(s) implied: {', '.join(filter_strs)}")
    if entities.dates:
        lines.append(f"- date/time reference(s) mentioned: {', '.join(entities.dates)}")
    if entities.top_n is not None:
        lines.append(f"- top N implied: {entities.top_n}")
    if entities.bottom_n is not None:
        lines.append(f"- bottom N implied: {entities.bottom_n}")
    if entities.chart_type:
        lines.append(f"- chart type requested: {entities.chart_type}")
    if entities.categories:
        lines.append(f"- specific category value(s) mentioned: {', '.join(entities.categories)}")

    if len(lines) == 1:
        lines.append("- none detected")

    return "\n".join(lines)


def _format_resolved_columns_section(resolutions: list[ColumnResolution]) -> str:
    """Render column resolutions. Confident and uncertain shown separately."""
    if not resolutions:
        return "Resolved column suggestions:\n- none"

    lines = ["Resolved column suggestions:"]
    confident = [r for r in resolutions if r.resolved]
    uncertain = [r for r in resolutions if not r.resolved]

    if confident:
        for r in confident:
            lines.append(
                f"- '{r.original_term}' likely means column '{r.resolved_column}' "
                f"(confidence: {r.score})"
            )
    if uncertain:
        lines.append("- Low-confidence guesses (verify against the dataset metadata before trusting these):")
        for r in uncertain:
            best_guess = r.resolved_column or "no reasonable match"
            lines.append(
                f"  - '{r.original_term}' -> closest guess: '{best_guess}' "
                f"(confidence: {r.score}, below threshold)"
            )

    return "\n".join(lines)


# --- Conversation history rendering ----------------------------------------

def _format_conversation_history(history: list[dict[str, str]] | None) -> str:
    """Render prior chat turns as a compact transcript.

    Each entry is {"role": "user"|"assistant", "content": "..."}. Truncated
    per entry to keep prompt size bounded.
    """
    if not history:
        return ""

    max_chars_per_turn = 600
    lines: list[str] = ["Conversation so far (most recent at the end):"]
    for turn in history:
        role = turn.get("role", "user")
        content = (turn.get("content") or "").strip()
        if len(content) > max_chars_per_turn:
            content = content[:max_chars_per_turn] + " [...]"
        lines.append(f"- {role}: {content}")
    return "\n".join(lines)


# --- Prompt assembly -------------------------------------------------------

CODE_GENERATION_PROMPT = """Dataset metadata:
{dataset_profile}

{intent_section}

{entities_section}

{resolved_columns_section}

{conversation_section}

{user_context_section}

User question:
{question}

Write Python code that answers this question, following the rules from
the system prompt exactly. Remember: assign your output to a dict named
`result`. If "User context" above mentions specific preferences (e.g.
chart type, currency), apply them when relevant — but never override
an explicit instruction in the user's question.
"""


def build_code_generation_prompt(
    profile: DatasetProfile,
    question: str,
    intents: list[Intent],
    entities: ExtractedEntities,
    resolved_columns: list[ColumnResolution],
    conversation_history: list[dict[str, str]] | None = None,
    user_context: str | None = None,
) -> str:
    """Build the user-message prompt for the code-generation call.

    V3 changes vs standalone V2:
    - `conversation_history`: short-term memory (recent turns in this chat)
      so follow-up questions resolve correctly.
    - `user_context`: long-term memory (cross-chat prefs + facts) so the
      agent personalizes its output to the user.
    """
    conversation_section = _format_conversation_history(conversation_history)
    if conversation_section:
        conversation_section = "Conversation so far:\n" + conversation_section.split("\n", 1)[1] if "Conversation so far:" in conversation_section else conversation_section

    return CODE_GENERATION_PROMPT.format(
        dataset_profile=_format_dataset_profile(profile),
        intent_section=_format_intent_section(intents),
        entities_section=_format_entities_section(entities),
        resolved_columns_section=_format_resolved_columns_section(resolved_columns),
        conversation_section=conversation_section or "(no prior conversation in this chat)",
        user_context_section=user_context or "(no known user context yet)",
        question=question,
    )


__all__ = ["SYSTEM_PROMPT", "build_code_generation_prompt"]
