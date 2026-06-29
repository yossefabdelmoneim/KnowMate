"""Small text utilities shared by the NLU pipeline.

Lifted verbatim from the standalone KnowMate utils.py and renamed to
avoid clashing with Python's own `utils` packages. The NLU modules in
prompts/nlu/ import from here — keeping the normalization logic in one
place means intent_detector.py and entity_extractor.py work against
the same canonical representation of the user's question.
"""

from __future__ import annotations

import re

# Maps loose, conversational phrasing to a single canonical term per
# concept. Multi-word phrases are listed BEFORE their single-word
# equivalents so longer matches are not pre-empted by a shorter
# substring replacing part of them first (dict iteration order matters
# here — Python dicts preserve insertion order).
SYNONYM_MAP: dict[str, str] = {
    # aggregation phrasing -> canonical aggregation term
    "on average": "average",
    "avg": "average",
    "mean": "average",
    "total of": "sum",
    "sum of": "sum",
    "number of": "count",
    "count of": "count",
    # ranking / top-n phrasing -> canonical ranking term
    "biggest": "highest",
    "largest": "highest",
    "greatest": "highest",
    "smallest": "lowest",
    "least": "lowest",
    # visualization phrasing -> canonical "chart" term
    "graph": "chart",
    "plot": "chart",
    "visualize": "chart",
    "visualise": "chart",
    "visualization": "chart",
    # trend phrasing -> canonical "trend" term
    "over time": "trend",
    "trending": "trend",
    "trends": "trend",
    # correlation phrasing -> canonical "correlation" term
    "relationship between": "correlation",
    "related to": "correlation",
    "correlated with": "correlation",
    # outlier phrasing -> canonical "outlier" term
    "anomalies": "outlier",
    "anomaly": "outlier",
    "unusual values": "outlier",
}

# Matches any character that isn't a word character or whitespace.
# Replaced with a space (not removed entirely) so adjacent tokens
# don't accidentally merge — e.g. "top-5" becomes "top 5", not "top5".
_PUNCTUATION_RE = re.compile(r"[^\w\s]")
_WHITESPACE_RE = re.compile(r"\s+")


def normalize_text(text: str) -> str:
    """Lowercase, apply synonym normalization, strip punctuation, collapse whitespace.

    Applied BEFORE keyword/regex matching in intent_detector.py and
    entity_extractor.py. Those modules extract things like dates and
    explicit column-name mentions from the ORIGINAL question text, not
    this normalized version — so nothing here should be treated as the
    only representation of the question downstream.
    """
    normalized = text.lower().strip()

    for phrase, canonical in SYNONYM_MAP.items():
        normalized = normalized.replace(phrase, canonical)

    normalized = _PUNCTUATION_RE.sub(" ", normalized)
    normalized = _WHITESPACE_RE.sub(" ", normalized).strip()

    return normalized


def dedup_preserve_order(items: list[str]) -> list[str]:
    """Case-insensitive dedup that keeps the first-seen original casing/order."""
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        cleaned = item.strip()
        key = cleaned.lower()
        if cleaned and key not in seen:
            seen.add(key)
            result.append(cleaned)
    return result
