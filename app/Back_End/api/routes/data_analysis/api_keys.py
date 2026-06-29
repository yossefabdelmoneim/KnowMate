"""API key management routes — DEFERRED but scaffolded.

Per the user's "we can wait for this feature" decision, this router is
NOT mounted in main.py by default. To enable, uncomment the include
line in main.py. All endpoints require JWT auth (you can only manage
your own API keys via the web UI; programmatic clients can't mint new
keys for themselves).
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from api.deps import get_current_user
from db.session import get_db
from models.data_analysis.user import User
from schemas.data_analysis.api_key import (
    ApiKeyCreateRequest, ApiKeyCreateResponse, ApiKeyListResponse, ApiKeyPublic,
)
from services.data_analysis.api_key_service import ApiKeyService

router = APIRouter(prefix="/api-keys", tags=["api-keys"])


@router.post("", response_model=ApiKeyCreateResponse, status_code=status.HTTP_201_CREATED)
def create_api_key(
    request: ApiKeyCreateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ApiKeyCreateResponse:
    """Issue a new API key. The plaintext is returned ONCE — store it securely."""
    return ApiKeyService(db).create(user_id=user.id, request=request)


@router.get("", response_model=ApiKeyListResponse)
def list_api_keys(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ApiKeyListResponse:
    return ApiKeyService(db).list_for_user(user_id=user.id)


@router.delete("/{api_key_id}", response_model=ApiKeyPublic)
def revoke_api_key(
    api_key_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ApiKeyPublic:
    return ApiKeyService(db).revoke(user_id=user.id, api_key_id=api_key_id)
