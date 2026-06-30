"""Data-analysis Base alias.

Option A keeps a single SQLAlchemy Base across the whole project so the
legacy and data-analysis tables are created together.
"""

from app.Back_End.db.session import Base

__all__ = ["Base"]
