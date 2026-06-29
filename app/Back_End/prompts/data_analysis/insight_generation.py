"""Insight-generation prompt builder.

Used in a second, separate LLM call: takes the *output* of the executed
code (not the dataset itself) and asks for a short business-oriented
explanation. This keeps "generate correct code" and "explain the result
like an analyst would" as two separate, simpler LLM tasks rather than
asking one prompt to do both well at once.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from schemas.data_analysis.message import Intent


INSIGHT_GENERATION_PROMPT = """A user asked the following question about a dataset:
"{question}"

Detected analysis intent(s): {intent_list}

Execution output — this is your ONLY source of factual numbers. Treat
the question above as context for what was asked, NOT as a source of
data:
{execution_output}

Write a short, business-oriented explanation (3-5 sentences) of this
result, as a data analyst would explain it to a non-technical
stakeholder. Every number or claim you make MUST come from the
Execution output above — do not invent, assume, or infer numbers that
are not shown there. Where relevant:
- Call out any notable trend, comparison, or anomaly visible in the numbers above.
- State the key finding plainly, in business terms (not just "the mean is X").
- If — and only if — the result clearly warrants one, add one short,
  concrete recommendation grounded in the actual numbers above. If the
  result is too simple or inconclusive for a recommendation to make
  sense (e.g. it's just a row count or a single lookup value), do not
  force one.

Do not repeat raw numbers verbatim if a table is large — summarize the
pattern instead. Do not write any code. Output plain text only.
"""


def build_insight_generation_prompt(
    question: str,
    execution_output: str,
    intents: list[Intent],
) -> str:
    """Build the prompt for the insight-generation call."""
    intent_list = ", ".join(i.value for i in intents) if intents else "summary"
    return INSIGHT_GENERATION_PROMPT.format(
        question=question,
        intent_list=intent_list,
        execution_output=execution_output,
    )


__all__ = ["build_insight_generation_prompt"]
