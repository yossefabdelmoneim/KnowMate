"""Data-analysis Base alias.

Option B uses a separate SQLAlchemy Base for data-analysis models to
avoid conflicts with the legacy models.
"""

from sqlalchemy.orm import declarative_base

# Define a separate Base for data-analysis models
Base = declarative_base()

__all__ = ["Base"]