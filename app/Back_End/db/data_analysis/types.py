"""Portable JSON type for SQLAlchemy columns.

Uses PostgreSQL's JSONB (binary JSON, supports GIN indexes + JSON
operators) when available, falls back to plain JSON on other backends
(e.g. SQLite for local dev / tests).

Usage:
    from db.types import JSONB
    meta: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
"""

from __future__ import annotations

from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import JSONB as PG_JSONB
from sqlalchemy.types import TypeDecorator


class JSONB(TypeDecorator):
    """Platform-independent JSON type.

    Renders as JSONB on PostgreSQL (for native JSON indexing / queries)
    and as plain JSON elsewhere. This lets the same models work on both
    Postgres (production) and SQLite (local dev / tests) without a
    separate test-only model set.
    """

    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):  # type: ignore[override]
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_JSONB())
        return dialect.type_descriptor(JSON())
