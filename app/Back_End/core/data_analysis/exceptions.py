"""Custom exception hierarchy.

These are the in-process errors raised by services and repositories.
The api/ layer translates them into HTTP responses — each exception
class carries an implicit status code so the translation is one switch
in api/deps.py rather than scattered try/excepts across routes.

Design choice: we do NOT raise HTTPException from services. Services
raise domain exceptions; only the api layer knows about HTTP status
codes. This keeps services reusable (e.g. callable from a CLI or a
Celery task) without dragging FastAPI into business logic.
"""

from __future__ import annotations


class AppError(Exception):
    """Base class for all app-defined errors.

    `status_code` is the HTTP code the API layer should map this to.
    `code` is a short machine-readable string clients can switch on.
    """

    status_code: int = 500
    code: str = "internal_error"

    def __init__(self, message: str, *, code: str | None = None, status_code: int | None = None):
        super().__init__(message)
        self.message = message
        if code is not None:
            self.code = code
        if status_code is not None:
            self.status_code = status_code


# --- Auth (401) ---

class AuthenticationError(AppError):
    status_code = 401
    code = "authentication_failed"


class InvalidCredentialsError(AuthenticationError):
    code = "invalid_credentials"


class InvalidTokenError(AuthenticationError):
    code = "invalid_token"


class InvalidApiKeyError(AuthenticationError):
    code = "invalid_api_key"


# --- Authorization (403) ---

class AuthorizationError(AppError):
    status_code = 403
    code = "forbidden"


class QuotaExceededError(AuthorizationError):
    code = "quota_exceeded"


# --- Resource state (404 / 409) ---

class NotFoundError(AppError):
    status_code = 404
    code = "not_found"


class ConflictError(AppError):
    status_code = 409
    code = "conflict"


class DatasetAlreadyAttachedError(ConflictError):
    """A session already has a dataset — the one-file-per-chat rule."""

    code = "dataset_already_attached"


class DatasetNotAttachedError(AppError):
    """A message was sent before any dataset was attached to the session."""

    status_code = 409
    code = "dataset_not_attached"


# --- Input validation (400 / 413 / 415) ---

class ValidationError(AppError):
    status_code = 400
    code = "validation_error"


class UnsupportedFileTypeError(ValidationError):
    code = "unsupported_file_type"


class FileTooLargeError(AppError):
    status_code = 413
    code = "file_too_large"


class EmptyUploadError(ValidationError):
    code = "empty_upload"


# --- Upstream / pipeline (502 / 503) ---

class LLMError(AppError):
    """Ollama (or future cloud LLM) returned an error or was unreachable."""

    status_code = 502
    code = "llm_error"


class CodeExecutionError(AppError):
    """LLM-generated code failed validation or execution."""

    status_code = 422
    code = "code_execution_error"
