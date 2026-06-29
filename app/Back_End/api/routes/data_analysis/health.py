"""Health + liveness endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from core.config import settings
from core.llm import get_llm_client

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict:
    """Liveness check — reports whether the LLM (Ollama) is reachable."""
    try:
        llm_ok = get_llm_client().is_available()
    except Exception:  # noqa: BLE001 — health must never 500
        llm_ok = False
    return {
        "status": "ok" if llm_ok else "degraded",
        "llm_available": llm_ok,
        "llm_provider": settings.llm_provider,
        "llm_model": settings.llm_model,
        "app_version": settings.app_version,
    }
