"""Dataset profiling — builds a DatasetProfile from a DataFrame.

Lifted from the standalone KnowMate dataset.py's build_dataset_profile
function. The load_dataset function moved to services/dataset_loader.py
(which now supports many more file formats).
"""

from __future__ import annotations

import logging
from typing import Any

import numpy as np
import pandas as pd

from KnowMate.app.Back_End.schemas.data_analysis.message import (
    CategoricalColumnStats, ColumnProfile, DatasetProfile, NumericColumnStats,
)

logger = logging.getLogger(__name__)

TOP_N_CATEGORICAL_VALUES = 5


def _build_numeric_stats(series: pd.Series) -> NumericColumnStats:
    described = series.describe()

    def _safe_float(value: Any) -> float | None:
        return float(value) if pd.notna(value) else None

    return NumericColumnStats(
        count=int(described.get("count", 0)),
        mean=_safe_float(described.get("mean")),
        std=_safe_float(described.get("std")),
        min=_safe_float(described.get("min")),
        q25=_safe_float(described.get("25%")),
        median=_safe_float(described.get("50%")),
        q75=_safe_float(described.get("75%")),
        max=_safe_float(described.get("max")),
    )


def _build_categorical_stats(series: pd.Series) -> CategoricalColumnStats:
    value_counts = series.value_counts(dropna=True).head(TOP_N_CATEGORICAL_VALUES)
    top_values = {str(index): int(count) for index, count in value_counts.items()}
    return CategoricalColumnStats(top_values=top_values)


def build_dataset_profile(df: pd.DataFrame) -> DatasetProfile:
    """Build a DatasetProfile from a loaded DataFrame.

    Column classification rule:
    - numeric dtypes (int/float) → numeric_stats
    - everything else → categorical_stats (string repr of values)
    """
    numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_columns = [col for col in df.columns if col not in numeric_columns]

    column_profiles: list[ColumnProfile] = []
    for column_name in df.columns:
        series = df[column_name]
        is_numeric = column_name in numeric_columns

        column_profiles.append(
            ColumnProfile(
                name=str(column_name),
                dtype=str(series.dtype),
                null_count=int(series.isna().sum()),
                unique_count=int(series.nunique(dropna=True)),
                numeric_stats=_build_numeric_stats(series) if is_numeric else None,
                categorical_stats=_build_categorical_stats(series) if not is_numeric else None,
            )
        )

    profile = DatasetProfile(
        row_count=int(df.shape[0]),
        column_count=int(df.shape[1]),
        columns=column_profiles,
        numeric_columns=[str(c) for c in numeric_columns],
        categorical_columns=[str(c) for c in categorical_columns],
    )

    logger.info(
        "Built profile: %d rows, %d columns (%d numeric, %d categorical)",
        profile.row_count, profile.column_count,
        len(numeric_columns), len(categorical_columns),
    )
    return profile
