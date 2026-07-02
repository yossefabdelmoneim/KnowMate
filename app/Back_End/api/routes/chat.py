from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session as DBSession
from app.Back_End.db import models
from app.Back_End.db.session import get_db
from app.Back_End.dependencies import get_current_user
from app.Back_End.services.rag_service import RAGService
from app.Back_End.services.data_analysis.session_service import SessionService
from app.Back_End.repositories.data_analysis.message_repository import MessageRepository
from app.Back_End.models.data_analysis.chat_session import ChatSession
from app.Back_End.models.data_analysis.message import Message
from app.Back_End.schemas.data_analysis.session import SessionCreateRequest
from app.Back_End.services.HR_service import ask_hr
import uuid
from datetime import datetime, timezone

router = APIRouter(tags=["Chat"])


class ChatRequest(BaseModel):
    question: str = Field(..., description="Question to ask the AI agent", example="What is the company's return policy?")
    company_id: str = Field(..., description="Company ID context", example="company_1")
    agent_type: str = Field("default", description="Type of agent to use", example="default")
    session_id: Optional[str] = Field(None, description="Session ID to persist messages (omit to create new session)")
    files: list[str] = Field(default_factory=list, description="Names of files attached to this message")

    class Config:
        json_schema_extra = {
            "example": {
                "question": "What is the company's return policy?",
                "company_id": "company_1",
                "agent_type": "default",
                "session_id": None,
                "files": []
            }
        }


class ChatResponse(BaseModel):
    answer: str = Field(..., description="AI-generated answer")
    sources: List[Dict[str, Any]] = Field(..., description="Source documents used for the answer")
    session_id: str = Field("", description="Session ID for message persistence")


def _persist_message(db: DBSession, session_id: uuid.UUID, role: str, content: str):
    repo = MessageRepository(db)
    seq = repo.next_seq(session_id)
    msg = Message(session_id=session_id, seq=seq, role=role, content=content)
    repo.add(msg)
    db.commit()


@router.post(
    "/chat",
    response_model=ChatResponse,
    summary="Chat with AI agent",
    responses={
        200: {"description": "AI response with sources"},
        401: {"description": "Not authenticated"},
        403: {"description": "Insufficient permissions"},
    }
)
def chat(
    request: ChatRequest,
    db: DBSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # ── Resolve session and its file names ──
    if request.session_id:
        session_id = uuid.UUID(request.session_id)
        session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if not session:
            session = ChatSession(
                id=session_id,
                user_id=current_user.id,
                title=request.question[:80],
            )
            db.add(session)
            db.commit()
            db.refresh(session)
        # Use stored file names, merging any new ones from this request
        existing = set(session.file_names or [])
        incoming = set(request.files or [])
        merged = sorted(existing | incoming)
        if merged != (session.file_names or []):
            session.file_names = merged
            db.commit()
        effective_files = session.file_names or []
    else:
        session = ChatSession(
            user_id=current_user.id,
            title=request.question[:80],
            file_names=request.files or None,
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        session_id = session.id
        effective_files = request.files or []

    # ── Route to the right agent ──
    if request.agent_type == "hr":
        result = ask_hr(
            company_id=request.company_id,
            question=request.question,
            files=effective_files,
        )
    else:
        prompt_type = request.agent_type if request.agent_type in ("marketing",) else "general"
        rag = RAGService(prompt_type=prompt_type)
        result = rag.generate_answer(
            question=request.question,
            company_id=request.company_id,
            files=effective_files,
        )

    _persist_message(db, session_id, "user", request.question)
    _persist_message(db, session_id, "assistant", result["answer"])

    raw_sources = result.get("sources") or result.get("source", [])
    sources_list: list[dict] = [
        {"source": s} if isinstance(s, str) else s for s in raw_sources
    ]

    return ChatResponse(
        answer=result["answer"],
        sources=sources_list,
        session_id=str(session_id),
    )
