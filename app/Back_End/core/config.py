"""
Central application configuration.

This file is the single source of truth for the entire backend.
It combines the original KnowMate settings with the Data Analysis
module settings while remaining backward compatible.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_ROOT = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BACKEND_ROOT.parent.parent  # KnowMate/ project root


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ==========================================================
    # Application
    # ==========================================================

    app_name: str = "KnowMate"
    app_version: str = "1.0.0"

    env: Literal["dev", "staging", "prod"] = "dev"
    log_level: str = "INFO"

    host: str = "0.0.0.0"
    port: int = 8000

    base_url: str = Field(
        default="http://localhost:8000",
        alias="BASE_URL",
    )

    cors_origins: list[str] = Field(default_factory=lambda: ["*"])

    # ==========================================================
    # Database
    # ==========================================================

    database_url: str = Field(
        default="postgresql://knowmate:knowmate_password@localhost:5432/knowmate",
        alias="DATABASE_URL",
    )

    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_echo: bool = False

    # ==========================================================
    # Authentication
    # ==========================================================

    jwt_secret: SecretStr = Field(
        default=SecretStr("change_this_secret_key"),
        alias="SECRET_KEY",
    )

    jwt_algorithm: str = "HS256"

    jwt_access_token_ttl_minutes: int = Field(
        default=60,
        alias="ACCESS_TOKEN_EXPIRE_MINUTES",
    )

    verification_token_expire_minutes: int = Field(
        default=30,
        alias="VERIFICATION_TOKEN_EXPIRE_MINUTES",
    )

    api_key_prefix: str = "sk-knowmate-"
    api_key_default_quota_per_day: int = 1000

    # ==========================================================
    # Vector Database
    # ==========================================================

    chroma_dir: str = "./chroma_db"
    embedding_model: str = "all-MiniLM-L6-v2"

    # ==========================================================
    # Storage
    # ==========================================================

    data_root: Path = BACKEND_ROOT / "data"

    max_upload_size_bytes: int = 25 * 1024 * 1024

    @property
    def datasets_root(self) -> Path:
        return self.data_root / "datasets"

    def ensure_storage_dirs(self):
        self.datasets_root.mkdir(parents=True, exist_ok=True)

    # ==========================================================
    # LLM
    # ==========================================================

    llm_provider: Literal["ollama", "groq"] = "ollama"

    llm_ollama_base_url: str = "http://localhost:11434"
    llm_ollama_chat_endpoint: str = "/api/chat"
    llm_ollama_tags_endpoint: str = "/api/tags"

    groq_api_key: str = Field(default="", alias="GROQ_API_KEY")
    groq_model: str = "llama3-70b-8192"
    groq_base_url: str = "https://api.groq.com/openai/v1"

    llm_model: str = "qwen2.5:7b"

    llm_request_timeout_seconds: int = 300

    code_retry_max_attempts: int = 2

    executor_max_table_rows: int = 100

    # ==========================================================
    # Memory
    # ==========================================================

    short_term_memory_window: int = 6

    long_term_memory_enabled: bool = True

    memory_inject_top_preferences: int = 5
    memory_inject_top_memories: int = 3
    memory_min_confidence_to_inject: float = 0.5

    # ==========================================================
    # Email (SMTP)
    # ==========================================================

    smtp_host: str = Field(default="smtp.gmail.com", alias="SMTP_HOST")
    smtp_port: int = Field(default=587, alias="SMTP_PORT")
    smtp_username: str = Field(default="", alias="SMTP_USERNAME")
    smtp_password: SecretStr = Field(default=SecretStr(""), alias="SMTP_PASSWORD")
    smtp_from_email: str = Field(default="", alias="SMTP_FROM_EMAIL")
    smtp_use_tls: bool = Field(default=True, alias="SMTP_USE_TLS")

    # ==========================================================
    # Dataset Parsing
    # ==========================================================

    allowed_dataset_extensions: tuple[str, ...] = (
        ".csv",
        ".tsv",
        ".txt",
        ".xlsx",
        ".xls",
        ".ods",
        ".json",
        ".jsonl",
        ".parquet",
        ".dta",
    )

    # ==========================================================
    # Backward Compatibility
    # ==========================================================

    @property
    def DATABASE_URL(self) -> str:
        return self.database_url

    @property
    def SECRET_KEY(self) -> str:
        return self.jwt_secret.get_secret_value()

    @property
    def ALGORITHM(self) -> str:
        return self.jwt_algorithm

    @property
    def ACCESS_TOKEN_EXPIRE_MINUTES(self) -> int:
        return self.jwt_access_token_ttl_minutes

    @property
    def VERIFICATION_TOKEN_EXPIRE_MINUTES(self) -> int:
        return self.verification_token_expire_minutes

    @property
    def BASE_URL(self) -> str:
        return self.base_url

    @property
    def CHROMA_DIR(self) -> str:
        return self.chroma_dir

    @property
    def EMBEDDING_MODEL(self) -> str:
        return self.embedding_model


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_storage_dirs()
    return settings


settings = get_settings()