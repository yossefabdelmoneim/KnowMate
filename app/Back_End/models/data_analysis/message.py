"""Message model — one row per turn inside a chat session.

`role` follows the OpenAI chat convention:
- "user"     — question sent by the human
- "assistant" — response from the analyst agent
- "system"   — reserved for injected context (rare; not user-visible)

The agent's structured response (table, chart, code, etc.) is stored
as JSON in `meta` so the chat history endpoint can reconstruct the
full response without re-running the agent. The `content` column
holds the human-readable text (the user's question for role=user, the
insight text for role=assistant).
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.Back_End.db.data_analysis.base import Base
from app.Back_End.db.data_analysis.types import JSONB
from app.Back_End.models.data_analysis._mixins import TimestampMixin, UUIDPkMixin


class Message(Base, UUIDPkMixin, TimestampMixin):
    __tablename__ = "messages"

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("chat_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # 0 = oldest, increasing. Used for the short-term memory window
    # without relying on created_at tie-breaking.
    seq: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    role: Mapped[str] = mapped_column(String(32), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # For assistant messages: the full structured payload (summary,
    # table preview, chart, generated_code, execution_time, etc.).
    # NULL for user messages.
    meta: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Time spent producing this message (assistant only). Useful for
    # UI latency display and per-session analytics.
    processing_time_seconds: Mapped[float | None] = mapped_column(nullable=True)

    # --- Relationships ---
    session: Mapped["ChatSession"] = relationship(  # noqa: F821
        back_populates="messages",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Message id={self.id} role={self.role!r} seq={self.seq}>"
