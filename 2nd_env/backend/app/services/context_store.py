from __future__ import annotations

from collections import defaultdict, deque

from backend.app.schemas import LLMMessage


class ConversationStore:
    def __init__(self, max_messages: int = 12) -> None:
        self.max_messages = max_messages
        self._store: dict[str, deque[LLMMessage]] = defaultdict(lambda: deque(maxlen=max_messages))

    def append(self, session_id: str, message: LLMMessage) -> None:
        self._store[session_id].append(message)

    def get(self, session_id: str) -> list[LLMMessage]:
        return list(self._store[session_id])
