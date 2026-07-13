import uuid

from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from app.Back_End.core.config import settings


_embedding_function = HuggingFaceEmbeddings(
    model_name=settings.embedding_model
)


def get_vector_store() -> Chroma:
    return Chroma(
        collection_name="hr_documents",
        embedding_function=_embedding_function,
        persist_directory=settings.chroma_dir,
    )


def _build_where(company_id: str, file_names: list[str] | None = None) -> dict:
    if not file_names:
        return {"company_id": company_id}
    return {"$and": [{"company_id": company_id}, {"source": {"$in": file_names}}]}


def delete_documents_by_source(source: str, company_id: str):
    db = get_vector_store()
    existing = db.get(where={"$and": [{"company_id": company_id}, {"source": source}]})
    ids = existing.get("ids", [])
    if ids:
        db.delete(ids=ids)


def add_documents(chunks: list[str], source: str, company_id: str):
    delete_documents_by_source(source=source, company_id=company_id)
    docs = [
        Document(
            page_content=chunk,
            metadata={"company_id": company_id, "source": source, "chunk": i},
        )
        for i, chunk in enumerate(chunks)
    ]
    db = get_vector_store()
    db.add_documents(docs)


def search_documents(
    query: str,
    company_id: str,
    n_results: int = 5,
    file_names: list[str] | None = None,
):
    db = get_vector_store()
    where = _build_where(company_id, file_names)
    docs = db.similarity_search(query, k=n_results, filter=where)
    if not docs:
        return [], []
    sources = list({d.metadata.get("source", "") for d in docs})
    return [d.page_content for d in docs], sources