"""Deterministic, dataset-aware entity extraction — no LLM call involved.

Lifted from the standalone KnowMate entity_extractor.py with import
paths adjusted (normalize_text now lives in core.text_utils; the
Pydantic models it constructs live in schemas/message.py).

"Dataset-aware" means this module is given the DatasetProfile (not just
the raw question) so it can:
  - recognize literal mentions of real column names directly
  - recognize literal mentions of real category VALUES (top_values)

For terms that do NOT literally match a real column, this module
captures the raw term as a metric/dimension candidate — column_resolver
does the fuzzy matching later.
"""

from __future__ import annotations

import logging
import re

from KnowMate.app.Back_End.core.data_analysis.text_utils import dedup_preserve_order, normalize_text
from schemas.data_analysis.message import DatasetProfile, ExtractedEntities, FilterCondition

logger = logging.getLogger(__name__)


def _already_known(term: str, *lists: list[str]) -> bool:
    term_key = term.strip().lower()
    return any(term_key == existing.strip().lower() for lst in lists for existing in lst)


# --- Dataset-aware column mention matching --------------------------------

def _build_column_lookup(column_names: list[str]) -> dict[str, str]:
    lookup: dict[str, str] = {}
    for name in column_names:
        key = re.sub(r"[_\-]+", " ", name.strip().lower())
        key = re.sub(r"\s+", " ", key).strip()
        if key:
            lookup[key] = name
    return lookup


def _find_column_mentions(text: str, lookup: dict[str, str]) -> list[str]:
    found: list[str] = []
    for normalized_name, actual_name in lookup.items():
        if re.search(rf"\b{re.escape(normalized_name)}\b", text):
            found.append(actual_name)
    return found


def _find_category_mentions(text: str, profile: DatasetProfile) -> list[str]:
    found: list[str] = []
    for column in profile.columns:
        if column.categorical_stats is None:
            continue
        for original_value in column.categorical_stats.top_values:
            search_form = re.sub(r"[^\w\s]", " ", original_value.lower())
            search_form = re.sub(r"\s+", " ", search_form).strip()
            if search_form and re.search(rf"\b{re.escape(search_form)}\b", text):
                found.append(original_value)
    return found


# --- Aggregation + candidate metric/dimension phrase capture --------------

_AGGREGATION_KEYWORDS: dict[str, str] = {
    "average": "average", "avg": "average", "mean": "average",
    "sum": "sum", "total": "sum",
    "count": "count", "number": "count",
    "min": "min", "minimum": "min",
    "max": "max", "maximum": "max",
    "median": "median",
}

_BOUNDARY_WORDS = {
    "by", "per", "where", "and", "or", "top", "bottom", "sorted", "sort",
    "chart", "group", "grouped", "for", "in", "of", "is", "the", "a",
    "an", "with", "from", "to", "between", "greater", "less", "than",
    "over", "above", "below", "compare", "comparison", "vs", "versus",
}

_GROUPING_TRIGGERS = {"by", "per"}


def _capture_phrase(tokens: list[str], start_idx: int, max_words: int = 3) -> str:
    words: list[str] = []
    for token in tokens[start_idx:start_idx + max_words]:
        if token in _BOUNDARY_WORDS:
            break
        words.append(token)
    return " ".join(words)


def _extract_aggregations_and_candidates(
    tokens: list[str],
) -> tuple[list[str], list[str], list[str]]:
    aggregations: list[str] = []
    metric_candidates: list[str] = []
    dimension_candidates: list[str] = []

    for idx, token in enumerate(tokens):
        if token in _AGGREGATION_KEYWORDS:
            aggregations.append(_AGGREGATION_KEYWORDS[token])
            start = idx + 1
            if start < len(tokens) and tokens[start] == "of":
                start += 1
            phrase = _capture_phrase(tokens, start)
            if phrase:
                metric_candidates.append(phrase)

        elif token in _GROUPING_TRIGGERS:
            phrase = _capture_phrase(tokens, idx + 1)
            if phrase:
                dimension_candidates.append(phrase)

    return aggregations, metric_candidates, dimension_candidates


# --- top_n / bottom_n -----------------------------------------------------

_TOP_N_PATTERN = re.compile(r"\btop\s*(\d+)\b")
_BOTTOM_N_PATTERN = re.compile(r"\bbottom\s*(\d+)\b")


def _extract_top_bottom_n(text: str) -> tuple[int | None, int | None]:
    top_match = _TOP_N_PATTERN.search(text)
    bottom_match = _BOTTOM_N_PATTERN.search(text)
    return (
        int(top_match.group(1)) if top_match else None,
        int(bottom_match.group(1)) if bottom_match else None,
    )


# --- Chart type -----------------------------------------------------------

_CHART_TYPE_PATTERNS: dict[str, re.Pattern] = {
    "bar": re.compile(r"\bbar\s*chart\b"),
    "line": re.compile(r"\bline\s*chart\b"),
    "pie": re.compile(r"\bpie\s*chart\b"),
    "scatter": re.compile(r"\bscatter\s*chart\b"),
    "histogram": re.compile(r"\bhistogram\b"),
}


def _extract_chart_type(text: str) -> str | None:
    for chart_type, pattern in _CHART_TYPE_PATTERNS.items():
        if pattern.search(text):
            return chart_type
    return None


# --- Dates ----------------------------------------------------------------

