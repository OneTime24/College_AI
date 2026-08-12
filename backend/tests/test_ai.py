import pytest

from app.api.ai import get_ai_service
from app.config import get_settings
from app.main import app
from app.services.ai_service import AIService
from app.services.llm.base import LLMProvider, ProviderStatus
from app.services.llm.ollama_provider import OllamaProvider
from app.services.speech import SpeechService


class FakeProvider(LLMProvider):
    name = "ollama"
    model = "test-model"

    async def generate(self, message: str, system_prompt: str, images: list[str] | None = None) -> str:
        return f"Local answer: {message}"

    async def health_check(self) -> ProviderStatus:
        return ProviderStatus(runtime="available", model_available=True, status="online", supports_image_input=True, supports_voice_input=True, supports_voice_output=True)


@pytest.fixture
def fake_ai_service():
    return AIService(FakeProvider(), get_settings())


@pytest.fixture
def mock_ai(fake_ai_service):
    app.dependency_overrides[get_ai_service] = lambda: fake_ai_service
    yield
    app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_ai_status_endpoint(client, mock_ai, monkeypatch):
    monkeypatch.setattr(SpeechService, "supports_transcription", lambda settings=None: False)
    monkeypatch.setattr(SpeechService, "supports_text_to_speech", lambda: True)
    response = await client.get("/api/ai/status")
    assert response.status_code == 200
    assert response.json() == {
        "provider": "ollama", "model": "test-model", "runtime": "available",
        "model_available": True, "status": "online", "supports_image_input": True, "supports_voice_input": False, "supports_voice_output": True,
        "voice_input_engine": "unavailable", "voice_output_engine": "espeak-ng",
    }


@pytest.mark.anyio
async def test_chat_rejects_empty_message(client, mock_ai):
    response = await client.post("/api/ai/chat", json={"message": "   "})
    assert response.status_code == 422
    assert response.json()["detail"] == "Message cannot be empty."


@pytest.mark.anyio
async def test_chat_returns_provider_response(client, mock_ai):
    response = await client.post("/api/ai/chat", json={"message": "What is the capital of Pakistan?"})
    assert response.status_code == 200
    assert response.json() == {
        "response": "Local answer: What is the capital of Pakistan?",
        "model": "test-model", "provider": "ollama",
    }


@pytest.mark.anyio
async def test_ollama_provider_reports_unavailable_runtime():
    settings = get_settings().model_copy(update={"ollama_base_url": "http://127.0.0.1:9", "llm_timeout": 0.1})
    status = await OllamaProvider(settings).health_check()
    assert status.runtime == "unavailable"
    assert status.status == "offline"
