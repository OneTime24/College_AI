from abc import ABC, abstractmethod
from dataclasses import dataclass


class LLMProviderError(Exception):
    """A safe, provider-facing failure suitable for API handling."""


class LLMRuntimeUnavailable(LLMProviderError):
    """The configured local runtime cannot be reached."""


@dataclass(frozen=True)
class ProviderStatus:
    runtime: str
    model_available: bool
    status: str
    supports_image_input: bool = False
    supports_voice_input: bool = False
    supports_voice_output: bool = False


class LLMProvider(ABC):
    name: str
    model: str

    @abstractmethod
    async def generate(self, message: str, system_prompt: str, images: list[str] | None = None) -> str:
        """Generate one non-streamed assistant response."""

    @abstractmethod
    async def health_check(self) -> ProviderStatus:
        """Report runtime and configured-model availability without raising."""


class UnconfiguredProvider(LLMProvider):
    """Safe provider used when no supported local provider is configured."""

    name = "not_configured"
    model = ""

    async def generate(self, message: str, system_prompt: str) -> str:
        raise LLMProviderError("Local AI provider is not configured.")

    async def health_check(self) -> ProviderStatus:
        return ProviderStatus(runtime="unavailable", model_available=False, status="not_configured")