_DATE_PATTERNS: tuple[re.Pattern, ...] = (
    re.compile(r"\b\d{4}-\d{2}-\d{2}\b"),
    re.compile(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b"),
    re.compile(
        r"\b(january|february|march|april|may|june|july|august|"
        r"september|october|november|december)\b(?:\s+\d{1,4})?,?\s*\d{0,4}"
    ),
    re.compile(r"\b(19|20)\d{2}\b"),
    re.compile(
        r"\blast\s+\d+\s+days\b|\blast\s+(week|month|quarter|year)\b|"
        r"\bthis\s+(week|month|quarter|year)\b|\byear\s+to\s+date\b|\bytd\b"
    ),
)


def _extract_dates(raw_question: str) -> list[str]:
    lowered = raw_question.lower()
    found: list[str] = []
    for pattern in _DATE_PATTERNS:
        for match in pattern.finditer(lowered):
            found.append(match.group(0).strip())
    return found


# --- Filters --------------------------------------------------------------

_LEADING_STOPWORDS = {"the", "a", "an", "is", "where", "for", "that", "which", "with"}


def _clean_filter_phrase(text: str) -> str:
    text = re.sub(r"[^\w\s.\-]", "", text).strip()
    words = text.split()
    while words and words[0] in _LEADING_STOPWORDS:
        words.pop(0)
    return " ".join(words).strip()


_CONTAINS_PATTERN = re.compile(r"([a-z_][a-z0-9_ ]{0,30}?)\s+contains\s+([a-z0-9_ ]{1,30}?)(?=[\s.,?!]|$)")
_NOT_EQUAL_PATTERN = re.compile(r"([a-z_][a-z0-9_ ]{0,30}?)\s+(?:is not|not equal to|!=)\s+([a-z0-9_ ]{1,30}?)(?=[\s.,?!]|$)")
_EQUAL_PATTERN = re.compile(r"([a-z_][a-z0-9_ ]{0,30}?)\s+(?:is|equals|equal to|==)\s+(?!not\b)([a-z0-9_ ]{1,30}?)(?=[\s.,?!]|$)")
_WORD_COMPARISON_PATTERN = re.compile(
    r"([a-z_][a-z0-9_ ]{0,30}?)\s+(greater than|more than|above|at least|less than|below|at most)\s+(-?\d+(?:\.\d+)?)"
)
_SYMBOL_COMPARISON_PATTERN = re.compile(r"([a-z_][a-z0-9_ ]{0,30}?)\s*(>=|<=|>|<)\s*(-?\d+(?:\.\d+)?)")

_WORD_OPERATOR_MAP = {
    "greater than": ">", "more than": ">", "above": ">",
    "at least": ">=",
    "less than": "<", "below": "<",
    "at most": "<=",
}


def _extract_filters(raw_question: str) -> list[FilterCondition]:
    text = raw_question.lower()
    filters: list[FilterCondition] = []

    if match := _CONTAINS_PATTERN.search(text):
        column = _clean_filter_phrase(match.group(1))
        value = _clean_filter_phrase(match.group(2))
        if column and value:
            filters.append(FilterCondition(column=column, operator="contains", value=value))

    if match := _NOT_EQUAL_PATTERN.search(text):
        column = _clean_filter_phrase(match.group(1))
        value = _clean_filter_phrase(match.group(2))
        if column and value:
            filters.append(FilterCondition(column=column, operator="!=", value=value))

    if match := _EQUAL_PATTERN.search(text):
        column = _clean_filter_phrase(match.group(1))
        value = _clean_filter_phrase(match.group(2))
        if column and value:
            filters.append(FilterCondition(column=column, operator="==", value=value))

    if match := _WORD_COMPARISON_PATTERN.search(text):
        column = _clean_filter_phrase(match.group(1))
        operator = _WORD_OPERATOR_MAP[match.group(2)]
        value = match.group(3).strip()
        if column:
            filters.append(FilterCondition(column=column, operator=operator, value=value))

    if match := _SYMBOL_COMPARISON_PATTERN.search(text):
        column = _clean_filter_phrase(match.group(1))
        operator = match.group(2).strip()
        value = match.group(3).strip()
        if column and operator in (">", ">=", "<", "<="):
            filters.append(FilterCondition(column=column, operator=operator, value=value))

    return filters


# --- Public entry point ---------------------------------------------------

def extract_entities(question: str, profile: DatasetProfile) -> ExtractedEntities:
    """Extract structured entities from a user's question."""
    normalized = normalize_text(question)
    tokens = normalized.split()

    numeric_lookup = _build_column_lookup(profile.numeric_columns)
    categorical_lookup = _build_column_lookup(profile.categorical_columns)

    literal_metrics = _find_column_mentions(normalized, numeric_lookup)
    literal_dimensions = _find_column_mentions(normalized, categorical_lookup)

    aggregations, metric_candidates, dimension_candidates = _extract_aggregations_and_candidates(tokens)

    metrics = list(literal_metrics)
    for candidate in metric_candidates:
        if not _already_known(candidate, metrics, literal_dimensions):
            metrics.append(candidate)

    dimensions = list(literal_dimensions)
    for candidate in dimension_candidates:
        if not _already_known(candidate, dimensions, metrics):
            dimensions.append(candidate)

    top_n, bottom_n = _extract_top_bottom_n(normalized)
    chart_type = _extract_chart_type(normalized)
    categories = _find_category_mentions(normalized, profile)
    dates = _extract_dates(question)
    filters = _extract_filters(question)

    entities = ExtractedEntities(
        metrics=dedup_preserve_order(metrics),
        dimensions=dedup_preserve_order(dimensions),
        filters=filters,
        dates=dedup_preserve_order(dates),
        top_n=top_n,
        bottom_n=bottom_n,
        aggregations=dedup_preserve_order(aggregations),
        chart_type=chart_type,
        categories=dedup_preserve_order(categories),
    )

    logger.debug("Extracted entities for question %r -> %s", question, entities.model_dump())
    return entities
