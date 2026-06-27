from fastapi import APIRouter
from pydantic import BaseModel
from app.Back_End.services.retrieval import search_mmr

router = APIRouter()

class SearchRequest(BaseModel):
    query: str
    company_id: str

@router.post("/")
def search(req: SearchRequest):
    docs = search_mmr(req.query, req.company_id)

    return [
        {
            "content": d.page_content,
            "metadata": d.metadata
        }
        for d in docs
    ]