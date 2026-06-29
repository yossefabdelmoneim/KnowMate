"""Fuzzy column-name resolution via RapidFuzz.

Lifted from the standalone KnowMate column_resolver.py with import
path adjustments. Advisory only — a low-confidence resolution is marked
`resolved=False` and the LLM is told to verify against the dataset
metadata before trusting it.
"""

from __future__ import annotations

import logging

from rapidfuzz import fuzz, process

from schemas.data_analysis.message import ColumnResolution, ExtractedEntities

logger = logging.getLogger(__name__)

# Below this RapidFuzz score (0-100), a match is too uncertain to
# suggest as authoritative.
CONFIDENCE_THRESHOLD = 70.0

# A small, flat synonym map for common business terms that have near-
# zero string similarity to their likely real column names.
_BUSINESS_SYNONYMS: dict[str, tuple[str, ...]] = {
    "revenue": ("sales", "amount", "income", "earnings"),
    "profit": ("margin", "earnings", "net"),
    "client": ("customer",),
    "purchase": ("order", "transaction"),
    "qty": ("quantity", "count"),
    "cost": ("price", "expense"),
    "region": ("area", "location", "territory"),
    "date": ("time", "timestamp", "period"),
}


def _normalize_column_for_matching(column_name: str) -> str:
    return column_name.replace("_", " ").replace("-", " ").lower().strip()


def _best_match(term: str, normalized_columns: dict[str, str]) -> tuple[str, float] | None:
    candidates = [term.lower().strip()]
    candidates.extend(_BUSINESS_SYNONYMS.get(term.lower().strip(), ()))

    best_column: str | None = None
    best_score = -1.0

    for candidate in candidates:
        match = process.extractOne(
            candidate,
            normalized_columns.keys(),
            scorer=fuzz.WRatio,
        )
        if match is not None:
            matched_key, score, _ = match
            if score > best_score:
                best_score = score
                best_column = normalized_columns[matched_key]

    if best_column is None:
        return None
    return best_column, best_score


def _resolve_term(term: str, normalized_columns: dict[str, str]) -> ColumnResolution:
    match = _best_match(term, normalized_columns)
    if match is None:
        return ColumnResolution(original_term=term, resolved_column=None, score=0.0, resolved=False)
    resolved_column, score = match
    return ColumnResolution(
        original_term=term,
        resolved_column=resolved_column,
        score=round(score, 1),
        resolved=score >= CONFIDENCE_THRESHOLD,
    )


def resolve_columns(
    entities: ExtractedEntities,
    column_names: list[str],
) -> list[ColumnResolution]:
    """Resolve every raw term in `entities` against the real dataset columns."""
    if not column_names:
        return []

    normalized_columns = {
        _normalize_column_for_matching(name): name for name in column_names
    }

    raw_terms: list[str] = list(entities.metrics) + list(entities.dimensions)
    raw_terms.extend(condition.column for condition in entities.filters)

    seen: set[str] = set()
    resolutions: list[ColumnResolution] = []
    for term in raw_terms:
        key = term.strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        resolutions.append(_resolve_term(term, normalized_columns))

    logger.debug("Resolved columns: %s", [r.model_dump() for r in resolutions])
    return resolutions
