"""LLM client — single integration point to Ollama.

This is the *only* module in the codebase that talks to Ollama over
HTTP. prompts/ builds strings; services/ calls `call_llm()` here and
decides what to do with the response. Swapping providers later means
adding a new adapter that implements the same `LLMClient` protocol —
no other file needs to change.

The protocol is intentionally narrow: it takes (system_prompt,
user_prompt, model) and returns the raw text. Streaming, tool calling,
and multi-turn chat history are NOT in this protocol because the
existing pipeline is single-shot text-in/text-out per stage. Add them
when an actual consumer needs them.
"""

from __future__ import annotations

import logging
from typing import Protocol

import requests

from app.Back_End.core.config import settings
from app.Back_End.core.data_analysis.exceptions import LLMError

logger = logging.getLogger(__name__)


class LLMClient(Protocol):
    """Minimal contract any LLM adapter must satisfy."""

    def chat(
        self,
        user_prompt: str,
        *,
        system_prompt: str | None = None,
        model: str | None = None,
        timeout: int | None = None,
    ) -> str: ...

    def is_available(self, *, timeout: int = 3) -> bool: ...


class OllamaClient:
    """Adapter for a locally-running Ollama server.

    Endpoint paths come from settings so the same code works against a
    remote Ollama instance by setting llm_ollama_base_url.
    """

    def __init__(
        self,
        base_url: str | None = None,
        default_model: str | None = None,
    ) -> None:
        self.base_url = base_url or settings.llm_ollama_base_url
        self.default_model = default_model or settings.llm_model
        self.chat_endpoint = f"{self.base_url}{settings.llm_ollama_chat_endpoint}"
        self.tags_endpoint = f"{self.base_url}{settings.llm_ollama_tags_endpoint}"

    def chat(
        self,
        user_prompt: str,
        *,
        system_prompt: str | None = None,
        model: str | None = None,
        timeout: int | None = None,
    ) -> str:
        """Single-turn chat call. Raises LLMError on any failure."""
        model = model or self.default_model
        timeout = timeout or settings.llm_request_timeout_seconds

        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_prompt})

        payload = {"model": model, "messages": messages, "stream": False}

        try:
            response = requests.post(self.chat_endpoint, json=payload, timeout=timeout)
        except requests.exceptions.ConnectionError as exc:
            raise LLMError(
                f"Could not connect to Ollama at {self.base_url}. Is it running?",
            ) from exc
        except requests.exceptions.Timeout as exc:
            raise LLMError(
                f"Ollama did not respond within {timeout}s — model may still be loading.",
            ) from exc
        except requests.exceptions.RequestException as exc:
            raise LLMError(f"Request to Ollama failed: {exc}") from exc

        if response.status_code != 200:
            raise LLMError(
                f"Ollama returned status {response.status_code}: {response.text[:500]}",
            )

        try:
            data = response.json()
            content = data["message"]["content"]
        except (ValueError, KeyError, TypeError) as exc:
            raise LLMError(f"Unexpected response shape from Ollama: {exc}") from exc

        if not content or not content.strip():
            raise LLMError("Ollama returned an empty response.")

        logger.info(
            "Ollama call succeeded (model=%s, response length=%d chars)",
            model, len(content),
        )
        return content

    def is_available(self, *, timeout: int = 3) -> bool:
        """Quick liveness check — used by /health."""
        try:
            response = requests.get(self.tags_endpoint, timeout=timeout)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False


# Module-level singleton — most of the app is fine sharing one Ollama
# client. Tests can construct their own OllamaClient instance and pass
# it through.
_default_client: LLMClient | None = None


def get_llm_client() -> LLMClient:
    """Return the process-wide LLM client (lazily instantiated)."""
    global _default_client
    if _default_client is None:
        # Currently only Ollama is implemented; the branch below is
        # where a CloudAdapter case would slot in when needed.
        if settings.llm_provider == "ollama":
            _default_client = OllamaClient()
        else:  # pragma: no cover - defensive
            raise LLMError(f"Unknown llm_provider: {settings.llm_provider}")
    return _default_client


def set_llm_client(client: LLMClient) -> None:
    """Override the default client (used in tests)."""
    global _default_client
    _default_client = client