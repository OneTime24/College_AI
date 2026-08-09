from __future__ import annotations

from typing import Protocol

from backend.app.schemas import LLMMessage, LLMResult


class LLMProvider(Protocol):
    provider_name: str

    async def generate(self, messages: list[LLMMessage], *, temperature: float = 0.2) -> LLMResult: ...
