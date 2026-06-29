"""Dataset repository."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from KnowMate.app.Back_End.models.data_analysis.dataset import Dataset
from KnowMate.app.Back_End.repositories.data_analysis.base import BaseRepository


class DatasetRepository(BaseRepository[Dataset]):
    model = Dataset

    def __init__(self, db: Session) -> None:
        super().__init__(db)

    def get_for_session(self, session_id: uuid.UUID) -> Dataset | None:
        stmt = select(Dataset).where(Dataset.session_id == session_id)
        return self.db.scalars(stmt).first()

    def has_dataset(self, session_id: uuid.UUID) -> bool:
        return self.get_for_session(session_id) is not None

    def get_by_id(self, dataset_id: uuid.UUID) -> Dataset | None:
        return self.get(dataset_id)
