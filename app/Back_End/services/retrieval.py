from app.Back_End.db.vector_store import get_vector_store


def _build_filter(company_id: str, file_names: list[str] | None = None) -> dict:
    base = {"company_id": company_id}
    if file_names is None:
        return base
    if not file_names:
        return {"company_id": "___NO_MATCH___"}
    return {"$and": [base, {"source": {"$in": file_names}}]}


def search(query: str, company_id: str, k: int = 5, file_names: list[str] | None = None):
    db = get_vector_store()
    results = db.similarity_search(
        query,
        k=k,
        filter=_build_filter(company_id, file_names),
    )
    return results


def search_mmr(query: str, company_id: str, k: int = 5, file_names: list[str] | None = None):
    db = get_vector_store()
    results = db.max_marginal_relevance_search(
        query,
        k=k,
        fetch_k=10,
        filter=_build_filter(company_id, file_names),
    )
    return results
