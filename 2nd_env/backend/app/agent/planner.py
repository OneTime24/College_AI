from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class PlanStep:
    action: str
    tool_name: str | None = None
    tool_args: dict[str, object] | None = None
    needs_llm: bool = False
    reason: str = ""


class RuleBasedPlanner:
    def decide(self, message: str) -> PlanStep:
        normalized = message.casefold().strip()
        if any(phrase in normalized for phrase in ["run this linux command", "shell command", "execute command"]):
            return PlanStep(action="refuse", needs_llm=False, reason="Unsafe shell execution is blocked.")
        if any(keyword in normalized for keyword in ["system status", "health", "backend status", "agent status"]):
            return PlanStep(action="tool", tool_name="system_status", tool_args={}, needs_llm=False, reason="Direct system status request.")
        if any(keyword in normalized for keyword in ["list rooms", "show rooms", "what rooms", "rooms available"]):
            return PlanStep(action="tool", tool_name="list_rooms", tool_args={}, needs_llm=False, reason="Direct room listing request.")
        if any(keyword in normalized for keyword in ["room status", "status of", "what is the status of"]):
            room = self._extract_room_name(message)
            return PlanStep(action="tool", tool_name="get_room_status", tool_args={"room": room} if room else {}, needs_llm=room is None, reason="Room status request.")
        return PlanStep(action="llm", needs_llm=True, reason="General request needs reasoning.")

    def _extract_room_name(self, message: str) -> str | None:
        candidates = ["AI Lab", "Reception", "Demo Room"]
        for candidate in candidates:
            if candidate.casefold() in message.casefold():
                return candidate
        return None
