"""Chat session routes — full chat lifecycle (REST only, no SSE/WS).

Endpoints:
    POST   /sessions                       create a new chat
    GET    /sessions                       list user's chats
    GET    /sessions/{id}                  get one chat (with dataset info)
    PATCH  /sessions/{id}                  update title/description/close
    DELETE /sessions/{id}                  delete a chat
    POST   /sessions/{id}/dataset          attach a dataset (one-file-per-chat)
    GET    /sessions/{id}/messages         list messages in a chat
    POST   /sessions/{id}/messages         send a message → agent runs analysis
"""

from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.Back_End.api.deps import get_current_user
from app.Back_End.core.data_analysis.exceptions import EmptyUploadError, ValidationError
from app.Back_End.db.session import get_db
from app.Back_End.models.data_analysis.user import User
from app.Back_End.repositories.data_analysis.session_repository import SessionRepository
from app.Back_End.schemas.data_analysis.dataset import DatasetPublic, DatasetUploadResponse, SupportedFileTypesResponse
from app.Back_End.schemas.data_analysis.message import (
    AnalyzeResponse, MessageCreateRequest, MessageListResponse, MessagePublic,
    ReportCreateRequest, ReportResponse,
)
from app.Back_End.schemas.data_analysis.session import SessionCreateRequest, SessionListResponse, SessionPublic, SessionUpdateRequest
from app.Back_End.services.data_analysis.analyst_agent import AnalystAgent
from app.Back_End.services.data_analysis.dataset_service import DatasetService
from app.Back_End.services.data_analysis.dataset_loader import get_supported_extensions
from app.Back_End.services.data_analysis.session_service import SessionService
from app.Back_End.services.data_analysis.report_service import ReportService
from app.Back_End.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sessions", tags=["sessions"])


# --- Session CRUD ---------------------------------------------------------

@router.post("", response_model=SessionPublic, status_code=status.HTTP_201_CREATED)
def create_session(
    request: SessionCreateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> SessionPublic:
    session = SessionService(db).create(user_id=user.id, request=request)
    return SessionService.to_public(session, message_count=0)


@router.get("", response_model=SessionListResponse)
def list_sessions(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> SessionListResponse:
    service = SessionService(db)
    sessions, total = service.list_for_user(user_id=user.id, offset=offset, limit=limit)
    items = [
        SessionService.to_public(
            s,
            message_count=SessionRepository(db).message_count(s.id),
        )
        for s in sessions
    ]
    return SessionListResponse(items=items, total=total)


@router.get("/{session_id}", response_model=SessionPublic)
def get_session(
    session_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> SessionPublic:
    service = SessionService(db)
    session = service.get_for_user(user_id=user.id, session_id=session_id)
    message_count = SessionRepository(db).message_count(session.id)
    return SessionService.to_public(session, message_count=message_count)


@router.patch("/{session_id}", response_model=SessionPublic)
def update_session(
    session_id: uuid.UUID,
    request: SessionUpdateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> SessionPublic:
    service = SessionService(db)
    session = service.update(user_id=user.id, session_id=session_id, request=request)
    message_count = SessionRepository(db).message_count(session.id)
    return SessionService.to_public(session, message_count=message_count)


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(
    session_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    SessionService(db).delete(user_id=user.id, session_id=session_id)


# --- Dataset attach (one-file-per-chat) -----------------------------------

@router.post(
    "/{session_id}/dataset",
    response_model=DatasetUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def attach_dataset(
    session_id: uuid.UUID,
    file: UploadFile = File(..., description="Dataset file (CSV, XLSX, JSON, Parquet, etc.)"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> DatasetUploadResponse:
    if not file.filename:
        raise ValidationError("Uploaded file must have a filename.")

    file_bytes = await file.read()
    service = DatasetService(db)
    dataset = service.attach_to_session(
        user_id=user.id,
        session_id=session_id,
        filename=file.filename,
        content_type=file.content_type,
        file_bytes=file_bytes,
    )
    return DatasetUploadResponse(
        dataset=DatasetService.to_public(dataset),
        session_id=session_id,
    )


@router.get("/_meta/supported-types", response_model=SupportedFileTypesResponse)
def supported_types() -> SupportedFileTypesResponse:
    """List supported dataset file extensions + max size. Useful for UI hints."""
    return SupportedFileTypesResponse(
        extensions=list(get_supported_extensions()),
        max_size_bytes=settings.max_upload_size_bytes,
        description=(
            "Supported formats: CSV, TSV, plain text, Excel (XLSX/XLS), "
            "OpenDocument (ODS), JSON, JSON Lines, Parquet, Stata (.dta)."
        ),
    )


# --- Messages + agent invocation ------------------------------------------

@router.get("/{session_id}/messages", response_model=MessageListResponse)
def list_messages(
    session_id: uuid.UUID,
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> MessageListResponse:
    # Verify ownership first.
    SessionService(db).get_for_user(user_id=user.id, session_id=session_id)

    from app.Back_End.repositories.data_analysis.message_repository import MessageRepository
    repo = MessageRepository(db)
    items, total = repo.list_for_session(session_id, offset=offset, limit=limit)
    return MessageListResponse(
        items=[MessagePublic.model_validate(m) for m in items],
        total=total,
    )


@router.post("/{session_id}/messages", response_model=AnalyzeResponse)
def send_message(
    session_id: uuid.UUID,
    request: MessageCreateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> AnalyzeResponse:
    """Send a question to the analyst agent and get a structured analysis back."""
    session_service = SessionService(db)
    session = session_service.get_for_user(user_id=user.id, session_id=session_id)
    session_service.ensure_open(session)

    agent = AnalystAgent(db)
    return agent.analyze(
        user_id=user.id,
        session_id=session_id,
        request=request,
    )


# --- Report generation (multi-section) ------------------------------------

@router.post("/{session_id}/reports", response_model=ReportResponse)
def generate_report(
    session_id: uuid.UUID,
    request: ReportCreateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ReportResponse:
    """Generate a full multi-section report.

    This is the heavy operation: ~19 LLM calls for a 5-section report
    (1 outline + 5×(code-gen + insight) + 5 section summaries + 1
    assembly + 2 memory extraction). Expect 1-3 minutes of wall time.

    The report is persisted as a single assistant Message with the
    full ReportResponse structure stored as JSON in `meta`.
    """
    session_service = SessionService(db)
    session = session_service.get_for_user(user_id=user.id, session_id=session_id)
    session_service.ensure_open(session)

    service = ReportService(db)
    return service.generate(
        user_id=user.id,
        session_id=session_id,
        request=request,
    )
