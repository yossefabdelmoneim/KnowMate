import chromadb
import uuid

from chromadb.utils.embedding_functions import (
    SentenceTransformerEmbeddingFunction
)

# إنشاء الـ Client
client = chromadb.PersistentClient(path="./chroma_db")

# استخدام BGE Embedding Model
embedding_function = SentenceTransformerEmbeddingFunction(
    model_name="BAAI/bge-small-en-v1.5"
)

# إنشاء الـ Collection
documents_collection = client.get_or_create_collection(
    name="hr_documents",
    embedding_function=embedding_function
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
    n_results: int = 10
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