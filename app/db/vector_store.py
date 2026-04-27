from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from app.core.config import settings


def get_embedding():
    return HuggingFaceEmbeddings(
        model_name=settings.EMBEDDING_MODEL
    )


def get_vector_store():
    return Chroma(
        persist_directory=settings.CHROMA_DIR,
        embedding_function=get_embedding()
    )