import uuid
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.db.vector_store import get_vector_store


def load_document(path: str):
    if path.endswith(".pdf"):
        return PyPDFLoader(path).load()
    elif path.endswith(".docx"):
        return Docx2txtLoader(path).load()
    else:
        return TextLoader(path).load()


def split_docs(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )
    return splitter.split_documents(docs)


def add_metadata(chunks, company_id):
    doc_id = str(uuid.uuid4())

    for i, c in enumerate(chunks):
        c.metadata.update({
            "doc_id": doc_id,
            "chunk_id": i,
            "company_id": company_id
        })

    return chunks


def ingest(path: str, company_id: str):
    docs = load_document(path)
    chunks = split_docs(docs)
    chunks = add_metadata(chunks, company_id)

    db = get_vector_store()
    db.add_documents(chunks)
    db.persist()

    return {
        "doc_id": chunks[0].metadata["doc_id"],
        "chunks": len(chunks)
    }