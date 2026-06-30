"""db/ — SQLAlchemy declarative base + session factory.

Two responsibilities:
1. `Base` — the declarative base all ORM models inherit from. Naming
   convention enforced so migrations are deterministic (snake_case
   table names, ix_<table>_<col> indexes, etc.).
2. `SessionLocal` — session factory bound to the configured database
   URL. Routes use the `get_db` dependency to grab a session per
   request.
"""

from __future__ import annotations

from app.Back_End.db.data_analysis.base import Base
from app.Back_End.db.data_analysis.session import SessionLocal, get_db, engine

__all__ = ["Base", "SessionLocal", "engine", "get_db"]
