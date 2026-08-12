from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.ai import AIStatus, ChatRequest, ChatResponse
from app.services.ai_service import AIService, get_ai_service
from app.services.llm import LLMProviderError

router = APIRouter(prefix="/ai", tags=["ai"])


@router.get("/status", response_model=AIStatus)
async def ai_status(service: AIService = Depends(get_ai_service)):
    return await service.status()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    service: AIService = Depends(get_ai_service),
):
    message = request.message.strip()
    if not message:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Message cannot be empty.")
    if len(message) > service.settings.llm_max_input_characters:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Message must be at most {service.settings.llm_max_input_characters} characters.",
        )
    try:
        response = await service.chat(message)
    except LLMProviderError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    return ChatResponse(response=response, model=service.provider.model, provider=service.provider.name)
