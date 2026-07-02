"""LLM client — single integration point to Ollama or Groq.

Prompts build strings; services call `get_llm_client().chat()`.
Adding a new provider means writing a new adapter class that satisfies
the `LLMClient` protocol and adding a branch in `get_llm_client()`.
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
    """Adapter for a locally-running Ollama server."""

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
        try:
            response = requests.get(self.tags_endpoint, timeout=timeout)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False


class GroqClient:
    """Adapter for the Groq cloud API (OpenAI-compatible)."""

    def __init__(
        self,
        api_key: str | None = None,
        default_model: str | None = None,
    ) -> None:
        self.api_key = api_key or settings.groq_api_key
        self.default_model = default_model or settings.groq_model
        self.base_url = settings.groq_base_url
        self.chat_endpoint = f"{self.base_url}/chat/completions"
        self.models_endpoint = f"{self.base_url}/models"

    def chat(
        self,
        user_prompt: str,
        *,
        system_prompt: str | None = None,
        model: str | None = None,
        timeout: int | None = None,
    ) -> str:
        model = model or self.default_model
        timeout = timeout or settings.llm_request_timeout_seconds

        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_prompt})

        payload = {"model": model, "messages": messages}
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(
                self.chat_endpoint, json=payload, headers=headers, timeout=timeout
            )
        except requests.exceptions.ConnectionError as exc:
            raise LLMError("Could not connect to Groq API.") from exc
        except requests.exceptions.Timeout as exc:
            raise LLMError(f"Groq did not respond within {timeout}s.") from exc
        except requests.exceptions.RequestException as exc:
            raise LLMError(f"Request to Groq failed: {exc}") from exc

        if response.status_code != 200:
            detail = response.text[:500]
            if response.status_code == 401:
                detail = "Invalid Groq API key."
            raise LLMError(f"Groq returned status {response.status_code}: {detail}")

        try:
            data = response.json()
            content = data["choices"][0]["message"]["content"]
        except (ValueError, KeyError, TypeError, IndexError) as exc:
            raise LLMError(f"Unexpected response shape from Groq: {exc}") from exc

        if not content or not content.strip():
            raise LLMError("Groq returned an empty response.")

        logger.info(
            "Groq call succeeded (model=%s, response length=%d chars)",
            model, len(content),
        )
        return content

    def is_available(self, *, timeout: int = 3) -> bool:
        if not self.api_key:
            return False
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            response = requests.get(self.models_endpoint, headers=headers, timeout=timeout)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False


_default_client: LLMClient | None = None


def get_llm_client() -> LLMClient:
    """Return the process-wide LLM client (lazily instantiated)."""
    global _default_client
    if _default_client is None:
        if settings.llm_provider == "ollama":
            _default_client = OllamaClient()
        elif settings.llm_provider == "groq":
            _default_client = GroqClient()
        else:
            raise LLMError(f"Unknown llm_provider: {settings.llm_provider}")
    return _default_client


def set_llm_client(client: LLMClient) -> None:
    """Override the default client (used in tests)."""
    global _default_client
    _default_client = client