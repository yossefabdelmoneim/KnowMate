"""User model.

A User is the identity behind both web (JWT) and programmatic (API
key) access. Sessions, datasets, and API keys all FK back to a user.

For an MVP we don't store roles/permissions — every authenticated user
has the same capabilities. Add a `role` column when you actually need
different access tiers.
"""

from __future__ import annotations

import uuid

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from KnowMate.app.Back_End.db.data_analysis.base import Base
from KnowMate.app.Back_End.models.data_analysis._mixins import TimestampMixin, UUIDPkMixin


class User(Base, UUIDPkMixin, TimestampMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # --- Relationships (lazy by default; routes that need them should
    #     explicitly selectinload to avoid N+1 queries) ---
    sessions: Mapped[list["ChatSession"]] = relationship(  # noqa: F821
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="ChatSession.created_at.desc()",
    )
    api_keys: Mapped[list["ApiKey"]] = relationship(  # noqa: F821
        back_populates="user",
        cascade="all, delete-orphan",
    )
    preferences: Mapped[list["UserPreference"]] = relationship(  # noqa: F821
        back_populates="user",
        cascade="all, delete-orphan",
    )
    memories: Mapped[list["LongTermMemory"]] = relationship(  # noqa: F821
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<User id={self.id} email={self.email!r}>"
