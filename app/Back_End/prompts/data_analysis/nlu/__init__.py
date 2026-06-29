"""prompts/nlu/ — deterministic NLU pipeline.

Three modules, each with one job:
- intent_detector.py  — keyword + regex + heuristic classification
- entity_extractor.py — dataset-aware entity extraction
- column_resolver.py  — fuzzy column-name resolution (RapidFuzz)

All three are deterministic (no LLM calls) and run on every request.
The combined output is fed to the code-generation prompt.
"""

from __future__ import annotations
