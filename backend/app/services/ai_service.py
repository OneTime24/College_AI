from functools import lru_cache

from app.config import Settings, get_settings
from app.schemas.ai import AIStatus
from app.services.llm import LLMProvider, OllamaProvider, UnconfiguredProvider


class AIService:
    def __init__(self, provider: LLMProvider, settings: Settings):
        self.provider = provider
        self.settings = settings

    async def status(self) -> AIStatus:
        health = await self.provider.health_check()
        return AIStatus(
            provider=self.provider.name,
            model=self.provider.model,
            runtime=health.runtime,
            model_available=health.model_available,
            status=health.status,
        )

    async def chat(self, message: str) -> str:
        return await self.provider.generate(message, self.settings.llm_system_prompt)


@lru_cache
def get_ai_service() -> AIService:
    settings = get_settings()
    if settings.llm_provider.lower() == "ollama":
        provider = OllamaProvider(settings)
    else:
        provider = UnconfiguredProvider()
    return AIService(provider, settings)
