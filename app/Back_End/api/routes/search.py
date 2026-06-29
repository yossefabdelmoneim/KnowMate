from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from typing import Any, List
from app.Back_End.db import models
from app.Back_End.dependencies import get_current_user, require_roles
from app.Back_End.services.retrieval import search_mmr

router = APIRouter(tags=["Search"])


class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query text", example="What is the company policy?")
    company_id: str = Field(..., description="Company ID to search within", example="company_1")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "What is the company policy?",
                "company_id": "company_1"
            }
        }


class SearchResult(BaseModel):
    content: str = Field(..., description="Document content snippet")
    metadata: dict = Field(..., description="Document metadata (source, page, etc.)")

    class Config:
        json_schema_extra = {
            "example": {
                "content": "The company policy states that...",
                "metadata": {
                    "source": "policy.pdf",
                    "page": 1
                }
            }
        }


@router.post(
    "/",
    response_model=List[SearchResult],
    summary="Search documents",
    responses={
        200: {"description": "List of search results"},
        401: {"description": "Not authenticated"},
        403: {"description": "Insufficient permissions"},
    }
)
def search(
    req: SearchRequest,
    current_user: models.User = Depends(get_current_user)
):
    """
    Search for documents in the knowledge base using semantic search.
    
    - **query**: Search query text (e.g., "company policies")
    - **company_id**: Company ID to search within
    
    Returns the most relevant documents based on the query.
    Uses MMR (Maximal Marginal Relevance) for diverse results.
    """
    docs = search_mmr(req.query, req.company_id)

    return [
        SearchResult(content=d.page_content, metadata=d.metadata)
        for d in docs
    ]