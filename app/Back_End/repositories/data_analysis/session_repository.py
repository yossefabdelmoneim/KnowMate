"""ChatSession repository."""

from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from KnowMate.app.Back_End.models.data_analysis.chat_session import ChatSession
from KnowMate.app.Back_End.models.data_analysis.message import Message
from KnowMate.app.Back_End.repositories.data_analysis.base import BaseRepository


class SessionRepository(BaseRepository[ChatSession]):
    model = ChatSession

    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def list_for_user(
        self,
        user_id: uuid.UUID,
        *,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[ChatSession], int]:
        """List a user's sessions, newest first, with total count."""
        base = select(ChatSession).where(ChatSession.user_id == user_id)
        items_stmt = (
            base.options(selectinload(ChatSession.dataset))
            .order_by(ChatSession.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        count_stmt = select(func.count()).select_from(base.subquery())

        items = list(self.db.scalars(items_stmt).all())
        total = int(self.db.scalar(count_stmt) or 0)
        return items, total

    def get_for_user(
        self,
        session_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> ChatSession | None:
        """Get a session, ensuring it belongs to `user_id`."""
        stmt = (
            select(ChatSession)
            .options(selectinload(ChatSession.dataset))
            .where(ChatSession.id == session_id, ChatSession.user_id == user_id)
        )
        return self.db.scalars(stmt).first()

    def message_count(self, session_id: uuid.UUID) -> int:
        stmt = select(func.count()).where(Message.session_id == session_id)
        return int(self.db.scalar(stmt) or 0)
