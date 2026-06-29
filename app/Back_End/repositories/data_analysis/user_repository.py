"""User repository."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from KnowMate.app.Back_End.models.data_analysis.user import User
from KnowMate.app.Back_End.repositories.data_analysis.base import BaseRepository


class UserRepository(BaseRepository[User]):
    model = User

    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        return self.db.scalars(stmt).first()

    def get_by_id(self, user_id: uuid.UUID) -> User | None:
        return self.get(user_id)

    def list_for_admin(self, *, offset: int = 0, limit: int = 50) -> list[User]:
        return self.list(offset=offset, limit=limit)
