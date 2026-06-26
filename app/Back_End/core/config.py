import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    CHROMA_DIR = "./chroma_db"
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://knowmate:knowmate_password@localhost:5432/knowmate"
    )
    SECRET_KEY = os.getenv("SECRET_KEY", "change_this_secret_key")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))


settings = Settings()
