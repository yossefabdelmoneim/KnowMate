from chromadb.utils import results

from app.db.vector_store import get_vector_store

def search(query: str, company_id: str, k: int =5):
    db = get_vector_store()

    results= db.similarity_search(
        query,
        k=k,
        filter={"company_id":company_id}
    )

    return results

def search_mmr(query: str, company_id: str, k: int =5):
    db = get_vector_store()

    results= db.max_marginal_relevance_search(
        query,
        k=k,
        fetch_k=10, #candidates
        filter={"company_id":company_id}
    )

    return results