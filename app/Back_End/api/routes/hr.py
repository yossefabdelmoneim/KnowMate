from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException
)

import os
import shutil

from app.Back_End.schemas.HR import (
    HRRequest,
    HRResponse
)

from app.Back_End.services.HR_service import ask_hr
from app.Back_End.services.ingestion_service import ingest_file


router = APIRouter(
    prefix="/hr",
    tags=["HR"]
)


@router.post(
    "/ask",
    response_model=HRResponse
)
def ask(request: HRRequest):

    result = ask_hr(
        company_id=request.company_id,
        question=request.question
    )

    return HRResponse(
        answer=result["answer"],
        source=result["source"]
    )


@router.post("/upload")
def upload_hr_document(
    company_id: str,
    file: UploadFile = File(...)
):

    # أنواع الملفات المسموح بها
    allowed_extensions = {
        ".txt",
        ".pdf",
        ".docx",
        ".xlsx",
        ".xls",
        ".jsonl"
    }

    extension = os.path.splitext(file.filename)[1].lower()

    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type."
        )

    # إنشاء فولدر uploads إذا لم يكن موجودًا
    upload_folder = "app/Back_End/uploads"
    os.makedirs(upload_folder, exist_ok=True)

    # حفظ الملف
    file_path = os.path.join(upload_folder, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # إدخال الملف إلى ChromaDB
    result = ingest_file(
        file_path=file_path,
        company_id=company_id
    )

    return {
        "status": "success",
        "message": "File uploaded and indexed successfully.",
        "company_id": company_id,
        "source": result["source"],
        "chunks": result["chunks"]
    }