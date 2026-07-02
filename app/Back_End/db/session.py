import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

from app.Back_End.core.config import settings

logger = logging.getLogger(__name__)

_using_fallback = False

try:
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
except Exception as e:
    logger.warning("PostgreSQL unreachable (%s). Falling back to SQLite.", e)
    _using_fallback = True
    engine = create_engine("sqlite:////tmp/knowmate.db", connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def is_using_fallback() -> bool:
    return _using_fallback