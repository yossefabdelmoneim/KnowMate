"""Memory schemas (long-term memory stub).

The schemas are defined so the API surface is stable when extraction
is implemented later. For now they're only used by read endpoints —
no write endpoints exist yet.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from  app.Back_End.schemas.data_analysis.common import ORMModel


class UserPreferencePublic(ORMModel):
    id: uuid.UUID
    user_id: uuid.UUID
    category: str
    key: str
    value: str
    confidence: float
    last_confirmed_at: datetime | None
    created_at: datetime
    updated_at: datetime


class LongTermMemoryPublic(ORMModel):
    id: uuid.UUID
    user_id: uuid.UUID
    kind: str
    content: str
    importance: float
    meta: dict[str, Any] | None = None
    last_accessed_at: datetime | None
    created_at: datetime
    updated_at: datetime


class MemoryListResponse(BaseModel):
    preferences: list[UserPreferencePublic] = Field(default_factory=list)
    memories: list[LongTermMemoryPublic] = Field(default_factory=list)
