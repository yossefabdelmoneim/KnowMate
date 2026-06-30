"""Chat session schemas."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.Back_End.schemas.data_analysis.common import ORMModel
from app.Back_End.schemas.data_analysis.dataset import DatasetPublic


class SessionCreateRequest(BaseModel):
    title: str = Field(default="New chat", max_length=255)
    description: str | None = None


class SessionUpdateRequest(BaseModel):
    title: str | None = Field(default=None, max_length=255)
    description: str | None = None
    closed: bool | None = None


class SessionPublic(ORMModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    description: str | None
    created_at: datetime
    updated_at: datetime
    closed_at: datetime | None
    dataset: DatasetPublic | None = None
    message_count: int = 0


class SessionListResponse(BaseModel):
    items: list[SessionPublic]
    total: int
