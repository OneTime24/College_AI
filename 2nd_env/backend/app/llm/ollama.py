from __future__ import annotations

import asyncio
import json
from urllib import error, request

from backend.app.schemas import LLMMessage, LLMResult


class OllamaProvider:
    provider_name = "ollama"

    def __init__(self, base_url: str, model: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model.strip()

    async def generate(self, messages: list[LLMMessage], *, temperature: float = 0.2) -> LLMResult:
        if not self.model:
            raise RuntimeError("OLLAMA_MODEL is not configured")
        payload = {
            "model": self.model,
            "messages": [message.model_dump() for message in messages],
            "stream": False,
            "options": {"temperature": temperature},
        }
        response = await asyncio.to_thread(self._post_json, "/api/chat", payload)
        content = response.get("message", {}).get("content", "")
        return LLMResult(content=content, model=response.get("model", self.model), provider=self.provider_name, raw=response)

    def _post_json(self, path: str, payload: dict[str, object]) -> dict[str, object]:
        body = json.dumps(payload).encode("utf-8")
        req = request.Request(
            f"{self.base_url}{path}",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=120) as response:
                return json.loads(response.read().decode("utf-8"))
        except error.URLError as exc:  # pragma: no cover - network failure path
            raise RuntimeError(f"Failed to reach Ollama at {self.base_url}: {exc}") from exc
