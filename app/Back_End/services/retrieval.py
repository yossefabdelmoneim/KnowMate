from app.Back_End.db.vector_store import get_vector_store


def _build_filter(company_id: str, file_names: list[str] | None = None) -> dict:
    clauses = [{"company_id": company_id}]
    if file_names:
        clauses.append({"source": {"$in": file_names}})
    if len(clauses) == 1:
        return clauses[0]
    return {"$and": clauses}


def _user_filter(results: list, user_id: str | None) -> list:
    if user_id is None:
        return results
    return [r for r in results if not r.metadata.get("user_id") or r.metadata["user_id"] == user_id]


def search(query: str, company_id: str, k: int = 5, file_names: list[str] | None = None, user_id: str | None = None):
    db = get_vector_store()
    results = db.similarity_search(
        query,
        k=k * 2,
        filter=_build_filter(company_id, file_names),
    )
    return _user_filter(results, user_id)[:k]


def search_mmr(query: str, company_id: str, k: int = 5, file_names: list[str] | None = None, user_id: str | None = None):
    db = get_vector_store()
    results = db.max_marginal_relevance_search(
        query,
        k=k * 2,
        fetch_k=20,
        filter=_build_filter(company_id, file_names),
    )
    return _user_filter(results, user_id)[:k]
