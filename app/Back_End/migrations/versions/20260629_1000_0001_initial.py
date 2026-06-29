"""Initial schema — creates all tables for the current model set.

Revision ID: 0001_initial
Revises:
Create Date: 2026-06-29 10:00:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# Use the portable JSON type that renders as JSONB on Postgres, JSON on
# SQLite/other backends — keeps models + migrations consistent.
from KnowMate.app.Back_End.db.data_analysis.types import JSONB

# revision identifiers, used by Alembic.
revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- users ---
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("is_admin", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # --- chat_sessions ---
    op.create_table(
        "chat_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False, server_default="New chat"),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_chat_sessions_user_id", "chat_sessions", ["user_id"])

    # --- datasets ---
    op.create_table(
        "datasets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("session_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("chat_sessions.id", ondelete="CASCADE"),
                  nullable=False, unique=True),
        sa.Column("original_filename", sa.String(512), nullable=False),
        sa.Column("file_extension", sa.String(16), nullable=False),
        sa.Column("content_type", sa.String(128), nullable=True),
        sa.Column("size_bytes", sa.Integer, nullable=False),
        sa.Column("storage_path", sa.String(1024), nullable=False),
        sa.Column("row_count", sa.Integer, nullable=True),
        sa.Column("column_count", sa.Integer, nullable=True),
        sa.Column("profile_json", JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_datasets_session_id", "datasets", ["session_id"], unique=True)

    # --- messages ---
    op.create_table(
        "messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("session_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("seq", sa.Integer, nullable=False, server_default="0"),
        sa.Column("role", sa.String(32), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("meta", JSONB, nullable=True),
        sa.Column("processing_time_seconds", sa.Float, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_messages_session_id", "messages", ["session_id"])

    # --- api_keys ---
    op.create_table(
        "api_keys",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("key_prefix", sa.String(32), nullable=False),
        sa.Column("key_hash", sa.String(128), nullable=False),
        sa.Column("quota_per_day", sa.Integer, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_api_keys_user_id", "api_keys", ["user_id"])
    op.create_index("ix_api_keys_key_prefix", "api_keys", ["key_prefix"], unique=True)
    op.create_index("ix_api_keys_key_hash", "api_keys", ["key_hash"], unique=True)

    # --- user_preferences (long-term memory stub) ---
    op.create_table(
        "user_preferences",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("category", sa.String(64), nullable=False),
        sa.Column("key", sa.String(128), nullable=False),
        sa.Column("value", sa.Text, nullable=False),
        sa.Column("confidence", sa.Float, nullable=False, server_default="0.5"),
        sa.Column("last_confirmed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("source_session_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("chat_sessions.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_user_preferences_user_id", "user_preferences", ["user_id"])
    op.create_index("ix_user_preferences_category", "user_preferences", ["category"])

    # --- long_term_memories (long-term memory stub) ---
    op.create_table(
        "long_term_memories",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("kind", sa.String(64), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("importance", sa.Float, nullable=False, server_default="0.5"),
        sa.Column("meta", JSONB, nullable=True),
        sa.Column("source_session_id", postgresql.UUID(as_uuid=True),
                  sa.ForeignKey("chat_sessions.id", ondelete="SET NULL"), nullable=True),
        sa.Column("last_accessed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_long_term_memories_user_id", "long_term_memories", ["user_id"])
    op.create_index("ix_long_term_memories_kind", "long_term_memories", ["kind"])


def downgrade() -> None:
    op.drop_table("long_term_memories")
    op.drop_table("user_preferences")
    op.drop_table("api_keys")
    op.drop_table("messages")
    op.drop_table("datasets")
    op.drop_table("chat_sessions")
    op.drop_table("users")
