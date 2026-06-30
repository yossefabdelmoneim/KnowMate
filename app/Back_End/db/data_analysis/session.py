"""Database session factory + FastAPI dependency.

`SessionLocal` is the engine-bound session factory. `get_db` is the
FastAPI dependency routes use to get a per-request session with proper
cleanup. Tests construct their own sessions directly against `engine`.
"""

from __future__ import annotations

import logging
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.Back_End.core.config import settings

logger = logging.getLogger(__name__)


# A single engine per process is the standard pattern — SQLAlchemy
# handles connection pooling underneath. `pool_pre_ping` avoids stale
# connections after a DB restart.
engine = create_engine(
    settings.database_url,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_pre_ping=True,
    echo=settings.db_echo,
    future=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    class_=Session,
)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency: yields a Session, rolls back on exception.

    The `finally` block ensures the session is ALWAYS returned to the
    pool even if the route handler swallows an exception. Without this
    you get connection leaks under load.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
