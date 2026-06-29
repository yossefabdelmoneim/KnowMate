"""ChatSession model — the "chat" in "one file per chat".

A session:
- belongs to exactly one user
- has at most ONE dataset attached (enforced at the service layer +
  nullable FK with a unique index on session_id in the datasets table)
- holds many Messages

The "one file per chat" rule is enforced in SessionService — attempts
to attach a second dataset raise DatasetAlreadyAttachedError before
any file is written to disk.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from KnowMate.app.Back_End.db.data_analysis.base import Base
from KnowMate.app.Back_End.models.data_analysis._mixins import TimestampMixin, UUIDPkMixin


class ChatSession(Base, UUIDPkMixin, TimestampMixin):
    __tablename__ = "chat_sessions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(String(255), default="New chat", nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Soft-close flag — closed sessions stay queryable for history but
    # reject new messages.
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # --- Relationships ---
    user: Mapped["User"] = relationship(  # noqa: F821
        back_populates="sessions",
    )
    dataset: Mapped["Dataset | None"] = relationship(  # noqa: F821
        back_populates="session",
        uselist=False,
        cascade="all, delete-orphan",
    )
    messages: Mapped[list["Message"]] = relationship(  # noqa: F821
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="Message.created_at.asc()",
    )

    @property
    def is_closed(self) -> bool:
        return self.closed_at is not None

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ChatSession id={self.id} user_id={self.user_id} title={self.title!r}>"
