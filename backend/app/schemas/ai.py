from pydantic import BaseModel, Field


class AIStatus(BaseModel):
    provider: str
    model: str | None = None
    runtime: str
    model_available: bool = False
    status: str
    supports_image_input: bool = False
    supports_voice_input: bool = False
    supports_voice_output: bool = False
    voice_input_engine: str = "unavailable"
    voice_output_engine: str = "unavailable"


class ChatRequest(BaseModel):
    message: str = Field(default="")
    audio: list[str] = Field(default_factory=list)
    images: list[str] = Field(default_factory=list)


class ChatResponse(BaseModel):
    response: str
    model: str
    provider: str
    transcript: str | None = None
