from __future__ import annotations

from backend.app.config import AppConfig
from backend.app.llm.base import LLMProvider
from backend.app.llm.ollama import OllamaProvider


def build_llm_provider(config: AppConfig) -> LLMProvider | None:
    if config.llm_provider.lower() == "ollama":
        if not config.ollama_model:
            return None
        return OllamaProvider(config.ollama_base_url, config.ollama_model)
    return None
