from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Any, List
from app.Back_End.services.retrieval import search_mmr
from app.Back_End.dependencies import get_current_user, require_roles

router = APIRouter(dependencies=[Depends(get_current_user)])

class SearchRequest(BaseModel):
    query: str
    company_id: str

class SearchResult(BaseModel):
    content: str
    metadata: dict

@router.post("/", response_model=List[SearchResult], dependencies=[Depends(require_roles(["admin","manager","employee"]))])
def search(req: SearchRequest):
    docs = search_mmr(req.query, req.company_id)

    return [
        SearchResult(content=d.page_content, metadata=d.metadata)
        for d in docs
    ]