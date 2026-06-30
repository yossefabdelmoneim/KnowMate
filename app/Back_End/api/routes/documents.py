import re
import shutil
import uuid
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query, Depends
from pydantic import BaseModel, Field
from typing import Optional
from app.Back_End.dependencies import get_current_user, require_roles
from app.Back_End.services.ingestion import delete_document, ingest, replace_document

router = APIRouter(tags=["Documents"])

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".xlsx", ".xls"}


class IngestResponse(BaseModel):
    doc_id: str = Field(..., description="Document ID")
    chunks: int = Field(..., description="Number of chunks created")

    class Config:
        json_schema_extra = {
            "example": {
                "doc_id": "doc_12345",
                "chunks": 5
            }
        }


class DeleteResponse(BaseModel):
    doc_id: str = Field(..., description="Document ID that was deleted")
    deleted_chunks: int = Field(..., description="Number of chunks deleted")

    class Config:
        json_schema_extra = {
            "example": {
                "doc_id": "doc_12345",
                "deleted_chunks": 5
            }
        }


class ReplaceResponse(BaseModel):
    doc_id: str = Field(..., description="Document ID that was replaced")
    chunks: int = Field(..., description="Total number of chunks in new document")
    replaced_chunks: Optional[int] = Field(None, description="Number of chunks replaced")

    class Config:
        json_schema_extra = {
            "example": {
                "doc_id": "doc_12345",
                "chunks": 7,
                "replaced_chunks": 5
            }
        }

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


@router.post(
    "/upload",
    response_model=IngestResponse,
    summary="Upload and ingest a document",
    responses={
        200: {"description": "Document uploaded and processed successfully"},
        400: {"description": "Invalid file type or processing error"},
        403: {"description": "Insufficient permissions"},
    }
)
async def upload(
    file: UploadFile = File(..., description="PDF, DOCX, TXT, XLSX, or XLS file"),
    company_id: str = Form(..., description="Company ID for document organization"),
    current_user = Depends(get_current_user)
):
    """
    Upload and ingest a document for the company.
    
    - **file**: Document file (PDF, DOCX, TXT, XLSX, XLS)
    - **company_id**: Company ID to associate the document with
    
    The document will be processed and stored in the knowledge base for searching.
    """
    file_path = save_upload(file)

    try:
        return ingest(str(file_path), company_id)
    except ValueError as exc:
        file_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.delete(
    "/{doc_id}",
    response_model=DeleteResponse,
    summary="Delete a document",
    responses={
        200: {"description": "Document deleted successfully"},
        403: {"description": "Insufficient permissions (admin/manager only)"},
        404: {"description": "Document not found"},
    }
)
def delete(
    doc_id: str,
    company_id: str = Query(..., description="Company ID"),
    current_user = Depends(require_roles(["admin", "manager"]))
):
    """
    Delete a document and its chunks from the knowledge base (admin/manager only).
    
    - **doc_id**: ID of the document to delete
    - **company_id**: Company ID the document belongs to
    """
    deleted_chunks = delete_document(doc_id, company_id)

    if deleted_chunks == 0:
        raise HTTPException(status_code=404, detail="Document not found")

    return DeleteResponse(doc_id=doc_id, deleted_chunks=deleted_chunks)


@router.put(
    "/{doc_id}",
    response_model=ReplaceResponse,
    summary="Replace a document",
    responses={
        200: {"description": "Document replaced successfully"},
        403: {"description": "Insufficient permissions (admin/manager only)"},
        404: {"description": "Document not found"},
    }
)
async def update(
    doc_id: str,
    file: UploadFile = File(..., description="New document file"),
    company_id: str = Form(..., description="Company ID"),
    current_user = Depends(require_roles(["admin", "manager"]))
):
    """
    Replace an existing document with a new one (admin/manager only).
    
    - **doc_id**: ID of the document to replace
    - **file**: New document file (PDF, DOCX, TXT, XLSX, XLS)
    - **company_id**: Company ID the document belongs to
    
    The old document chunks will be replaced with new ones from the new file.
    """
    file_path = save_upload(file)

    try:
        result = replace_document(str(file_path), company_id, doc_id)
    except ValueError as exc:
        file_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if result is None:
        file_path.unlink(missing_ok=True)
        raise HTTPException(status_code=404, detail="Document not found")

    return ReplaceResponse(**result)