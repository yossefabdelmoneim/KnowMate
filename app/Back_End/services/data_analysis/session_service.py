"""SessionService — chat session lifecycle.

Enforces business rules:
- A session belongs to exactly one user (cross-user access → NotFoundError).
- Closing a session prevents new messages but keeps history.
- The "one file per chat" rule is delegated to DatasetService.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.Back_End.core.data_analysis.exceptions import ConflictError, NotFoundError, ValidationError
from app.Back_End.models.data_analysis.chat_session import ChatSession
from app.Back_End.repositories.data_analysis.session_repository import SessionRepository
from app.Back_End.schemas.data_analysis.session import SessionCreateRequest, SessionPublic, SessionUpdateRequest

logger = logging.getLogger(__name__)


class SessionService:
    """CRUD + lifecycle for chat sessions."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = SessionRepository(db)

    def create(
        self,
        *,
        user_id: uuid.UUID,
        request: SessionCreateRequest,
    ) -> ChatSession:
        session = ChatSession(
            user_id=user_id,
            title=request.title,
            description=request.description,
        )
        self.repo.add(session)
        self.db.commit()
        self.db.refresh(session)
        logger.info("Created session %s for user %s", session.id, user_id)
        return session

    def get_for_user(
        self,
        *,
        user_id: uuid.UUID,
        session_id: uuid.UUID,
    ) -> ChatSession:
        session = self.repo.get_for_user(session_id, user_id)
        if session is None:
            raise NotFoundError(f"Session {session_id} not found.")
        return session

    def list_for_user(
        self,
        *,
        user_id: uuid.UUID,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[ChatSession], int]:
        return self.repo.list_for_user(user_id, offset=offset, limit=limit)

    def update(
        self,
        *,
        user_id: uuid.UUID,
        session_id: uuid.UUID,
        request: SessionUpdateRequest,
    ) -> ChatSession:
        session = self.get_for_user(user_id=user_id, session_id=session_id)

        if request.title is not None:
            session.title = request.title
        if request.description is not None:
            session.description = request.description
        if request.closed is True:
            if session.closed_at is None:
                session.closed_at = datetime.now(timezone.utc)
        elif request.closed is False:
            session.closed_at = None

        self.db.flush()
        self.db.commit()
        self.db.refresh(session)
        return session

    def close(
        self,
        *,
        user_id: uuid.UUID,
        session_id: uuid.UUID,
    ) -> ChatSession:
        return self.update(
            user_id=user_id, session_id=session_id,
            request=SessionUpdateRequest(closed=True),
        )

    def delete(self, *, user_id: uuid.UUID, session_id: uuid.UUID) -> None:
        session = self.get_for_user(user_id=user_id, session_id=session_id)
        self.repo.delete(session)
        self.db.commit()
        logger.info("Deleted session %s", session_id)

    def ensure_open(self, session: ChatSession) -> None:
        """Raise ConflictError if the session is closed."""
        if session.is_closed:
            raise ConflictError("This chat is closed and cannot accept new messages.")

    @staticmethod
    def to_public(session: ChatSession, *, message_count: int = 0) -> SessionPublic:
        from app.Back_End.services.data_analysis.dataset_service import DatasetService

        dataset_public = (
            DatasetService.to_public(session.dataset) if session.dataset else None
        )
        return SessionPublic(
            id=session.id,
            user_id=session.user_id,
            title=session.title,
            description=session.description,
            created_at=session.created_at,
            updated_at=session.updated_at,
            closed_at=session.closed_at,
            dataset=dataset_public,
            message_count=message_count,
        )
