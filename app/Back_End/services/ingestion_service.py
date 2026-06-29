import os

from app.Back_End.loaders.txt_loader import load_txt
from app.Back_End.loaders.pdf_loader import load_pdf
from app.Back_End.loaders.docx_loader import load_docx
from app.Back_End.loaders.excel_loader import load_excel
from app.Back_End.loaders.jsonl_loader import load_jsonl

from app.Back_End.services.chunking import chunk_text
from app.Back_End.db.vector_store import add_documents


def ingest_file(
    file_path: str,
    company_id: str
):
    """
    Read a single file, split it into chunks,
    then store the chunks in ChromaDB.
    """

    extension = os.path.splitext(file_path)[1].lower()

    source = os.path.basename(file_path)

    # -------- TXT --------
    if extension == ".txt":

        text = load_txt(file_path)
        chunks = chunk_text(text)

    # -------- PDF --------
    elif extension == ".pdf":

        text = load_pdf(file_path)
        chunks = chunk_text(text)

    # -------- DOCX --------
    elif extension == ".docx":

        text = load_docx(file_path)
        chunks = chunk_text(text)

    # -------- Excel --------
    elif extension in [".xlsx", ".xls"]:

        text = load_excel(file_path)
        chunks = chunk_text(text)

    # -------- JSONL --------
    elif extension == ".jsonl":

        # كل Question/Answer يعتبر Document مستقل
        chunks = load_jsonl(file_path)

    else:

        raise ValueError(f"Unsupported file type: {extension}")

    # تخزين الـ Chunks مع company_id
    add_documents(
        chunks=chunks,
        source=source,
        company_id=company_id
    )

    return {
        "status": "success",
        "message": "File uploaded and indexed successfully.",
        "company_id": company_id,
        "source": source,
        "chunks": len(chunks)
    }


def ingest_folder(
    folder_path: str,
    company_id: str
):
    """
    Read all supported files inside a folder
    and store them in ChromaDB.
    """

    results = []

    supported_extensions = (
        ".txt",
        ".pdf",
        ".docx",
        ".xlsx",
        ".xls",
        ".jsonl"
    )

    for file_name in os.listdir(folder_path):

        if file_name.lower().endswith(supported_extensions):

            file_path = os.path.join(folder_path, file_name)

            result = ingest_file(
                file_path=file_path,
                company_id=company_id
            )

            results.append(result)

    return results