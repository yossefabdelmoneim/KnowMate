"""DatasetService — handles file upload, on-disk storage, and profile caching.

Enforces:
- File extension whitelist (delegates to dataset_loader).
- Max upload size (from settings).
- "One file per chat" rule — a session can have at most one dataset.

The on-disk layout is:
    <data_root>/datasets/<user_id>/<session_id>/<original_filename>

User/session IDs in the path prevent cross-user filename collisions and
make per-user cleanup trivial (rm -rf datasets/<user_id>).
"""

from __future__ import annotations

import logging
import uuid
from pathlib import Path

import pandas as pd
from sqlalchemy.orm import Session

from app.Back_End.core.config import settings
from app.Back_End.core.data_analysis.exceptions import (
    ConflictError, DatasetAlreadyAttachedError, EmptyUploadError,
    FileTooLargeError, NotFoundError, UnsupportedFileTypeError, ValidationError,
)
from app.Back_End.models.data_analysis.dataset import Dataset as DatasetModel
from app.Back_End.repositories.data_analysis.dataset_repository import DatasetRepository
from app.Back_End.repositories.data_analysis.session_repository import SessionRepository
from app.Back_End.schemas.data_analysis.dataset import DatasetPublic
from app.Back_End.schemas.data_analysis.message import DatasetProfile
from app.Back_End.services.data_analysis.dataset_loader import is_extension_supported, load_dataset
from app.Back_End.services.data_analysis.dataset_profiler import build_dataset_profile

logger = logging.getLogger(__name__)


class DatasetService:
    """Upload, store, and profile datasets for chat sessions."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = DatasetRepository(db)
        self.session_repo = SessionRepository(db)

    # --- Upload / attach ---------------------------------------------------

    def attach_to_session(
        self,
        *,
        user_id: uuid.UUID,
        session_id: uuid.UUID,
        filename: str,
        content_type: str | None,
        file_bytes: bytes,
    ) -> DatasetModel:
        """Upload a file and attach it to a chat session (one-file-per-chat)."""
        # Verify the session exists and belongs to the user.
        session = self.session_repo.get_for_user(session_id, user_id)
        if session is None:
            raise NotFoundError(f"Session {session_id} not found for user {user_id}.")

        # Enforce the one-file-per-chat rule.
        if self.repo.has_dataset(session_id):
            raise DatasetAlreadyAttachedError(
                "This chat already has a dataset. Open a new chat to analyze a different file."
            )

        # Validate the upload itself.
        if not filename:
            raise ValidationError("Uploaded file must have a filename.")
        if not file_bytes:
            raise EmptyUploadError("Uploaded file is empty.")
        if len(file_bytes) > settings.max_upload_size_bytes:
            raise FileTooLargeError(
                f"File exceeds the {settings.max_upload_size_bytes // (1024 * 1024)}MB limit."
            )
        if not is_extension_supported(filename):
            raise UnsupportedFileTypeError(
                f"File type for '{filename}' is not supported. "
                f"Allowed: {', '.join(settings.allowed_dataset_extensions)}"
            )

        # Parse + profile BEFORE writing to disk — if parsing fails we
        # don't want to leave orphan files behind.
        try:
            df = load_dataset(file_bytes, filename)
        except ValueError as exc:
            raise UnsupportedFileTypeError(str(exc)) from exc

        profile = build_dataset_profile(df)

        # Write to disk.
        storage_path = self._build_storage_path(user_id, session_id, filename)
        storage_path.parent.mkdir(parents=True, exist_ok=True)
        storage_path.write_bytes(file_bytes)

        # Persist metadata + cached profile.
        ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        dataset = DatasetModel(
            session_id=session_id,
            original_filename=filename,
            file_extension=ext,
            content_type=content_type,
            size_bytes=len(file_bytes),
            storage_path=str(storage_path),
            row_count=profile.row_count,
            column_count=profile.column_count,
            profile_json=profile.model_dump(mode="json"),
        )
        self.repo.add(dataset)
        self.db.commit()
        self.db.refresh(dataset)

        logger.info(
            "Attached dataset %s (%d rows, %d cols) to session %s",
            filename, profile.row_count, profile.column_count, session_id,
        )
        return dataset

    # --- Read --------------------------------------------------------------

    def get_for_session(
        self,
        *,
        user_id: uuid.UUID,
        session_id: uuid.UUID,
    ) -> DatasetModel:
        """Get the dataset attached to a session. Raises NotFoundError if missing."""
        session = self.session_repo.get_for_user(session_id, user_id)
        if session is None:
            raise NotFoundError(f"Session {session_id} not found for user {user_id}.")

        dataset = self.repo.get_for_session(session_id)
        if dataset is None:
            raise NotFoundError(f"Session {session_id} has no dataset attached.")
        return dataset

    def load_dataframe(self, dataset: DatasetModel) -> pd.DataFrame:
        """Re-load the DataFrame from disk for analysis."""
        path = Path(dataset.storage_path)
        if not path.exists():
            raise NotFoundError(
                f"Dataset file '{dataset.original_filename}' is missing from disk."
            )
        return load_dataset(path.read_bytes(), dataset.original_filename)

    def get_cached_profile(self, dataset: DatasetModel) -> DatasetProfile:
        """Parse the cached DatasetProfile JSON back into a Pydantic model."""
        if dataset.profile_json is None:
            # Fallback: profile wasn't cached (e.g. legacy row). Re-build it.
            df = self.load_dataframe(dataset)
            return build_dataset_profile(df)
        return DatasetProfile.model_validate(dataset.profile_json)

    # --- Public schema mapping --------------------------------------------

    @staticmethod
    def to_public(dataset: DatasetModel) -> DatasetPublic:
        return DatasetPublic.model_validate(dataset)

    # --- Internals ---------------------------------------------------------

    def _build_storage_path(
        self,
        user_id: uuid.UUID,
        session_id: uuid.UUID,
        filename: str,
    ) -> Path:
        """On-disk path for an uploaded file.

        Sanitizes the filename (keeps only the extension + a short uuid
        prefix) to avoid path traversal and filesystem-illegal chars.
        """
        ext = ""
        if "." in filename:
            ext = "." + filename.rsplit(".", 1)[-1].lower()
        # Don't trust user-supplied filenames on disk — replace with
        # a stable, unique name. Original filename is preserved in DB.
        safe_name = f"{uuid.uuid4().hex[:12]}{ext}"
        return settings.datasets_root / str(user_id) / str(session_id) / safe_name
