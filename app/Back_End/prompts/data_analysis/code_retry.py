"""Code-retry prompt builder.

Used when the first code-generation attempt fails during execution.
Takes the failing code and the error message, and asks the LLM to fix it.
"""

from __future__ import annotations


CODE_RETRY_PROMPT = """The following Python code was generated to answer a user question,
but it failed during execution. Fix the code so it runs correctly.

User question:
{question}

Previous code (FAILED):
```python
{previous_code}
```

Error:
{error}

Instructions:
- Fix the error while keeping the original intent.
- Output ONLY a single Python code block. No explanation before or after.
- Assign your output to a dict named `result`.
- Follow all the same rules as the original code generation prompt.
"""


def build_code_retry_prompt(
    *,
    question: str,
    previous_code: str,
    error: str,
) -> str:
    """Build the user-message prompt for a code-retry LLM call."""
    return CODE_RETRY_PROMPT.format(
        question=question,
        previous_code=previous_code,
        error=error,
    )


__all__ = ["build_code_retry_prompt"]
