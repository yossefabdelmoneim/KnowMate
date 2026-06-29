from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Dict, Any
from app.Back_End.db import models
from app.Back_End.dependencies import get_current_user
from app.Back_End.services.rag_service import RAGService
from app.Back_End.dependencies import get_current_user, require_roles

router = APIRouter(dependencies=[Depends(get_current_user)])


class ChatRequest(BaseModel):
    question: str
    company_id: str
    agent_type: str = "default"


class ChatResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]


@router.post("/chat", response_model=ChatResponse, dependencies=[Depends(require_roles(["admin","manager"]))])
def chat(request: ChatRequest):
    rag = RAGService(agent_type=request.agent_type)

    return rag.generate_answer(
        question=request.question,
        company_id=request.company_id
    )
