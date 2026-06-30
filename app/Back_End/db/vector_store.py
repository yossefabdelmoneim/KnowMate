import chromadb
import uuid

from langchain_huggingface import HuggingFaceEmbeddings  # Add this line
from langchain_chroma import Chroma
from app.Back_End.core.config import settings

# Initialize ChromaDB client and collection
client = chromadb.PersistentClient(path=settings.chroma_dir)
documents_collection = client.get_or_create_collection(
    "hr_documents"
)

# Initialize embedding function
_embedding_function = HuggingFaceEmbeddings(
    model_name=settings.embedding_model
)

def get_vector_store() -> Chroma:
    """
    Returns a LangChain Chroma vector store instance.
    """
    return Chroma(
        client=client,
        collection_name="hr_documents",
        embedding_function=_embedding_function,
    )

def delete_documents_by_source(
    source: str,
    company_id: str
):
    """
    Delete all chunks for the same file
    belonging to the same company.
    """

    results = documents_collection.get(
        where={
            "$and": [
                {"company_id": company_id},
                {"source": source}
            ]
        }
    )

    ids = results.get("ids", [])

    if ids:
        documents_collection.delete(ids=ids)


def add_documents(
    chunks: list[str],
    source: str,
    company_id: str
):
    """
    Store document chunks with metadata.
    If the same company uploads the same file again,
    the old chunks are removed first.
    """

    # حذف النسخة القديمة
    delete_documents_by_source(
        source=source,
        company_id=company_id
    )

    ids = []
    metadatas = []

    for i, chunk in enumerate(chunks):

        ids.append(str(uuid.uuid4()))

        metadatas.append({
            "company_id": company_id,
            "source": source,
            "chunk": i
        })

    documents_collection.add(
        documents=chunks,
        ids=ids,
        metadatas=metadatas
    )


def search_documents(
    query: str,
    company_id: str,
    n_results: int = 5
):
    """
    Search only inside documents
    belonging to one company.
    """

    results = documents_collection.query(
        query_texts=[query],
        where={
            "company_id": company_id
        },
        n_results=n_results
    )

    if not results or not results.get("documents"):
        return [], []

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    sources = list(
        {
            metadata["source"]
            for metadata in metadatas
        }
    )

    return documents, sources