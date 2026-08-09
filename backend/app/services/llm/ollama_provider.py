import logging

import httpx

from app.config import Settings
from app.services.llm.base import LLMProvider, LLMProviderError, LLMRuntimeUnavailable, ProviderStatus

logger = logging.getLogger(__name__)


class OllamaProvider(LLMProvider):
    name = "ollama"

    def __init__(self, settings: Settings):
        self.base_url = settings.ollama_base_url.rstrip("/")
        self.model = settings.ollama_model
        self.timeout = settings.llm_timeout
        self.temperature = settings.llm_temperature
        self.max_tokens = settings.llm_max_tokens

    async def health_check(self) -> ProviderStatus:
        try:
            async with httpx.AsyncClient(timeout=min(self.timeout, 10.0)) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                response.raise_for_status()
                models = response.json().get("models", [])
        except (httpx.HTTPError, ValueError) as exc:
            logger.warning("Ollama runtime health check failed: %s", exc)
            return ProviderStatus(runtime="unavailable", model_available=False, status="offline")

        available = any(item.get("name") == self.model for item in models)
        return ProviderStatus(
            runtime="available",
            model_available=available,
            status="online" if available else "error",
        )

    async def generate(self, message: str, system_prompt: str) -> str:
        payload = {
            "model": self.model,
            "prompt": message,
            "system": system_prompt,
            "stream": False,
            "options": {"temperature": self.temperature, "num_predict": self.max_tokens},
        }
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(f"{self.base_url}/api/generate", json=payload)
                response.raise_for_status()
                data = response.json()
        except httpx.ConnectError as exc:
            logger.warning("Ollama runtime is unavailable: %s", exc)
            raise LLMRuntimeUnavailable("Local AI runtime is unavailable.") from exc
        except httpx.TimeoutException as exc:
            logger.warning("Ollama generation timed out: %s", exc)
            raise LLMProviderError("Local AI generation timed out.") from exc
        except httpx.HTTPStatusError as exc:
            logger.warning("Ollama generation failed with status %s", exc.response.status_code)
            raise LLMProviderError("Local AI model could not generate a response.") from exc
        except (httpx.HTTPError, ValueError) as exc:
            logger.exception("Unexpected Ollama provider failure")
            raise LLMProviderError("Local AI engine is unavailable.") from exc

        text = data.get("response")
        if not isinstance(text, str) or not text.strip():
            logger.warning("Ollama returned an empty response for model %s", self.model)
            raise LLMProviderError("Local AI model returned an empty response.")
        return text.strip()
