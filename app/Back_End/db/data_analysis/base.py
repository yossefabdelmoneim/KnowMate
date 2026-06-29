"""Declarative base + naming convention for all ORM models.

The naming convention below is what Alembic's autogenerate relies on
to produce stable, readable migration scripts — without it, you get
random constraint names like `ck_1` that change between runs and make
migrations a nightmare to review.
"""

from __future__ import annotations

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase, registry

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """Project-wide declarative base. All models inherit from this."""

    metadata = MetaData(naming_convention=NAMING_CONVENTION)
    registry = registry()


# Importing models here would create circular imports (models import
# Base from here). Instead, the app's entry point (main.py) imports
# models.* explicitly so they register on Base.metadata before Alembic
# or `Base.metadata.create_all()` runs.
