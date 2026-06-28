import os
from fastapi import APIRouter, UploadFile, File, Form, Depends
from sqlalchemy.orm import Session

from app.db import models
from app.db.session import get_db
from app.dependencies import get_current_user
from app.services.ingestion import ingest

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
async def upload(
    file: UploadFile = File(...),
    company_id: str = Form(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    result = ingest(file_path, company_id)

    doc = models.Document(
        user_id=current_user.id,
        company_id=company_id,
        filename=file.filename,
        file_path=file_path,
        doc_id=result["doc_id"],
        chunks=result["chunks"],
    )
    db.add(doc)
    db.commit()

    return result