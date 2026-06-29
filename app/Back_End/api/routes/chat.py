from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from app.Back_End.db import models
from app.Back_End.dependencies import get_current_user, require_roles
from app.Back_End.services.rag_service import RAGService

router = APIRouter(tags=["Chat"])


class ChatRequest(BaseModel):
    question: str = Field(..., description="Question to ask the AI agent", example="What is the company's return policy?")
    company_id: str = Field(..., description="Company ID context", example="company_1")
    agent_type: str = Field("default", description="Type of agent to use", example="default")

    class Config:
        json_schema_extra = {
            "example": {
                "question": "What is the company's return policy?",
                "company_id": "company_1",
                "agent_type": "default"
            }
        }


class ChatResponse(BaseModel):
    answer: str = Field(..., description="AI-generated answer")
    sources: List[Dict[str, Any]] = Field(..., description="Source documents used for the answer")

    class Config:
        json_schema_extra = {
            "example": {
                "answer": "The company's return policy allows returns within 30 days...",
                "sources": [
                    {
                        "source": "policy.pdf",
                        "page": 2,
                        "content": "..."
                    }
                ]
            }
        }


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
    current_user: models.User = Depends(get_current_user)
):
    """
    Chat with the AI agent to get answers based on company documents.
    
    - **question**: Your question about company information
    - **company_id**: Company ID for context
    - **agent_type**: Type of RAG agent to use (default, research, etc.)
    
    Returns the AI-generated answer with sources from the knowledge base.
    """
    rag = RAGService(agent_type=request.agent_type)

    return rag.generate_answer(
        question=request.question,
        company_id=request.company_id
    )
