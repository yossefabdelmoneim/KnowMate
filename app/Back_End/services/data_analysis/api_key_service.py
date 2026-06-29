"""ApiKeyService — issue, validate, revoke per-user API keys.

DEFERRED FEATURE per the user ("we can wait for this feature") — but
the service + model + repository + middleware are scaffolded so the
surface is ready. To enable, expose the routes in api/routes/api_keys.py
(they're already written but not mounted in main.py — uncomment to
enable).
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from KnowMate.app.Back_End.core.config import settings
from KnowMate.app.Back_End.core.data_analysis.exceptions import InvalidApiKeyError, NotFoundError
from KnowMate.app.Back_End.core.security import constant_time_eq, generate_api_key, hash_api_key
from KnowMate.app.Back_End.models.data_analysis.api_key import ApiKey
from KnowMate.app.Back_End.models.data_analysis.user import User
from KnowMate.app.Back_End.repositories.data_analysis.api_key_repository import ApiKeyRepository
from KnowMate.app.Back_End.schemas.data_analysis.api_key import (
    ApiKeyCreateRequest, ApiKeyCreateResponse, ApiKeyListResponse, ApiKeyPublic,
)

logger = logging.getLogger(__name__)

# How many chars of the plaintext key to store as the displayable prefix.
# Full prefix is "sk-knowmate-" + 8 chars of secret = ~20 chars total.
_KEY_PREFIX_DISPLAY_LEN = len(settings.api_key_prefix) + 8


class ApiKeyService:
    """Per-user API key management."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = ApiKeyRepository(db)

    def create(
        self,
        *,
        user_id: uuid.UUID,
        request: ApiKeyCreateRequest,
    ) -> ApiKeyCreateResponse:
        """Issue a new API key. Returns the plaintext ONCE."""
        plaintext, key_hash = generate_api_key()
        key_prefix = plaintext[:_KEY_PREFIX_DISPLAY_LEN]

        api_key = ApiKey(
            user_id=user_id,
            name=request.name,
            key_prefix=key_prefix,
            key_hash=key_hash,
            quota_per_day=request.quota_per_day,
            expires_at=request.expires_at,
        )
        self.repo.add(api_key)
        self.db.commit()
        self.db.refresh(api_key)

        logger.info("Created API key %s for user %s", api_key.id, user_id)
        return ApiKeyCreateResponse(
            id=api_key.id,
            name=api_key.name,
            plaintext_key=plaintext,  # shown once
            key_prefix=api_key.key_prefix,
            quota_per_day=api_key.quota_per_day,
            expires_at=api_key.expires_at,
            created_at=api_key.created_at,
        )

    def list_for_user(self, *, user_id: uuid.UUID) -> ApiKeyListResponse:
        keys = self.repo.list_for_user(user_id)
        return ApiKeyListResponse(
            items=[ApiKeyPublic.model_validate(k) for k in keys],
            total=len(keys),
        )

    def revoke(self, *, user_id: uuid.UUID, api_key_id: uuid.UUID) -> ApiKeyPublic:
        api_key = self.repo.get_for_user(api_key_id, user_id)
        if api_key is None:
            raise NotFoundError("API key not found.")
        api_key.is_active = False
        api_key.revoked_at = datetime.now(timezone.utc)
        self.db.flush()
        self.db.commit()
        self.db.refresh(api_key)
        return ApiKeyPublic.model_validate(api_key)

    # --- Validation (called by the auth middleware) ------------------------

    def validate_key(self, plaintext: str) -> User:
        """Resolve an API key plaintext to its owning User.

        Raises InvalidApiKeyError on any failure (not found, revoked,
        expired, hash mismatch). Updates last_used_at on success.
        """
        if not plaintext or not plaintext.startswith(settings.api_key_prefix):
            raise InvalidApiKeyError("Malformed API key.")

        # The prefix we store is the first N chars — use it for the
        # indexed lookup, then verify the full key against the hash.
        key_prefix = plaintext[:_KEY_PREFIX_DISPLAY_LEN]
        api_key = self.repo.get_by_prefix(key_prefix)
        if api_key is None:
            raise InvalidApiKeyError("API key not found.")

        if not constant_time_eq(hash_api_key(plaintext), api_key.key_hash):
            raise InvalidApiKeyError("API key hash mismatch.")

        if not api_key.is_valid:
            raise InvalidApiKeyError("API key is revoked or expired.")

        api_key.last_used_at = datetime.now(timezone.utc)
        self.db.flush()
        self.db.commit()

        # Eagerly load the user relationship — the caller needs it.
        user = api_key.user
        if user is None or not user.is_active:
            raise InvalidApiKeyError("API key has no active user.")
        return user
