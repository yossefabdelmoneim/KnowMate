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


def add_metadata(chunks, company_id):
    doc_id = str(uuid.uuid4()) # Generate a unique document ID

    for i, c in enumerate(chunks):
        c.metadata.update({
            "doc_id": doc_id, #All chunks from the same document get the same ID
            "chunk_id": i,
            "company_id": company_id
        })

    return chunks


def ingest(path: str, company_id: str):
    docs = load_document(path)
    chunks = split_docs(docs)

    if not chunks:
        raise ValueError("Document did not contain any readable text.")

    chunks = add_metadata(chunks, company_id)

    db = get_vector_store()
    db.add_documents(chunks)

    return {
        "doc_id": chunks[0].metadata["doc_id"],
        "chunks": len(chunks)
    }
