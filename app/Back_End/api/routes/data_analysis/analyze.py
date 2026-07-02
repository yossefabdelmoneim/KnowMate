"""Backwards-compatible standalone /analyze endpoint.

Mirrors the original standalone KnowMate API: one POST, file + question
in, analysis out. Useful for:
- Quick testing without setting up sessions.
- Keeping existing scripts that hit the old /analyze working.
- Programmatic API key consumers who don't want chat state.

Behind the scenes this creates an ephemeral session + dataset, runs the
agent, and returns the response. The session is NOT closed (callers who
want to follow up can list sessions and find it by the returned
session_id).

When authenticated via API key, the session is owned by the API key's
user. When authenticated via JWT, the session is owned by the JWT user.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.orm import Session

from app.Back_End.dependencies import get_current_user
from app.Back_End.core.config import settings
from app.Back_End.core.data_analysis.exceptions import ValidationError
from app.Back_End.db.session import get_db
from app.Back_End.db.models import User
from app.Back_End.schemas.data_analysis.message import AnalyzeResponse, MessageCreateRequest
from app.Back_End.schemas.data_analysis.session import SessionCreateRequest
from app.Back_End.services.data_analysis.analyst_agent import AnalystAgent
from app.Back_End.services.data_analysis.dataset_service import DatasetService
from app.Back_End.services.data_analysis.session_service import SessionService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["analyze"])


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(
    file: UploadFile = File(..., description="Dataset file"),
    question: str = Form(..., description="Natural-language question about the dataset"),
    debug: bool = Form(False, description="Include NLU debug fields in the response."),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> AnalyzeResponse:
    """Run the analyst agent on an uploaded file + question.

    Creates an ephemeral session + dataset under the authenticated user.
    """
    if not question or not question.strip():
        raise ValidationError("Question must not be empty.")
    if not file.filename:
        raise ValidationError("Uploaded file must have a filename.")

    file_bytes = await file.read()

    # Create the ephemeral session.
    session = SessionService(db).create(
        user_id=user.id,
        request=SessionCreateRequest(
            title=f"Standalone /analyze — {file.filename}",
            description="Ephemeral session created by the /analyze endpoint.",
        ),
    )

    # Attach the dataset (enforces one-file-per-chat, which is always
    # satisfied here since this is a brand-new session).
    DatasetService(db).attach_to_session(
        user_id=user.id,
        session_id=session.id,
        filename=file.filename,
        content_type=file.content_type,
        file_bytes=file_bytes,
    )

    # Run the agent.
    agent = AnalystAgent(db)
    return agent.analyze(
        user_id=user.id,
        session_id=session.id,
        request=MessageCreateRequest(question=question, debug=debug),
    )
