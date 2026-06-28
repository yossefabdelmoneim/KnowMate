import uuid
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader, UnstructuredExcelLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.Back_End.db.vector_store import get_vector_store


def load_document(path: str):
    #Detects file type and then load it
    suffix = path.lower()

    if suffix.endswith(".pdf"):
        return PyPDFLoader(path).load()
    elif suffix.endswith(".docx"):
        return Docx2txtLoader(path).load()
    elif suffix.endswith(".xlsx") or suffix.endswith(".xls"):
        return UnstructuredExcelLoader(path, mode="elements").load()
    elif suffix.endswith(".txt"):
        return TextLoader(path).load()

    raise ValueError(f"Unsupported file type: {path}")


def split_docs(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )
    return splitter.split_documents(docs)


def add_metadata(chunks, company_id, doc_id=None):
    doc_id = doc_id or str(uuid.uuid4()) # Generate a unique document ID

    for i, c in enumerate(chunks):
        c.metadata.update({
            "doc_id": doc_id, #All chunks from the same document get the same ID
            "chunk_id": i,
            "company_id": company_id
        })

    return chunks


def build_chunks(path: str, company_id: str, doc_id: str | None = None):
    docs = load_document(path)
    chunks = split_docs(docs)

    if not chunks:
        raise ValueError("Document did not contain any readable text.")

    return add_metadata(chunks, company_id, doc_id)


def add_chunks(chunks):
    db = get_vector_store()
    db.add_documents(chunks)

    return {
        "doc_id": chunks[0].metadata["doc_id"],
        "chunks": len(chunks)
    }


def ingest(path: str, company_id: str, doc_id: str | None = None):
    chunks = build_chunks(path, company_id, doc_id)
    return add_chunks(chunks)


def get_document_chunk_ids(doc_id: str, company_id: str | None = None):
    db = get_vector_store()
    where = {"doc_id": doc_id}
    result = db.get(where=where, include=["metadatas"])

    ids = result.get("ids", [])
    metadatas = result.get("metadatas", [])

    if company_id is not None:
        ids = [
            chunk_id
            for chunk_id, metadata in zip(ids, metadatas)
            if metadata.get("company_id") == company_id
        ]

    return ids


def delete_chunk_ids(ids):
    if not ids:
        return 0

    db = get_vector_store()
    db.delete(ids=ids)
    return len(ids)


def delete_document(doc_id: str, company_id: str | None = None):
    ids = get_document_chunk_ids(doc_id, company_id)
    return delete_chunk_ids(ids)


def replace_document(path: str, company_id: str, doc_id: str):
    old_ids = get_document_chunk_ids(doc_id, company_id)

    if not old_ids:
        return None

    chunks = build_chunks(path, company_id, doc_id)
    result = add_chunks(chunks)
    result["replaced_chunks"] = delete_chunk_ids(old_ids)

    return result
