"""Memory repository (long-term memory stub).

Fully functional CRUD — the only thing that's stubbed is the
*extraction* logic (services/memory_service.py). When extraction is
implemented, the agent populates these tables; until then they stay
empty for every user.
"""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from  app.Back_End.models.data_analysis.long_term_memory import LongTermMemory, UserPreference
from  app.Back_End.repositories.data_analysis.base import BaseRepository


class UserPreferenceRepository(BaseRepository[UserPreference]):
    model = UserPreference

    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def list_for_user(
        self,
        user_id: uuid.UUID,
        *,
        category: str | None = None,
    ) -> list[UserPreference]:
        stmt = select(UserPreference).where(UserPreference.user_id == user_id)
        if category is not None:
            stmt = stmt.where(UserPreference.category == category)
        stmt = stmt.order_by(UserPreference.category.asc(), UserPreference.key.asc())
        return list(self.db.scalars(stmt).all())

    def get_by_key(
        self,
        user_id: uuid.UUID,
        category: str,
        key: str,
    ) -> UserPreference | None:
        stmt = select(UserPreference).where(
            UserPreference.user_id == user_id,
            UserPreference.category == category,
            UserPreference.key == key,
        )
        return self.db.scalars(stmt).first()


class LongTermMemoryRepository(BaseRepository[LongTermMemory]):
    model = LongTermMemory

    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def list_for_user(
        self,
        user_id: uuid.UUID,
        *,
        kind: str | None = None,
        limit: int = 50,
    ) -> list[LongTermMemory]:
        stmt = select(LongTermMemory).where(LongTermMemory.user_id == user_id)
        if kind is not None:
            stmt = stmt.where(LongTermMemory.kind == kind)
        stmt = stmt.order_by(LongTermMemory.importance.desc(), LongTermMemory.created_at.desc()).limit(limit)
        return list(self.db.scalars(stmt).all())

    def touch(self, memory_id: uuid.UUID) -> None:
        """Update last_accessed_at — called when a memory is surfaced to the agent."""
        from datetime import datetime, timezone
        stmt = select(LongTermMemory).where(LongTermMemory.id == memory_id)
        memory = self.db.scalars(stmt).first()
        if memory is not None:
            memory.last_accessed_at = datetime.now(timezone.utc)
            self.db.flush()
