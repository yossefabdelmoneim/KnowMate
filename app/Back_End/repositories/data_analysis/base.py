"""Base repository with shared CRUD helpers.

Subclasses set `model` and inherit get/create/delete/list for free.
Custom queries live as additional methods on the subclass.
"""

from __future__ import annotations

import uuid
from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from KnowMate.app.Back_End.db.data_analysis.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """Generic CRUD repo. `model` is set by subclasses."""

    model: type[ModelT]

    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, id: uuid.UUID) -> ModelT | None:
        return self.db.get(self.model, id)

    def add(self, instance: ModelT) -> ModelT:
        self.db.add(instance)
        self.db.flush()
        return instance

    def delete(self, instance: ModelT) -> None:
        self.db.delete(instance)
        self.db.flush()

    def list(self, *, offset: int = 0, limit: int = 50) -> list[ModelT]:
        stmt = select(self.model).offset(offset).limit(limit)
        return list(self.db.scalars(stmt).all())
