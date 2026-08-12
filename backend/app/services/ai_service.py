from functools import lru_cache

from app.config import Settings, get_settings
from app.schemas.ai import AIStatus
from app.services.llm import LLMProvider, OllamaProvider, UnconfiguredProvider
from app.services.speech import SpeechService


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
            supports_image_input=health.supports_image_input,
            supports_voice_input=SpeechService.supports_transcription(self.settings),
            supports_voice_output=SpeechService.supports_text_to_speech(self.settings),
            voice_input_engine=SpeechService.voice_input_engine(self.settings),
            voice_output_engine=SpeechService.voice_output_engine(self.settings),
        )

    async def chat(self, message: str, images: list[str] | None = None) -> str:
        return await self.provider.generate(message, self.settings.llm_system_prompt, images=images)


@lru_cache
def get_ai_service() -> AIService:
    settings = get_settings()
    if settings.llm_provider.lower() == "ollama":
        provider = OllamaProvider(settings)
    else:
        provider = UnconfiguredProvider()
    return AIService(provider, settings)
