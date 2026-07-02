"""ApiKey model — long-lived per-user API keys for programmatic access.

The plaintext key is shown to the user EXACTLY ONCE at creation time
and never stored. We persist only `key_hash` (SHA-256). Lookups are
done by `key_prefix` (the first 12 chars of the plaintext, e.g.
"sk-knowmate-") + a hash comparison in the application layer.

Why store `key_prefix` at all? Because hashing is one-way, we can't
list "which keys does this user have" without an indexable identifier.
The prefix gives us a stable per-key handle for listing/revocation
without exposing the secret.

DEFERRED FEATURE: the user said "we can wait for this feature" — the
model + repository + middleware are scaffolded so the surface is
ready, but the API-key auth path is wired in a minimal way (no
listing/rotation endpoints yet, just creation + validation).
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.Back_End.db.data_analysis.base import Base
from app.Back_End.models.data_analysis._mixins import TimestampMixin, UUIDPkMixin


class ApiKey(Base, UUIDPkMixin, TimestampMixin):
    __tablename__ = "api_keys"
    __table_args__ = {'extend_existing': True}

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("data_analysis_users.id", ondelete="CASCADE"), # Updated ForeignKey
        nullable=False,
        index=True,
    )

    # Human-readable label so the user can tell keys apart in a list
    # ("Production CLI", "Laptop notebook", etc.).
    name: Mapped[str] = mapped_column(String(128), nullable=False)

    # First N chars of the plaintext key — stable identifier for
    # display ("sk-knowmate-ab...") and for admin lookups.
    key_prefix: Mapped[str] = mapped_column(String(32), nullable=False, unique=True, index=True)

    # SHA-256 hash of the full plaintext key. Never store the plaintext.
    key_hash: Mapped[str] = mapped_column(String(128), nullable=False, unique=True, index=True)

    # Optional per-day quota override; falls back to settings.api_key_default_quota_per_day.
    quota_per_day: Mapped[int | None] = mapped_column(Integer, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # --- Relationships ---
    user: Mapped["User"] = relationship(  # noqa: F821
        back_populates="api_keys",
    )

    @property
    def is_valid(self) -> bool:
        """True if the key can currently be used to authenticate."""
        if not self.is_active or self.revoked_at is not None:
            return False
        if self.expires_at is not None:
            # Naive comparison — fine since expires_at is timezone-aware.
            import datetime as _dt
            return _dt.datetime.now(self.expires_at.tzinfo) < self.expires_at
        return True

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ApiKey id={self.id} name={self.name!r} prefix={self.key_prefix!r}>"