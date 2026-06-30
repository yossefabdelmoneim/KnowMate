"""Message + analysis result schemas.

Most of these mirror models.py from the standalone KnowMate — they're
the wire representation of the agent's structured output.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field

from app.Back_End.schemas.data_analysis.common import ORMModel


# --- Dataset profile (sent to the LLM as context) ---------------------------

class NumericColumnStats(BaseModel):
    count: int
    mean: Optional[float] = None
    std: Optional[float] = None
    min: Optional[float] = None
    q25: Optional[float] = None
    median: Optional[float] = None
    q75: Optional[float] = None
    max: Optional[float] = None


class CategoricalColumnStats(BaseModel):
    top_values: dict[str, int] = Field(default_factory=dict)


class ColumnProfile(BaseModel):
    name: str
    dtype: str
    null_count: int
    unique_count: int
    numeric_stats: Optional[NumericColumnStats] = None
    categorical_stats: Optional[CategoricalColumnStats] = None


class DatasetProfile(BaseModel):
    """Full dataset metadata profile sent to the LLM as context."""

    row_count: int
    column_count: int
    columns: list[ColumnProfile]
    numeric_columns: list[str]
    categorical_columns: list[str]


# --- NLU output (V2 deterministic pipeline) ---------------------------------

class Intent(BaseModel):
    """String enum of supported intent types.

    Mirrors models.py from the standalone   Kept as a Pydantic
    BaseModel with Literal typing so the OpenAPI docs render it cleanly.
    """

    value: Literal[
        "summary", "aggregation", "filtering", "sorting", "comparison",
        "visualization", "correlation", "statistics", "distribution",
        "trend_analysis", "outlier_detection", "report",
    ]


class FilterCondition(BaseModel):
    column: str
    operator: Literal["==", "!=", ">", ">=", "<", "<=", "contains"]
    value: str


class ExtractedEntities(BaseModel):
    metrics: list[str] = Field(default_factory=list)
    dimensions: list[str] = Field(default_factory=list)
    filters: list[FilterCondition] = Field(default_factory=list)
    dates: list[str] = Field(default_factory=list)
    top_n: Optional[int] = None
    bottom_n: Optional[int] = None
    aggregations: list[str] = Field(default_factory=list)
    chart_type: Optional[str] = None
    categories: list[str] = Field(default_factory=list)


class ColumnResolution(BaseModel):
    original_term: str
    resolved_column: Optional[str] = None
    score: float
    resolved: bool


# --- Execution result -------------------------------------------------------

class ChartData(BaseModel):
    type: Literal["image", "plotly"]
    data: str  # base64 PNG (image) or JSON string (plotly)


class AnalysisResult(BaseModel):
    """Structured shape of the `result` dict produced by generated code.

    V3 changes:
    - Added `figures: Optional[list[ChartData]]` to support MULTIPLE
      charts per response. `figure` is kept for backwards compat —
      it's the first chart from `figures` (or None if no charts).
    """

    summary: Optional[str] = None
    insights: Optional[str] = None
    table: Optional[list[dict[str, Any]]] = None
    figure: Optional[ChartData] = None          # backwards-compat: first chart
    figures: Optional[list[ChartData]] = None    # full list of charts
    kpis: Optional[dict[str, Any]] = None


# --- Message request / response --------------------------------------------

class MessageCreateRequest(BaseModel):
    """Send a new user message to a session."""

    question: str = Field(min_length=1, max_length=4000)
    debug: bool = False


class ReportCreateRequest(BaseModel):
    """Request generation of a full multi-section report.

    `question` is the high-level ask (e.g. "generate a comprehensive
    report on sales performance"). `max_sections` caps how many sections
    the orchestrator will generate (each section = 1 LLM call + 1 code
    execution + 1 insight call, so this scales cost linearly).
    """

    question: str = Field(min_length=1, max_length=4000)
    max_sections: int = Field(default=5, ge=2, le=10)
    debug: bool = False


class MessagePublic(ORMModel):
    """One row from the messages table, as returned by the chat history endpoint."""

    id: uuid.UUID
    session_id: uuid.UUID
    seq: int
    role: str
    content: str
    meta: Optional[dict[str, Any]] = None
    processing_time_seconds: Optional[float] = None
    created_at: datetime


class MessageListResponse(BaseModel):
    items: list[MessagePublic]
    total: int


class AnalyzeResponse(BaseModel):
    """Response to POST /sessions/{id}/messages (and the legacy /analyze).

    Identical to the standalone KnowMate AnalyzeResponse, plus the
    session/message IDs needed for chat-history reconstruction.

    V3 changes:
    - Added `charts: Optional[list[ChartData]]` to support multiple
      charts per response. `chart` is kept for backwards compat — it's
      the first chart from `charts` (or None if no charts).
    """

    success: bool
    session_id: uuid.UUID
    message_id: uuid.UUID
    summary: Optional[str] = None
    generated_code: Optional[str] = None
    insights: Optional[str] = None
    table: Optional[list[dict[str, Any]]] = None
    chart: Optional[ChartData] = None          # backwards-compat: first chart
    charts: Optional[list[ChartData]] = None    # full list of charts
    execution_time: float
    errors: Optional[str] = None

    # V2 debug-only fields (populated when debug=True)
    detected_intents: Optional[list[str]] = None
    entities: Optional[ExtractedEntities] = None
    resolved_columns: Optional[list[ColumnResolution]] = None


# --- Report schemas (V3 — full multi-section reports) ----------------------

class ReportSection(BaseModel):
    """One section of a generated report.

    Each section is the output of an independent analysis sub-pipeline:
    the report orchestrator asked the LLM "what sub-question should
    section N answer?", then ran the full AnalystAgent on that
    sub-question. So each section has its own generated code, its own
    table, and its own chart(s).
    """

    title: str
    intent: str  # the sub-question's primary intent
    content: str  # the insight / business explanation for this section
    summary: Optional[str] = None  # short numeric summary from the code
    table: Optional[list[dict[str, Any]]] = None
    charts: list[ChartData] = Field(default_factory=list)
    generated_code: Optional[str] = None
    execution_time_seconds: Optional[float] = None


class ReportResponse(BaseModel):
    """Response to POST /sessions/{id}/reports.

    A structured, multi-section report generated by the agent. The
    orchestrator:
    1. Calls the LLM to generate a section outline based on the user's
       question + the dataset profile.
    2. For each section, runs the full AnalystAgent pipeline on the
       sub-question (so each section has its own code/table/charts).
    3. Calls the LLM one more time to generate an executive summary
       and recommendations from all sections combined.
    """

    success: bool
    session_id: uuid.UUID
    message_id: uuid.UUID  # the persisted assistant message holding this report
    title: str
    executive_summary: Optional[str] = None
    sections: list[ReportSection] = Field(default_factory=list)
    recommendations: Optional[str] = None
    total_execution_time: float
    errors: Optional[str] = None
