from app.Back_End.db.vector_store import get_vector_store


def _build_filter(company_id: str, file_names: list[str] | None = None, user_id: str | None = None) -> dict:
    clauses = [{"company_id": company_id}]
    if user_id is not None:
        clauses.append({"user_id": user_id})
    if file_names:
        clauses.append({"source": {"$in": file_names}})
    if len(clauses) == 1:
        return clauses[0]
    return {"$and": clauses}


def search(query: str, company_id: str, k: int = 5, file_names: list[str] | None = None, user_id: str | None = None):
    db = get_vector_store()
    results = db.similarity_search(
        query,
        k=k,
        filter=_build_filter(company_id, file_names, user_id),
    )
    return results


def search_mmr(query: str, company_id: str, k: int = 5, file_names: list[str] | None = None, user_id: str | None = None):
    db = get_vector_store()
    results = db.max_marginal_relevance_search(
        query,
        k=k,
        fetch_k=10,
        filter=_build_filter(company_id, file_names, user_id),
    )
    return results
