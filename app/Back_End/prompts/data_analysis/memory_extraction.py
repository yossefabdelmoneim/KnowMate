"""Memory extraction prompts — used by MemoryService after each analysis.

Two separate prompts:

1. PREFERENCE_EXTRACTION_PROMPT — scans a Q&A pair for explicit user
   preferences ("I prefer bar charts", "always show values in EGP",
   "I work in retail"). Returns a JSON list of {category, key, value}
   triples. Conservative by design — only extracts explicit statements,
   never infers.

2. FACT_EXTRACTION_PROMPT — scans a Q&A pair for durable facts worth
   remembering across chats ("user asked about Q3 sales", "user
   struggled with correlation concept"). Returns a JSON list of
   {kind, content, importance} triples.

Both prompts expect strict JSON output (no prose, no markdown fences)
so the service layer can `json.loads()` the response directly. If the
LLM returns malformed JSON or refuses, the service logs a warning and
skips — extraction failures NEVER break the main analysis flow.
"""

from __future__ import annotations


PREFERENCE_EXTRACTION_PROMPT = """You are a preference extractor. Your job is to scan a single user-assistant conversation turn from a data-analysis chat and identify EXPLICIT user preferences — things the user said they want, like, or always want done a certain way.

CONVERSATION TURN:
- User question: {question}
- Agent response summary: {response_summary}

Extract preferences ONLY when the user EXPLICITLY stated one. Do NOT infer preferences from the type of question (e.g. asking for a bar chart once does not mean they "prefer" bar charts — they would need to say something like "I always want bar charts" or "please use bar charts from now on").

Categories (use these exact category strings):
- "formatting"  — chart type preference, number formatting (currency, decimals), date format
- "language"    — response language, technical level (e.g. "explain simply")
- "domain"      — industry, role, use case (e.g. "I work in retail")
- "ui"          — UI prefs (dark mode, table vs chart default)

Output ONLY a JSON object with this exact shape (no markdown fences, no prose):
{{
  "preferences": [
    {{"category": "formatting", "key": "chart_type", "value": "bar", "confidence": 0.9}},
    ...
  ]
}}

Confidence guidance:
- 0.9+ for explicit "always" / "from now on" / "I prefer" statements
- 0.7 for clear but less emphatic statements ("please use X")
- 0.5 for inferred-but-reasonable preferences
- Below 0.5: do not include

If no preferences are extractable, return: {{"preferences": []}}
"""


FACT_EXTRACTION_PROMPT = """You are a memory extractor. Your job is to scan a single user-assistant conversation turn from a data-analysis chat and identify DURABLE FACTS worth remembering across chats — things that would help future conversations with this same user be more useful.

CONVERSATION TURN:
- User question: {question}
- Agent response summary: {response_summary}

Extract facts ONLY when they are genuinely durable (would still be relevant in a future chat). Examples of good facts:
- "User is analyzing e-commerce sales data from Egypt" → kind: "context"
- "User asked about outlier detection — may need simpler explanations of statistical concepts" → kind: "skill_gap"
- "User's primary metric of interest is revenue" → kind: "topic_of_interest"
- "User cares about Q3 performance specifically" → kind: "topic_of_interest"

Do NOT extract:
- One-off questions that won't matter tomorrow
- Facts about the dataset itself (those belong to the dataset profile)
- Anything the user didn't actually engage with

Kinds (use these exact strings):
- "context"            — background context about the user / their data
- "topic_of_interest"  — what they care about
- "skill_gap"          — concepts they may need explained more simply
- "summary"            — a 1-sentence summary of what this chat was about

Output ONLY a JSON object (no markdown fences, no prose):
{{
  "facts": [
    {{"kind": "context", "content": "User is analyzing Egyptian e-commerce data", "importance": 0.7}},
    ...
  ]
}}

Importance guidance:
- 0.9+ for facts that will matter in almost every future chat (e.g. user's role/industry)
- 0.7 for facts that matter for several future chats
- 0.5 for facts that may matter occasionally
- Below 0.5: do not include

If no facts are extractable, return: {{"facts": []}}
"""


def build_preference_extraction_prompt(question: str, response_summary: str) -> str:
    """Build the user-message prompt for preference extraction."""
    return PREFERENCE_EXTRACTION_PROMPT.format(
        question=question,
        response_summary=response_summary,
    )


def build_fact_extraction_prompt(question: str, response_summary: str) -> str:
    """Build the user-message prompt for fact extraction."""
    return FACT_EXTRACTION_PROMPT.format(
        question=question,
        response_summary=response_summary,
    )


__all__ = [
    "build_preference_extraction_prompt",
    "build_fact_extraction_prompt",
]
