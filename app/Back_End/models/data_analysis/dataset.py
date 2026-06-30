"""Dataset model — metadata for one uploaded file.

Each row is one file owned by one session. The "one file per chat"
rule is enforced by:
- This table has a UNIQUE constraint on session_id (a session can
  only have one dataset row).
- SessionService.attach_dataset() checks for an existing dataset row
  before accepting an upload, raising DatasetAlreadyAttachedError.

The raw file bytes live on disk at `storage_path`; this row only
holds the metadata needed to:
1. Re-load the DataFrame on subsequent messages in the same session.
2. Display file info in the UI (filename, size, row/column counts).
3. Compute the dataset profile once and cache it (avoid re-profiling
   on every message in a long chat).

`profile_json` caches the DatasetProfile Pydantic model serialized as
JSON. Re-parsing it per message is cheap (one pydantic parse); re-
profiling a 100k-row dataframe per message is not.
"""

from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.Back_End.db.data_analysis.base import Base
from app.Back_End.db.data_analysis.types import JSONB
from app.Back_End.models.data_analysis._mixins import TimestampMixin, UUIDPkMixin


class Dataset(Base, UUIDPkMixin, TimestampMixin):
    __tablename__ = "datasets"
    __table_args__ = (
        {'extend_existing': True}, # Add this line
        # Enforces "one file per chat" at the DB level too — even if
        # the service layer had a bug, the unique constraint would
        # reject a second insert.
        # Unique is implied by the OneToOne relationship + this index.
    )

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("chat_sessions.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,  # one dataset per session, hard-enforced
        index=True,
    )

    # Original filename as the user uploaded it (used for display only).
    original_filename: Mapped[str] = mapped_column(String(512), nullable=False)

    # Normalized extension (lowercased, with dot), e.g. ".csv".
    file_extension: Mapped[str] = mapped_column(String(16), nullable=False)

    # MIME type as detected by the loader (best-effort; not authoritative).
    content_type: Mapped[str | None] = mapped_column(String(128), nullable=True)

    # Size in bytes of the stored file.
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)

    # Absolute path on disk where the file is stored.
    # Format: <data_root>/datasets/<user_id>/<session_id>/<filename>
    storage_path: Mapped[str] = mapped_column(String(1024), nullable=False)

    # Row + column counts captured at upload time — cheap to compute
    # and useful for UI display + sanity checks on subsequent loads.
    row_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    column_count: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Cached DatasetProfile (Pydantic) serialized as JSON.
    # Re-parsed per message in services/analyst_agent.py.
    profile_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # --- Relationships ---
    session: Mapped["ChatSession"] = relationship(  # noqa: F821
        back_populates="dataset",
        uselist=False,
    )

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<Dataset id={self.id} session_id={self.session_id} "
            f"filename={self.original_filename!r}>"
        )