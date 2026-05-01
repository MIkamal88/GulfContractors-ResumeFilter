"""
AI provider abstractions with automatic fallback.

Each provider exposes ``generate_json(system, prompt, max_tokens, temperature)``
and either returns the raw model text (expected to be JSON) or raises
``AIProviderError`` so the caller can move on to the next provider in the chain.

Providers:
- GeminiProvider          : google-genai SDK, response_mime_type=application/json
- GroqProvider            : OpenAI-compatible REST, json_object response_format
- OpenRouterProvider      : OpenAI-compatible REST + multi-model fallback array

This file is intentionally self-contained so it can be deleted once the
in-house inference service comes online.
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import List, Optional

import httpx


class AIProviderError(Exception):
    """Raised when a provider attempt fails in a way that should trigger fallback."""


# Status codes worth retrying / falling back on (transient or capacity issues).
_TRANSIENT_STATUS = {408, 425, 429, 500, 502, 503, 504, 529}


class BaseProvider(ABC):
    """Common interface for all AI providers."""

    name: str = "base"

    @abstractmethod
    def generate_json(
        self,
        system: str,
        prompt: str,
        max_tokens: int = 5000,
        temperature: float = 0.4,
    ) -> str:
        """Return the raw model output (expected to be JSON string)."""


# ---------------------------------------------------------------------------
# Gemini
# ---------------------------------------------------------------------------


class GeminiProvider(BaseProvider):
    name = "gemini"

    def __init__(self, api_key: str, model: str):
        # Lazy import so the module stays importable even if google-genai is
        # not installed in some future minimal deployment.
        from google import genai  # noqa: WPS433

        self._genai = genai
        self._model = model
        self._client = genai.Client(api_key=api_key)

    def generate_json(
        self,
        system: str,
        prompt: str,
        max_tokens: int = 5000,
        temperature: float = 0.4,
    ) -> str:
        from google.genai import types  # noqa: WPS433
        from google.genai.types import ThinkingConfig  # noqa: WPS433

        last_err: Optional[Exception] = None
        for attempt in (1, 2):
            try:
                response = self._client.models.generate_content(
                    model=self._model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system,
                        max_output_tokens=max_tokens,
                        temperature=temperature,
                        response_mime_type="application/json",
                        thinking_config=ThinkingConfig(thinking_budget=0),
                    ),
                )
                text = response.text
                if text is None or not text.strip():
                    raise AIProviderError("empty response")

                usage = getattr(response, "usage_metadata", None)
                if usage:
                    print(
                        f"[ai] gemini ok model={self._model} "
                        f"tokens prompt={usage.prompt_token_count} "
                        f"completion={usage.candidates_token_count} "
                        f"total={usage.total_token_count}"
                    )
                return text
            except AIProviderError:
                raise
            except Exception as exc:  # noqa: BLE001
                last_err = exc
                msg = str(exc).lower()
                # Heuristic: 503 / overloaded / unavailable / quota are retriable.
                transient = any(
                    token in msg
                    for token in (
                        "503",
                        "429",
                        "500",
                        "overloaded",
                        "unavailable",
                        "deadline",
                        "timeout",
                        "quota",
                        "rate",
                        "retry",
                    )
                )
                print(
                    f"[ai] gemini attempt={attempt} model={self._model} "
                    f"failed transient={transient}: {exc}"
                )
                if attempt == 1 and transient:
                    time.sleep(1.5)
                    continue
                raise AIProviderError(f"gemini: {exc}") from exc

        raise AIProviderError(f"gemini exhausted retries: {last_err}")


# ---------------------------------------------------------------------------
# OpenAI-compatible base (Groq, OpenRouter)
# ---------------------------------------------------------------------------


class OpenAICompatibleProvider(BaseProvider):
    """Shared logic for any /chat/completions OpenAI-compatible endpoint."""

    base_url: str = ""
    default_model: str = ""

    def __init__(
        self,
        api_key: str,
        model: Optional[str] = None,
        extra_headers: Optional[dict] = None,
        extra_body: Optional[dict] = None,
        timeout: float = 45.0,
    ):
        self._api_key = api_key
        self._model = model or self.default_model
        self._extra_headers = extra_headers or {}
        self._extra_body = extra_body or {}
        self._timeout = timeout

    def _headers(self) -> dict:
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        headers.update(self._extra_headers)
        return headers

    def _build_body(
        self, system: str, prompt: str, max_tokens: int, temperature: float
    ) -> dict:
        body = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "response_format": {"type": "json_object"},
        }
        body.update(self._extra_body)
        return body

    def generate_json(
        self,
        system: str,
        prompt: str,
        max_tokens: int = 5000,
        temperature: float = 0.4,
    ) -> str:
        url = f"{self.base_url.rstrip('/')}/chat/completions"
        body = self._build_body(system, prompt, max_tokens, temperature)
        last_err: Optional[Exception] = None

        for attempt in (1, 2):
            try:
                with httpx.Client(timeout=self._timeout) as client:
                    resp = client.post(url, headers=self._headers(), json=body)

                if resp.status_code in _TRANSIENT_STATUS:
                    print(
                        f"[ai] {self.name} attempt={attempt} model={self._model} "
                        f"transient http={resp.status_code} body={resp.text[:200]}"
                    )
                    last_err = AIProviderError(
                        f"{self.name} http {resp.status_code}: {resp.text[:200]}"
                    )
                    if attempt == 1:
                        retry_after = resp.headers.get("retry-after")
                        sleep_s = 1.5
                        if retry_after:
                            try:
                                sleep_s = max(sleep_s, float(retry_after))
                            except ValueError:
                                pass
                        time.sleep(min(sleep_s, 5.0))
                        continue
                    raise last_err

                if resp.status_code >= 400:
                    # Non-transient (auth, model not found, malformed request) —
                    # surface as fallback-trigger but do not retry.
                    raise AIProviderError(
                        f"{self.name} http {resp.status_code}: {resp.text[:200]}"
                    )

                data = resp.json()
                choices = data.get("choices") or []
                if not choices:
                    raise AIProviderError(f"{self.name}: no choices in response")
                content = (choices[0].get("message") or {}).get("content")
                if not content or not content.strip():
                    raise AIProviderError(f"{self.name}: empty content")

                usage = data.get("usage") or {}
                print(
                    f"[ai] {self.name} ok model={self._model} "
                    f"tokens prompt={usage.get('prompt_tokens')} "
                    f"completion={usage.get('completion_tokens')} "
                    f"total={usage.get('total_tokens')}"
                )
                return content

            except AIProviderError:
                raise
            except (httpx.TimeoutException, httpx.NetworkError) as exc:
                last_err = exc
                print(
                    f"[ai] {self.name} attempt={attempt} model={self._model} "
                    f"network: {exc}"
                )
                if attempt == 1:
                    time.sleep(1.5)
                    continue
                raise AIProviderError(f"{self.name}: {exc}") from exc
            except Exception as exc:  # noqa: BLE001
                raise AIProviderError(f"{self.name}: {exc}") from exc

        raise AIProviderError(f"{self.name} exhausted retries: {last_err}")


class GroqProvider(OpenAICompatibleProvider):
    name = "groq"
    base_url = "https://api.groq.com/openai/v1"
    default_model = "meta-llama/llama-4-scout-17b-16e-instruct"


class OpenRouterProvider(OpenAICompatibleProvider):
    name = "openrouter"
    base_url = "https://openrouter.ai/api/v1"
    default_model = "qwen/qwen3-next-80b-a3b-instruct:free"

    def __init__(
        self,
        api_key: str,
        model: Optional[str] = None,
        fallback_model: Optional[str] = None,
        site_url: str = "",
        app_name: str = "",
        timeout: float = 45.0,
    ):
        extra_headers = {}
        if site_url:
            extra_headers["HTTP-Referer"] = site_url
        if app_name:
            extra_headers["X-OpenRouter-Title"] = app_name

        # OpenRouter's "models" array enables in-request fallback to a second
        # free model when the primary is rate-limited or unavailable.
        extra_body: dict = {}
        chain: List[str] = []
        primary = model or self.default_model
        chain.append(primary)
        if fallback_model and fallback_model != primary:
            chain.append(fallback_model)
        if len(chain) > 1:
            extra_body["models"] = chain

        super().__init__(
            api_key=api_key,
            model=primary,
            extra_headers=extra_headers,
            extra_body=extra_body,
            timeout=timeout,
        )


# ---------------------------------------------------------------------------
# Chain construction
# ---------------------------------------------------------------------------


def _instantiate(name: str, settings) -> Optional[BaseProvider]:
    """Build a single provider instance or return None if its key is missing."""
    name = name.strip().lower()
    if not name:
        return None

    if name == "gemini":
        if not settings.gemini_api_key:
            return None
        try:
            return GeminiProvider(
                api_key=settings.gemini_api_key, model=settings.gemini_model
            )
        except Exception as exc:  # noqa: BLE001
            print(f"[ai] gemini init failed: {exc}")
            return None

    if name == "groq":
        if not getattr(settings, "groq_api_key", None):
            return None
        return GroqProvider(
            api_key=settings.groq_api_key,
            model=getattr(settings, "groq_model", None),
        )

    if name == "openrouter":
        if not getattr(settings, "openrouter_api_key", None):
            return None
        return OpenRouterProvider(
            api_key=settings.openrouter_api_key,
            model=getattr(settings, "openrouter_model", None),
            fallback_model=getattr(settings, "openrouter_fallback_model", None),
            site_url=getattr(settings, "openrouter_site_url", "") or "",
            app_name=getattr(settings, "openrouter_app_name", "") or "",
        )

    print(f"[ai] unknown provider name in chain: {name!r}")
    return None


def build_provider_chain(settings) -> List[BaseProvider]:
    """
    Build the ordered provider chain from ``AI_PROVIDER_PRIMARY`` and
    ``AI_PROVIDER_FALLBACKS`` settings. Providers without an API key are
    silently skipped.
    """
    raw_chain: List[str] = []
    primary = (getattr(settings, "ai_provider_primary", "gemini") or "gemini").strip()
    raw_chain.append(primary)

    fallbacks = getattr(settings, "ai_provider_fallbacks", "") or ""
    for entry in fallbacks.split(","):
        entry = entry.strip()
        if entry and entry not in raw_chain:
            raw_chain.append(entry)

    providers: List[BaseProvider] = []
    for name in raw_chain:
        provider = _instantiate(name, settings)
        if provider is not None:
            providers.append(provider)

    return providers
