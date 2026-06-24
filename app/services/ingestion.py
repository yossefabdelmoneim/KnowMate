import uuid
from langchain_community.document_loaders import PyPDFLoader, TextLoader, Docx2txtLoader, UnstructuredExcelLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.db.vector_store import get_vector_store


def load_document(path: str):
    #Detects file type and then load it
    if path.endswith(".pdf"):
        return PyPDFLoader(path).load()
    elif path.endswith(".docx"):
        return Docx2txtLoader(path).load()
    elif path.endswith(".xlsx") or path.endswith(".xls"):
        return UnstructuredExcelLoader(path, mode="elements").load()
    else:
        return TextLoader(path).load()


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
    chunks = add_metadata(chunks, company_id)

    db = get_vector_store()
    db.add_documents(chunks)
    db.persist() #Save to disk

    return {
        "doc_id": chunks[0].metadata["doc_id"],
        "chunks": len(chunks)
    }