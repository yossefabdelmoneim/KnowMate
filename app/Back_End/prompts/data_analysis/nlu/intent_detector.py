"""Deterministic intent classifier — no LLM call involved.

Lifted from the standalone KnowMate intent_detector.py with no logic
changes — only the import path of `normalize_text` moved to
core.text_utils.

Three layers are applied, in order, and their results merged:
1. Keyword matching   — direct phrase lookup against the normalized question.
2. Regex matching     — structural patterns (numeric comparisons, "top N",
                        "monthly/yearly", etc.) that keyword lookup alone
                        can't express cleanly.
3. Heuristic rules    — co-occurrence reasoning that looks at *combinations*
                        of signals already found, rather than single
                        keywords/patterns.

A single question can — and very often does — map to multiple intents at
once. detect_intents() always returns at least one intent (SUMMARY as a
fallback when nothing else matches), so prompts.py always has something
to anchor on.
"""

from __future__ import annotations

import logging
import re

from KnowMate.app.Back_End.core.data_analysis.text_utils import normalize_text

logger = logging.getLogger(__name__)


# All supported intent values — must stay in sync with
# schemas/message.py's Intent Literal.
INTENT_VALUES: tuple[str, ...] = (
    "summary", "aggregation", "filtering", "sorting", "comparison",
    "visualization", "correlation", "statistics", "distribution",
    "trend_analysis", "outlier_detection", "report",
)


_KEYWORD_RULES: dict[str, tuple[str, ...]] = {
    "summary": (
        "summary", "summarize", "overview", "describe", "description",
        "explore", "general info", "tell me about",
    ),
    "aggregation": (
        "average", "sum", "total", "count", "mean", "group by", "per",
        "aggregate",
    ),
    "filtering": (
        "where", "filter", "only", "exclude", "excluding", "equal to",
        "equals",
    ),
    "sorting": (
        "sort", "sorted", "rank", "ranked", "ranking", "order by",
        "highest", "lowest", "ascending", "descending", "top", "bottom",
    ),
    "comparison": (
        "compare", "comparison", "versus", "vs", "difference",
        "differences",
    ),
    "visualization": (
        "chart", "plot", "graph", "visual", "bar chart", "pie chart",
        "line chart", "scatter plot", "histogram",
    ),
    "correlation": (
        "correlation", "correlate", "correlated", "relationship",
    ),
    "statistics": (
        "statistics", "stats", "standard deviation", "variance",
        "median", "quartile", "percentile",
    ),
    "distribution": (
        "distribution", "histogram", "spread", "frequency",
    ),
    "trend_analysis": (
        "trend", "trends", "time series", "growth", "monthly", "yearly",
        "quarterly", "weekly", "daily",
    ),
    "outlier_detection": (
        "outlier", "outliers", "anomaly", "anomalies", "unusual",
        "abnormal",
    ),
    "report": (
        "report", "full report", "detailed report", "comprehensive",
        "deep dive", "in-depth", "executive summary", "briefing",
        "analysis report", "study", "white paper", "dashboard",
    ),
}


def _match_keywords(text: str) -> set[str]:
    matched: set[str] = set()
    for intent, phrases in _KEYWORD_RULES.items():
        for phrase in phrases:
            if re.search(rf"\b{re.escape(phrase)}\b", text):
                matched.add(intent)
                break
    return matched


_REGEX_RULES: dict[str, tuple[re.Pattern, ...]] = {
    "filtering": (
        re.compile(r"[<>]=?\s*\d+"),
        re.compile(r"\b(greater than|less than|more than|at least|at most)\b"),
    ),
    "sorting": (
        re.compile(r"\btop\s*\d+\b"),
        re.compile(r"\bbottom\s*\d+\b"),
        re.compile(r"\brank(ed|ing)?\b"),
    ),
    "trend_analysis": (
        re.compile(r"\b(year|month|quarter)\s*over\s*(year|month|quarter)\b"),
    ),
    "report": (
        re.compile(r"\bgenerate\s+(a|an|the)?\s*(full|comprehensive|detailed)?\s*report\b"),
        re.compile(r"\bwrite\s+(a|an|the)?\s*report\b"),
        re.compile(r"\bcreate\s+(a|an|the)?\s*report\b"),
    ),
}


def _match_regex(text: str) -> set[str]:
    matched: set[str] = set()
    for intent, patterns in _REGEX_RULES.items():
        for pattern in patterns:
            if pattern.search(text):
                matched.add(intent)
                break
    return matched


def _apply_heuristic_rules(text: str, matched: set[str]) -> set[str]:
    result = set(matched)

    # H1: ranking language + grouping marker => aggregation implied.
    if "sorting" in result and "aggregation" not in result:
        if re.search(r"\b(by|per|each)\b", text):
            result.add("aggregation")

    # H2: "between X and Y" => comparison implied.
    if "comparison" not in result and re.search(r"\bbetween\b.+\band\b", text):
        result.add("comparison")

    # H3: fallback to summary.
    if not result:
        result.add("summary")

    # H4: report intent is sticky — if detected, we don't auto-add
    # "summary" because the report flow handles its own structure.
    # No action needed; just documenting the behavior.

    return result


def detect_intents(question: str) -> list[str]:
    """Detect all applicable analysis intents for a user's question.

    Always returns at least one intent. Order is fixed (matches
    INTENT_VALUES declaration order), so output is stable across calls.
    """
    normalized = normalize_text(question)
    matched = _match_keywords(normalized)
    matched |= _match_regex(normalized)
    matched = _apply_heuristic_rules(normalized, matched)
    ordered = [v for v in INTENT_VALUES if v in matched]
    logger.debug("Detected intents for question %r -> %s", question, ordered)
    return ordered
