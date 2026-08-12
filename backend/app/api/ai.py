from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.ai import AIStatus, ChatRequest, ChatResponse
from app.services.ai_service import AIService, get_ai_service
from app.services.llm import LLMProviderError
from app.services.speech import SpeechService, get_speech_service

router = APIRouter(prefix="/ai", tags=["ai"])


@router.get("/status", response_model=AIStatus)
async def ai_status(service: AIService = Depends(get_ai_service)):
    return await service.status()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    service: AIService = Depends(get_ai_service),
    speech: SpeechService = Depends(get_speech_service),
):
    message = request.message.strip()
    transcript_parts: list[str] = []
    for item in request.audio[:1]:
        if not item.strip():
            continue
        try:
            transcript = await speech.transcribe(item)
        except LLMProviderError as exc:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
        transcript_parts.append(transcript)
    transcript = " ".join(transcript_parts).strip() or None
    if transcript:
        message = f"{message} {transcript}".strip()
    if not message:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Message cannot be empty.")
    if len(message) > service.settings.llm_max_input_characters:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Message must be at most {service.settings.llm_max_input_characters} characters.",
        )
    images = []
    for item in request.images[:3]:
        if not isinstance(item, str) or not item.strip():
            continue
        image = item.strip()
        if image.startswith("data:"):
            comma_index = image.find(",")
            image = image[comma_index + 1 :] if comma_index >= 0 else image
        images.append(image)
    try:
        response = await service.chat(message, images=images or None)
    except LLMProviderError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    return ChatResponse(response=response, model=service.provider.model, provider=service.provider.name, transcript=transcript)
