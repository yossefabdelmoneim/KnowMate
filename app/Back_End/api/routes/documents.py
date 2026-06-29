import re
import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query, Depends
from sqlalchemy.orm import Session

from app.Back_End.db import models
from app.Back_End.db.session import get_db
from app.Back_End.dependencies import get_current_user
from app.Back_End.services.ingestion import delete_document, ingest, replace_document

router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".xlsx", ".xls"}


def safe_upload_path(filename: str) -> Path:
    original_name = Path(filename or "upload").name
    suffix = Path(original_name).suffix.lower()

    if suffix not in ALLOWED_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_EXTENSIONS))
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed extensions: {allowed}",
        )

    stem = Path(original_name).stem
    safe_stem = re.sub(r"[^A-Za-z0-9_.-]+", "_", stem).strip("._") or "upload"

    return UPLOAD_DIR / f"{uuid.uuid4().hex}_{safe_stem}{suffix}"


def save_upload(file: UploadFile) -> Path:
    file_path = safe_upload_path(file.filename)

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    return file_path


@router.post("/upload")
async def upload(
    file: UploadFile = File(...),
    company_id: str = Form(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    file_path = save_upload(file)

    try:
        result = ingest(str(file_path), company_id)
    except ValueError as exc:
        file_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    doc = models.Document(
        user_id=current_user.id,
        company_id=company_id,
        filename=file.filename,
        file_path=str(file_path),
        doc_id=result["doc_id"],
        chunks=result["chunks"],
    )
    db.add(doc)
    db.commit()

    return result


@router.delete("/{doc_id}")
def delete(
    doc_id: str,
    company_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    deleted_chunks = delete_document(doc_id, company_id)

    if deleted_chunks == 0:
        raise HTTPException(status_code=404, detail="Document not found")

    doc = db.query(models.Document).filter(models.Document.doc_id == doc_id).first()
    if doc:
        db.delete(doc)
        db.commit()

    return {
        "doc_id": doc_id,
        "deleted_chunks": deleted_chunks
    }


@router.put("/{doc_id}")
async def update(
    doc_id: str,
    file: UploadFile = File(...),
    company_id: str = Form(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    file_path = save_upload(file)

    try:
        result = replace_document(str(file_path), company_id, doc_id)
    except ValueError as exc:
        file_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if result is None:
        file_path.unlink(missing_ok=True)
        raise HTTPException(status_code=404, detail="Document not found")

    doc = db.query(models.Document).filter(models.Document.doc_id == doc_id).first()
    if doc:
        doc.filename = file.filename
        doc.file_path = str(file_path)
        doc.chunks = result["chunks"]
        db.commit()

    return result
