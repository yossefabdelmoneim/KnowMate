from Back_End.db import get_vector_store

def get_retriever():
    vectorstore = get_vector_store()

    return vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": 5,
            "fetch_k": 10
        }
    )