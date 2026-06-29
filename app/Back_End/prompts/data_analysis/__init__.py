"""prompts/ — prompt builders + deterministic NLU pipeline.

Two sub-concerns live here:

1. Prompt templates (system_prompts.py, code_generation.py,
   insight_generation.py) — render already-computed structures into
   text for the LLM. No NLU logic, no HTTP, no DB.

2. The NLU pipeline (nlu/) — deterministic, dataset-aware intent
   detection, entity extraction, and column resolution. Adds zero
   extra LLM calls; feeds the code-generation prompt.
"""

from __future__ import annotations
