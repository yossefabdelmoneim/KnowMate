import re
import shutil
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query, Depends
from pydantic import BaseModel
from typing import Optional
from app.Back_End.db import models
from app.Back_End.db.session import get_db
from app.Back_End.dependencies import get_current_user, require_roles
from app.Back_End.services.ingestion import delete_document, ingest, replace_document

router = APIRouter(dependencies=[Depends(get_current_user)])

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".xlsx", ".xls"}


class IngestResponse(BaseModel):
    doc_id: str
    chunks: int


class DeleteResponse(BaseModel):
    doc_id: str
    deleted_chunks: int


class ReplaceResponse(BaseModel):
    doc_id: str
    chunks: int
    replaced_chunks: Optional[int] = None


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

    return UPLOAD_DIR / f"{safe_stem}{suffix}"


def save_upload(file: UploadFile) -> Path:
    file_path = safe_upload_path(file.filename)

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    return file_path


@router.post("/upload", response_model=IngestResponse, dependencies=[Depends(require_roles(["admin","manager","employee"]))])
async def upload(
    file: UploadFile = File(...),
    company_id: str = Form(...),
    current_user: models.User = Depends(get_current_user)
):
    file_path = save_upload(file)

    try:
        result = ingest(str(file_path), company_id)
    except Exception as exc:
        file_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=f"Failed to process file: {exc}") from exc


@router.delete("/{doc_id}", response_model=DeleteResponse, dependencies=[Depends(require_roles(["admin","manager"]))])
def delete(doc_id: str, company_id: str = Query(...)):
    deleted_chunks = delete_document(doc_id, company_id)

    if deleted_chunks == 0:

@router.delete("/", dependencies=[Depends(require_roles(["admin","manager"]))])
def delete(
    filename: str = Query(...),
    company_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    doc = db.query(models.Document).filter(
        models.Document.filename == filename,
        models.Document.company_id == company_id
    ).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    return DeleteResponse(doc_id=doc_id, deleted_chunks=deleted_chunks)
    deleted_chunks = delete_document(doc.doc_id, company_id)

    Path(doc.file_path).unlink(missing_ok=True)
    db.delete(doc)
    db.commit()

    return {
        "doc_id": doc.doc_id,
        "filename": doc.filename,
        "deleted_chunks": deleted_chunks
    }

@router.put("/{doc_id}", response_model=ReplaceResponse, dependencies=[Depends(require_roles(["admin","manager"]))])

@router.put("/", dependencies=[Depends(require_roles(["admin","manager"]))])
async def update(
    filename: str = Query(...),
    company_id: str = Query(...),
    file: UploadFile = File(...),
    company_id: str = Form(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    doc = db.query(models.Document).filter(
        models.Document.filename == filename,
        models.Document.company_id == company_id
    ).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    file_path = save_upload(file)

    try:
        result = replace_document(str(file_path), company_id, doc.doc_id)
    except Exception as exc:
        file_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=f"Failed to process file: {exc}") from exc

    if result is None:
        file_path.unlink(missing_ok=True)
        raise HTTPException(status_code=404, detail="Document not found")

    return ReplaceResponse(**result)
    Path(doc.file_path).unlink(missing_ok=True)

    doc.filename = file.filename
    doc.file_path = str(file_path)
    doc.chunks = result["chunks"]
    db.commit()

    return result
