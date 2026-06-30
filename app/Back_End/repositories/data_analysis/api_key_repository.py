"""API key repository.

Lookups happen by `key_prefix` (indexed) — the prefix is the stable
identifier we expose; the actual plaintext is never stored. After
fetching by prefix, the service layer hashes the supplied plaintext
and compares against `key_hash` in constant time.
"""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.Back_End.models.data_analysis.api_key import ApiKey
from app.Back_End.repositories.data_analysis.base import BaseRepository


class ApiKeyRepository(BaseRepository[ApiKey]):
    model = ApiKey

    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def get_by_prefix(self, key_prefix: str) -> ApiKey | None:
        stmt = select(ApiKey).where(ApiKey.key_prefix == key_prefix)
        return self.db.scalars(stmt).first()

    def list_for_user(
        self,
        user_id: uuid.UUID,
        *,
        include_revoked: bool = False,
    ) -> list[ApiKey]:
        stmt = select(ApiKey).where(ApiKey.user_id == user_id)
        if not include_revoked:
            stmt = stmt.where(ApiKey.revoked_at.is_(None))
        stmt = stmt.order_by(ApiKey.created_at.desc())
        return list(self.db.scalars(stmt).all())

    def get_for_user(
        self,
        api_key_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> ApiKey | None:
        stmt = select(ApiKey).where(
            ApiKey.id == api_key_id, ApiKey.user_id == user_id,
        )
        return self.db.scalars(stmt).first()
