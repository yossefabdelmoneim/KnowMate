from fastapi import APIRouter
from pydantic import BaseModel
from app.Back_End.services.rag_service import RAGService

router = APIRouter()


class ChatRequest(BaseModel):
    question: str
    company_id: str


@router.post("/chat")
def chat(request: ChatRequest):
    rag = RAGService()

    return rag.generate_answer(
        question=request.question,
        company_id=request.company_id
    )
