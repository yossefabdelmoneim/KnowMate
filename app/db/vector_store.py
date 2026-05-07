from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from app.core.config import settings

# Cache embedding (avoid reloading model every time)
_embedding = None

def get_embedding():
    global _embedding

    if _embedding is None:
        _embedding = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL
        )

    return _embedding


def get_vector_store(collection_name: str = "documents") :
    return Chroma(
        persist_directory=settings.CHROMA_DIR,
        embedding_function=get_embedding(),
        collection_name=collection_name
    )