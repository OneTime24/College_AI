from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response

from app.services.speech import SpeechService, get_speech_service
from app.services.llm import LLMProviderError

router = APIRouter(prefix="/speech", tags=["speech"])


@router.post("/tts")
async def text_to_speech(payload: dict[str, str], speech: SpeechService = Depends(get_speech_service)):
    text = payload.get("text", "").strip()
    if not text:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Text cannot be empty.")
    try:
        audio = await speech.synthesize(text)
    except LLMProviderError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    return Response(content=audio, media_type="audio/wav")
