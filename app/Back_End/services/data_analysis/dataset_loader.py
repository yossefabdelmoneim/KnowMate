"""Dataset loader — multi-format file → pandas DataFrame.

EXPANDED from the standalone KnowMate (which only supported CSV + XLSX)
to also handle TSV, plain-text tabular, XLS (legacy Excel), ODS, JSON,
JSONL, Parquet, and Stata .dta.

Each format gets a small loader function. The dispatcher picks one by
extension; failures raise ValueError (which DatasetService translates
to UnsupportedFileTypeError / ValidationError).

The loader is intentionally separate from DatasetService so:
- It's trivially testable in isolation (no DB, no FS).
- Adding a new format is one new function + one line in the dispatcher.
"""

from __future__ import annotations

import io
import logging
from typing import Callable

import pandas as pd

logger = logging.getLogger(__name__)


def _load_csv(buf: io.BytesIO) -> pd.DataFrame:
    return pd.read_csv(buf)


def _load_tsv(buf: io.BytesIO) -> pd.DataFrame:
    return pd.read_csv(buf, sep="\t")


def _load_txt(buf: io.BytesIO) -> pd.DataFrame:
    """Plain text — try CSV with auto-sniffing first, fall back to TSV.

    .txt is intentionally permissive: it's commonly used for both
    comma-separated and tab-separated exports. Let pandas sniff it.
    """
    try:
        return pd.read_csv(buf, sep=None, engine="python")
    except Exception:
        buf.seek(0)
        return pd.read_csv(buf, sep="\t")


def _load_xlsx(buf: io.BytesIO) -> pd.DataFrame:
    return pd.read_excel(buf, engine="openpyxl")


def _load_xls(buf: io.BytesIO) -> pd.DataFrame:
    # Legacy .xls requires the `xlrd` package.
    return pd.read_excel(buf, engine="xlrd")


def _load_ods(buf: io.BytesIO) -> pd.DataFrame:
    # OpenDocument spreadsheet requires `odfpy`.
    return pd.read_excel(buf, engine="odf")


def _load_json(buf: io.BytesIO) -> pd.DataFrame:
    # pandas auto-detects list-of-records vs dict-of-columns.
    return pd.read_json(buf)


def _load_jsonl(buf: io.BytesIO) -> pd.DataFrame:
    return pd.read_json(buf, lines=True)


def _load_parquet(buf: io.BytesIO) -> pd.DataFrame:
    # Parquet requires `pyarrow`.
    return pd.read_parquet(buf)


def _load_stata(buf: io.BytesIO) -> pd.DataFrame:
    return pd.read_stata(buf)


# Extension -> loader. Adding a format = add one entry here + the
# loader function above + the dependency in requirements.txt.
_LOADERS: dict[str, Callable[[io.BytesIO], pd.DataFrame]] = {
    ".csv": _load_csv,
    ".tsv": _load_tsv,
    ".txt": _load_txt,
    ".xlsx": _load_xlsx,
    ".xls": _load_xls,
    ".ods": _load_ods,
    ".json": _load_json,
    ".jsonl": _load_jsonl,
    ".parquet": _load_parquet,
    ".dta": _load_stata,
}


def get_supported_extensions() -> tuple[str, ...]:
    """Return the tuple of supported extensions (with leading dot, lowercase)."""
    return tuple(_LOADERS.keys())


def load_dataset(file_bytes: bytes, filename: str) -> pd.DataFrame:
    """Load raw uploaded file bytes into a pandas DataFrame.

    Dispatches by file extension. Raises ValueError on unsupported
    extension, parse failure, or empty result.
    """
    lowered = filename.lower()
    ext = next(
        (e for e in _LOADERS if lowered.endswith(e)),
        None,
    )
    if ext is None:
        supported = ", ".join(_LOADERS.keys())
        raise ValueError(
            f"Unsupported file type for '{filename}'. Supported: {supported}."
        )

    try:
        df = _LOADERS[ext](io.BytesIO(file_bytes))
    except Exception as exc:
        logger.exception("Failed to parse uploaded file '%s' as %s", filename, ext)
        raise ValueError(
            f"Could not parse '{filename}' as {ext[1:].upper()}: {exc}"
        ) from exc

    if df is None or df.empty or df.shape[1] == 0:
        raise ValueError(f"Uploaded file '{filename}' contains no usable data.")

    logger.info("Loaded dataset '%s' (ext=%s) with shape %s", filename, ext, df.shape)
    return df


def is_extension_supported(filename: str) -> bool:
    lowered = filename.lower()
    return any(lowered.endswith(ext) for ext in _LOADERS)
