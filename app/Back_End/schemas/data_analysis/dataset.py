"""Dataset schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel

from app.Back_End.schemas.data_analysis.common import ORMModel


class DatasetPublic(ORMModel):
    """Subset of the Dataset model returned in API responses."""

    id: uuid.UUID
    session_id: uuid.UUID
    original_filename: str
    file_extension: str
    content_type: str | None
    size_bytes: int
    row_count: int | None
    column_count: int | None
    created_at: datetime


class DatasetUploadResponse(BaseModel):
    """Returned after a successful dataset attach to a session."""

    dataset: DatasetPublic
    session_id: uuid.UUID


class SupportedFileTypesResponse(BaseModel):
    """Returned by GET /datasets/supported-types — drives UI hints."""

    extensions: list[str]
    max_size_bytes: int
    description: str
