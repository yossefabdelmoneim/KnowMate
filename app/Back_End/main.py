from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from app.Back_End.api.routes import chat, search
from app.Back_End.api.routes import documents
from app.Back_End.api.routes import auth
from app.Back_End.api.routes import companies
from app.Back_End.db.session import engine, Base
"""
Main FastAPI application.

Combines the original KnowMate backend with the Data Analysis Agent.

Features:
- Authentication
- Documents
- Search / RAG
- Chat
- Data Analysis Agent
- Session Memory
- Global exception handling
- Logging
- CORS
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
# -------------------------------
# Core
# -------------------------------

from app.Back_End.core.config import settings
from app.Back_End.core.logging import setup_logging
from app.Back_End.core.exceptions import AppError

# -------------------------------
# Database
# -------------------------------

from app.Back_End.db.session import Base, engine

# Register all SQLAlchemy models
import app.Back_End.db.models  # noqa: F401
import app.Back_End.models.data_analysis  # noqa: F401

# -------------------------------
# Original Routes
# -------------------------------

from app.Back_End.api.routes import (
    auth,
    chat,
    documents,
    search,
)

# -------------------------------
# Data Analysis Routes
# -------------------------------

from app.Back_End.api.routes.data_analysis import (
    analyze,
    health,
    memory,
    sessions,
)

# API Keys (enable later if needed)
# from app.Back_End.api.routes.data_analysis import api_keys

# ---------------------------------------------------------------------

setup_logging()

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup / Shutdown.
    """


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="KnowMate API",
    description="Knowledge Management and AI Assistant API for enterprises",
    version="1.0.0",
    contact={
        "name": "KnowMate Support",
        "url": "https://knowmate.example.com",
        "email": "support@knowmate.example.com",
    },
    license_info={
        "name": "MIT",
    },
)
    settings.ensure_storage_dirs()

    logger.info(
        "Starting %s v%s",
        settings.app_name,
        settings.app_version,
    )

    yield

    logger.info("Application shutdown.")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

# ---------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------
# Global Exception Handler
# ---------------------------------------------------------------------

@app.exception_handler(AppError)
async def app_error_handler(
    request: Request,
    exc: AppError,
):
    if exc.status_code >= 500:
        logger.exception(exc)
    else:
        logger.warning(exc.message)

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.code,
            "message": exc.message,
            "details": None,
        },
    )

# ---------------------------------------------------------------------
# Original Project Routers
# ---------------------------------------------------------------------

app.include_router(auth.router, prefix="/auth", tags=["auth"])

app.include_router(documents.router, prefix="/documents")
app.include_router(search.router, prefix="/search")
app.include_router(auth.router, prefix="/auth")
app.include_router(companies.router, prefix="/companies")
app.include_router(chat.router, prefix="/api")

# ---------------------------------------------------------------------
# Data Analysis Routers
# ---------------------------------------------------------------------

app.include_router(health.router)

app.include_router(sessions.router)

app.include_router(analyze.router)

app.include_router(memory.router)

# Uncomment later if API keys are enabled.
# app.include_router(api_keys.router)

# ---------------------------------------------------------------------
# Root
# ---------------------------------------------------------------------

@app.get("/")
def root():
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health",
    }

@app.get(
    "/health",
    tags=["Health"],
    summary="Health check",
    responses={
        200: {
            "description": "API is healthy",
            "content": {
                "application/json": {
                    "example": {"status": "ok"}
                }
            }
        }
    }
)
def health():
    """
    Health check endpoint to verify API is running.

    Returns a simple status response if the API is operational.
    """
    return {"status": "ok"}
# ---------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.env == "dev",
    )