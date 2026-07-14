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
from app.Back_End.services.data_analysis.chart_generator import auto_generate_chart
from app.Back_End.prompts.data_analysis.nlu.intent_detector import detect_intents
from app.Back_End.schemas.data_analysis.message import Intent
from app.Back_End.core.config import settings
from app.Back_End.core.llm import get_llm_client
from pathlib import Path
import uuid, os, io
from datetime import datetime, timezone
import pandas as pd

router = APIRouter(tags=["Chat"])

UPLOAD_DIR = Path("uploads")


def _is_data_file(filename: str) -> bool:
    return filename.lower().endswith((".csv", ".xlsx", ".xls"))


def _find_file_bytes(original_name: str) -> bytes | None:
    """Find a previously-uploaded file by its original name in the uploads directory."""
    if not UPLOAD_DIR.is_dir():
        return None
    for f in UPLOAD_DIR.iterdir():
        if f.name.endswith(f"_{original_name}") or f.name == original_name:
            return f.read_bytes()
    return None


def _run_data_analysis(question: str, file_bytes: bytes, filename: str) -> dict:
    """Load a CSV/XLSX file, use the LLM to analyze it, and auto-generate a chart."""
    ext = os.path.splitext(filename)[1].lower()
    try:
        if ext == ".csv":
            df = pd.read_csv(io.BytesIO(file_bytes))
        elif ext in (".xlsx", ".xls"):
            df = pd.read_excel(io.BytesIO(file_bytes))
        else:
            return {"answer": f"Unsupported file type: {ext}.", "sources": []}
    except Exception as exc:
        return {"answer": f"Could not read {filename}: {exc}", "sources": []}

    if df.empty:
        return {"answer": f"{filename} is empty.", "sources": []}

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    info_lines = [
        f"**Dataset**: {filename} — {len(df):,} rows × {len(df.columns)} columns",
        f"**Columns**: {', '.join(df.columns.tolist())}",
    ]
    if numeric_cols:
        info_lines.append(f"**Numeric columns**: {', '.join(numeric_cols[:10])}")
    info_lines.append(f"\n**Preview (first 5 rows):**\n```\n{df.head(5).to_string()}\n```")
    dataset_info = "\n".join(info_lines)

    llm = get_llm_client()
    prompt = (
        "You are a data analyst. Given the dataset description below and the "
        "user's question, provide a clear, insightful analysis. Include specific "
        "numbers, trends, and comparisons.\n\n"
        f"{dataset_info}\n\n"
        f"**User question**: {question}"
    )
    try:
        answer = llm.chat(user_prompt=prompt, model=settings.llm_model)
    except Exception as exc:
        answer = f"Note: LLM analysis unavailable ({exc}). Showing raw data preview.\n\n{dataset_info}"

    # Auto-generate a chart from the data.
    try:
        intent_values = detect_intents(question)
        intent_strs = list(intent_values)
        table_records = df.head(100).to_dict(orient="records")
        chart = auto_generate_chart(table_records, intent_strs, question)
        if chart and chart.data:
            answer += f'<br><br><img src="data:image/png;base64,{chart.data}" style="max-width:100%;height:auto;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.15)" alt="chart"/>'
    except Exception:
        pass

    return {"answer": answer, "sources": []}


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
            user_id=str(current_user.id),
        )
    elif request.agent_type == "general" and any(_is_data_file(f) for f in effective_files):
        data_files = [f for f in effective_files if _is_data_file(f)]
        file_bytes = _find_file_bytes(data_files[0])
        if file_bytes:
            result = _run_data_analysis(request.question, file_bytes, data_files[0])
        else:
            prompt_type = "general"
            rag = RAGService(prompt_type=prompt_type)
            result = rag.generate_answer(
                question=request.question,
                company_id=request.company_id,
                files=effective_files,
                user_id=str(current_user.id),
            )
    else:
        prompt_type = request.agent_type if request.agent_type in ("marketing",) else "general"
        rag = RAGService(prompt_type=prompt_type)
        result = rag.generate_answer(
            question=request.question,
            company_id=request.company_id,
            files=effective_files,
            user_id=str(current_user.id),
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
