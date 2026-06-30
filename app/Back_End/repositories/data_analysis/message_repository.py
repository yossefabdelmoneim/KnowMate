"""Message repository."""

from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.Back_End.models.data_analysis.message import Message
from app.Back_End.repositories.data_analysis.base import BaseRepository


class MessageRepository(BaseRepository[Message]):
    model = Message

    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def list_for_session(
        self,
        session_id: uuid.UUID,
        *,
        offset: int = 0,
        limit: int = 100,
    ) -> tuple[list[Message], int]:
        base = select(Message).where(Message.session_id == session_id)
        items_stmt = (
            base.order_by(Message.seq.asc(), Message.created_at.asc())
            .offset(offset)
            .limit(limit)
        )
        count_stmt = select(func.count()).select_from(base.subquery())

        items = list(self.db.scalars(items_stmt).all())
        total = int(self.db.scalar(count_stmt) or 0)
        return items, total

    def recent_for_session(
        self,
        session_id: uuid.UUID,
        *,
        limit: int,
    ) -> list[Message]:
        """Most recent N messages, oldest-first (so the LLM sees them in order)."""
        stmt = (
            select(Message)
            .where(Message.session_id == session_id)
            .order_by(Message.seq.desc())
            .limit(limit)
        )
        rows = list(self.db.scalars(stmt).all())
        rows.reverse()
        return rows

    def next_seq(self, session_id: uuid.UUID) -> int:
        stmt = select(func.max(Message.seq)).where(Message.session_id == session_id)
        current = self.db.scalar(stmt)
        return int(current or 0) + 1
