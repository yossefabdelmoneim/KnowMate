"""Chart auto-generator — builds charts from table data when the LLM didn't."""
from __future__ import annotations
import io, logging, base64
from typing import Any
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from app.Back_End.schemas.data_analysis.message import ChartData

logger = logging.getLogger(__name__)
_CHART_WORTHY_INTENTS = {"visualization","sorting","aggregation","comparison","distribution","trend_analysis","correlation","summary","statistics"}


def auto_generate_chart(table, intents, user_question=""):
    if not table: return None
    try: df = pd.DataFrame(table)
    except Exception: return None
    if df.empty or df.shape[1]==0: return None
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    if not numeric_cols: return None
    if len(df)>50: df = df.sort_values(numeric_cols[0], ascending=False).head(20)
    q = user_question.lower()
    user_asked = any(w in q for w in ("chart","plot","visualize","visualise","graph","histogram"))
    kind = _pick(df, numeric_cols, intents, user_asked)
    if kind is None: return None
    try:
        fig = _build(df, kind, numeric_cols)
        return _figure_to_chart_data(fig) if fig else None
    except Exception as exc:
        logger.warning("auto_generate_chart failed: %s", exc)
        return None


def _pick(df, numeric_cols, intents, user_asked):
    other = [c for c in df.columns if c not in numeric_cols]
    has_date = _has_date(df, other)
    if "distribution" in intents: return "hist"
    if "correlation" in intents and len(numeric_cols)>=2: return "scatter"
    if "trend_analysis" in intents and has_date: return "line"
    if other:
        if any(i in _CHART_WORTHY_INTENTS for i in intents):
            return "bar"
        if user_asked or len(numeric_cols) == 1:
            return "bar"
    if len(numeric_cols) >= 1:
        return "hist"
    return None


def _has_date(df, cols):
    for c in cols:
        try: pd.to_datetime(df[c], errors="raise"); return True
        except: continue
    return False


def _build(df, kind, numeric_cols):
    other = [c for c in df.columns if c not in numeric_cols]
    if kind=="bar":
        if not other: return None
        x,y = other[0], numeric_cols[0]
        fig,ax = plt.subplots(figsize=(10,5))
        ax.bar(df[x].astype(str), df[y]); ax.set_xlabel(x); ax.set_ylabel(y); ax.set_title(f"{y} by {x}")
        if len(df)>5: plt.xticks(rotation=45, ha="right")
        plt.tight_layout(); return fig
    if kind=="line":
        if not other: return None
        x_col = other[0]
        try: x = pd.to_datetime(df[x_col])
        except: x = df[x_col]
        y = numeric_cols[0]
        fig,ax = plt.subplots(figsize=(10,5))
        ax.plot(x, df[y], marker="o"); ax.set_xlabel(x_col); ax.set_ylabel(y); ax.set_title(f"{y} over {x_col}")
        if len(df)>5: plt.xticks(rotation=45, ha="right")
        plt.tight_layout(); return fig
    if kind=="hist":
        y = numeric_cols[0]
        fig,ax = plt.subplots(figsize=(10,5))
        ax.hist(df[y].dropna(), bins=min(20,max(5,len(df)//2)))
        ax.set_xlabel(y); ax.set_ylabel("Frequency"); ax.set_title(f"Distribution of {y}")
        plt.tight_layout(); return fig
    if kind=="scatter":
        if len(numeric_cols)<2: return None
        x,y = numeric_cols[0], numeric_cols[1]
        fig,ax = plt.subplots(figsize=(10,5))
        ax.scatter(df[x], df[y]); ax.set_xlabel(x); ax.set_ylabel(y); ax.set_title(f"{y} vs {x}")
        plt.tight_layout(); return fig
    return None


def _figure_to_chart_data(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=100)
    plt.close(fig)
    return ChartData(type="image", data=base64.b64encode(buf.getvalue()).decode("utf-8"))