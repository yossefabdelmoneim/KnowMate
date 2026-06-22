from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.services.rag_service import RAGService
from app.dependencies import get_retriever

router = APIRouter()


class ChatRequest(BaseModel):
    question: str
    company_id: str


@router.post("/chat")
def chat(request: ChatRequest, retriever=Depends(get_retriever)):
    rag = RAGService(retriever)

    return rag.generate_answer(
        question=request.question,
        company_id=request.company_id
    )