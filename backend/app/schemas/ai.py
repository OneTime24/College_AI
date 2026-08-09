from pydantic import BaseModel, Field


class AIStatus(BaseModel):
    provider: str
    model: str | None = None
    runtime: str
    model_available: bool = False
    status: str


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)


class ChatResponse(BaseModel):
    response: str
    model: str
    provider: str
