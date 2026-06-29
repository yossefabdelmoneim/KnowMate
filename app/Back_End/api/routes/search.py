from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.Back_End.db import models
from app.Back_End.dependencies import get_current_user
from app.Back_End.services.retrieval import search_mmr

router = APIRouter()

class SearchRequest(BaseModel):
    query: str
    company_id: str

@router.post("/")
def search(req: SearchRequest, current_user: models.User = Depends(get_current_user)):
    docs = search_mmr(req.query, req.company_id)

    return [
        {
            "content": d.page_content,
            "metadata": d.metadata
        }
        for d in docs
    ]