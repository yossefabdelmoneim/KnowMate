"""API key schemas.

Note: the plaintext key is ONLY returned from CreateApiKeyResponse —
all other responses show only the prefix ("sk-knowmate-ab...").
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.Back_End.schemas.data_analysis.common import ORMModel


class ApiKeyCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    quota_per_day: int | None = Field(default=None, ge=1, le=100_000)
    expires_at: datetime | None = None


class ApiKeyCreateResponse(BaseModel):
    """Returned ONCE on creation. The plaintext key is never retrievable again."""

    id: uuid.UUID
    name: str
    plaintext_key: str  # shown once
    key_prefix: str
    quota_per_day: int | None
    expires_at: datetime | None
    created_at: datetime


class ApiKeyPublic(ORMModel):
    """Safe-to-list view of an API key (no plaintext)."""

    id: uuid.UUID
    name: str
    key_prefix: str
    quota_per_day: int | None
    is_active: bool
    last_used_at: datetime | None
    revoked_at: datetime | None
    expires_at: datetime | None
    created_at: datetime


class ApiKeyListResponse(BaseModel):
    items: list[ApiKeyPublic]
    total: int
