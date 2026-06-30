"""Restricted Executor — runs AST-validated LLM-generated code.

Lifted from the standalone KnowMate code_executor.py's execute_code
function. The MAX_TABLE_ROWS cap and ChartData conversion logic are
unchanged; only the import paths moved.
"""

from __future__ import annotations

import base64
import io
import logging
import time
from dataclasses import dataclass
from typing import Any, Optional

import matplotlib
matplotlib.use("Agg")  # headless backend — no GUI, no file system access for rendering
import matplotlib.figure
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from app.Back_End.core.config import settings
from app.Back_End.execution.validator import CodeValidationError, extract_code_block, validate_code
from app.Back_End.schemas.data_analysis.message import AnalysisResult, ChartData

logger = logging.getLogger(__name__)

MAX_TABLE_ROWS = settings.executor_max_table_rows

# Safely extract builtins whether they are inside a dict context or an object
BUILTIN_SOURCE = __builtins__ if isinstance(__builtins__, dict) else __builtins__.__dict__

# Builtins exposed inside generated code's exec() namespace.
SAFE_BUILTINS: dict[str, Any] = {
    name: BUILTIN_SOURCE[name]
    for name in (
        "abs", "all", "any", "bool", "dict", "enumerate", "float", "int",
        "isinstance", "len", "list", "max", "min", "print", "range",
        "round", "set", "sorted", "str", "sum", "tuple", "zip",
        "Exception", "ValueError", "TypeError", "KeyError", "IndexError",
        "StopIteration", "ZeroDivisionError", "True", "False", "None",
    )
    if name in BUILTIN_SOURCE
}

# Enable bytecode-level import structures safely for authorized packages.
SAFE_BUILTINS["__import__"] = BUILTIN_SOURCE["__import__"]


@dataclass
class ExecutionOutcome:
    """Result of attempting to execute generated code."""

    success: bool
    result: Optional[AnalysisResult]
    execution_time: float
    error: Optional[str]


def _build_restricted_namespace(df: pd.DataFrame) -> dict[str, Any]:
    """Build the exec() namespace exposed to generated code."""
    return {
        "df": df.copy(),
        "pd": pd,
        "np": np,
        "plt": plt,
        "px": px,
        "go": go,
        "result": {},
        "__builtins__": SAFE_BUILTINS,
    }


def _figure_to_chart_data(figure_obj: Any) -> Optional[ChartData]:
    """Convert a matplotlib or plotly figure into a ChartData model."""
    if isinstance(figure_obj, matplotlib.figure.Figure):
        buffer = io.BytesIO()
        figure_obj.savefig(buffer, format="png", bbox_inches="tight")
        encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return ChartData(type="image", data=encoded)

    if isinstance(figure_obj, go.Figure):
        return ChartData(type="plotly", data=figure_obj.to_json())

    logger.warning("result['figure'] was of unsupported type %s — ignoring it.", type(figure_obj))
    return None


def _table_to_records(table_obj: Any) -> Optional[list[dict[str, Any]]]:
    """Convert a DataFrame (or Series) into JSON-friendly records, capped in size."""
    if isinstance(table_obj, pd.Series):
        table_obj = table_obj.to_frame()

    if not isinstance(table_obj, pd.DataFrame):
        logger.warning("result['table'] was of unsupported type %s — ignoring it.", type(table_obj))
        return None

    if len(table_obj) > MAX_TABLE_ROWS:
        logger.info("Truncating table result from %d to %d rows.", len(table_obj), MAX_TABLE_ROWS)
        table_obj = table_obj.head(MAX_TABLE_ROWS)

    return table_obj.where(pd.notnull(table_obj), None).to_dict(orient="records")


def _parse_result_dict(raw_result: Any) -> AnalysisResult:
    """Validate and convert the raw `result` dict produced by generated code.

    Supports both single-figure (`result["figure"]`) and multi-figure
    (`result["figures"]` as a list) outputs. When both are present, they
    are merged into a single list (figure first, then figures).
    """
    if not isinstance(raw_result, dict):
        raise CodeValidationError(
            f"Generated code must assign a dict to `result`, got {type(raw_result)}."
        )

    summary = raw_result.get("summary")
    if summary is not None and not isinstance(summary, str):
        summary = str(summary)

    table = _table_to_records(raw_result["table"]) if raw_result.get("table") is not None else None

    # Collect figures from both `figure` (single) and `figures` (list).
    figures: list[ChartData] = []
    if raw_result.get("figure") is not None:
        single = _figure_to_chart_data(raw_result["figure"])
        if single is not None:
            figures.append(single)
    if raw_result.get("figures") is not None:
        multi = raw_result["figures"]
        if not isinstance(multi, (list, tuple)):
            logger.warning(
                "result['figures'] was of unsupported type %s — ignoring it.",
                type(multi),
            )
        else:
            for fig in multi:
                chart = _figure_to_chart_data(fig)
                if chart is not None:
                    figures.append(chart)

    kpis = raw_result.get("kpis") if isinstance(raw_result.get("kpis"), dict) else None

    return AnalysisResult(
        summary=summary, table=table,
        figure=figures[0] if figures else None,        # backwards-compat: first chart
        figures=figures if figures else None,           # full list
        kpis=kpis,
    )


def execute_code(code: str, df: pd.DataFrame) -> ExecutionOutcome:
    """Validate and run generated code against the given DataFrame."""
    start_time = time.perf_counter()
    cleaned_code = extract_code_block(code)

    try:
        validate_code(cleaned_code)
        namespace = _build_restricted_namespace(df)
        exec(compile(cleaned_code, "<generated_code>", "exec"), namespace)

        raw_result = namespace.get("result")
        parsed_result = _parse_result_dict(raw_result)

        elapsed = time.perf_counter() - start_time
        logger.info("Code executed successfully in %.3fs", elapsed)
        return ExecutionOutcome(success=True, result=parsed_result, execution_time=elapsed, error=None)

    except CodeValidationError as exc:
        elapsed = time.perf_counter() - start_time
        logger.warning("Code validation failed: %s", exc)
        return ExecutionOutcome(success=False, result=None, execution_time=elapsed, error=str(exc))

    except Exception as exc:
        elapsed = time.perf_counter() - start_time
        logger.exception("Generated code raised an exception during execution.")
        return ExecutionOutcome(
            success=False, result=None, execution_time=elapsed,
            error=f"{type(exc).__name__}: {exc}",
        )

    finally:
        plt.close("all")
