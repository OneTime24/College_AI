from __future__ import annotations

from dataclasses import dataclass

from backend.app.agent.planner import RuleBasedPlanner
from backend.app.llm.base import LLMProvider
from backend.app.schemas import ChatResponse, LLMMessage, ToolCallRecord
from backend.app.services.context_store import ConversationStore
from backend.app.tools.registry import ToolRegistry


@dataclass(slots=True)
class AgentCore:
    llm_provider: LLMProvider | None
    tool_registry: ToolRegistry
    conversation_store: ConversationStore
    max_tool_calls: int = 3

    async def handle(self, session_id: str, user_message: str) -> ChatResponse:
        action_log: list[str] = [f"received_message:{user_message}"]
        tool_calls: list[ToolCallRecord] = []
        planner = RuleBasedPlanner()
        self.conversation_store.append(session_id, LLMMessage(role="user", content=user_message))

        plan = planner.decide(user_message)
        action_log.append(f"plan:{plan.action}:{plan.reason}")

        if plan.action == "refuse":
            answer = "I cannot execute shell commands. I can only use registered local tools."
            self.conversation_store.append(session_id, LLMMessage(role="assistant", content=answer))
            return ChatResponse(session_id=session_id, answer=answer, used_llm=False, tool_calls=tool_calls, action_log=action_log)

        if plan.action == "tool" and plan.tool_name:
            tool_result = await self._call_tool(plan.tool_name, plan.tool_args or {}, tool_calls, action_log)
            answer = self._summarize_tool_result(plan.tool_name, tool_result.payload, tool_result.success)
            if self.llm_provider and tool_result.success:
                answer = await self._polish_with_llm(session_id, user_message, answer, action_log)
            self.conversation_store.append(session_id, LLMMessage(role="assistant", content=answer))
            return ChatResponse(session_id=session_id, answer=answer, used_llm=self.llm_provider is not None and tool_result.success, tool_calls=tool_calls, action_log=action_log)

        if plan.action == "llm" and self.llm_provider is not None:
            answer = await self._answer_with_llm(session_id, user_message, action_log)
            self.conversation_store.append(session_id, LLMMessage(role="assistant", content=answer))
            return ChatResponse(session_id=session_id, answer=answer, used_llm=True, tool_calls=tool_calls, action_log=action_log)

        answer = "I can help with system status, listing rooms, and room status in this foundation build."
        self.conversation_store.append(session_id, LLMMessage(role="assistant", content=answer))
        return ChatResponse(session_id=session_id, answer=answer, used_llm=False, tool_calls=tool_calls, action_log=action_log)

    async def _call_tool(self, tool_name: str, tool_args: dict[str, object], tool_calls: list[ToolCallRecord], action_log: list[str]):
        if len(tool_calls) >= self.max_tool_calls:
            action_log.append("tool_limit_reached")
            return await self.tool_registry.execute("__missing__", {})
        action_log.append(f"tool_call:{tool_name}:{tool_args}")
        result = await self.tool_registry.execute(tool_name, tool_args)
        tool_calls.append(ToolCallRecord(tool_name=tool_name, tool_args=tool_args, success=result.success, result=result.payload))
        action_log.append(f"tool_result:{tool_name}:{'success' if result.success else 'failure'}")
        return result

    def _summarize_tool_result(self, tool_name: str, payload: dict[str, object], success: bool) -> str:
        if not success:
            return str(payload.get("message", f"{tool_name} failed."))
        if tool_name == "system_status":
            return "System status is available and the local demo tools are ready."
        if tool_name == "list_rooms":
            rooms = payload.get("rooms", [])
            names = ", ".join(room.get("name", "unknown") for room in rooms if isinstance(room, dict))
            return f"Available rooms: {names}."
        if tool_name == "get_room_status":
            room = payload.get("room", {})
            return f"Room status loaded for {room.get('name', 'unknown')} in simulation."
        return "Tool completed successfully."

    async def _answer_with_llm(self, session_id: str, user_message: str, action_log: list[str]) -> str:
        history = self.conversation_store.get(session_id)
        messages = [
            LLMMessage(
                role="system",
                content=(
                    "You are the AI College local assistant. Keep responses concise, grounded, and honest. "
                    "Do not claim to control hardware unless a tool result confirms it."
                ),
            ),
            *history,
        ]
        action_log.append("llm_generate:direct")
        result = await self.llm_provider.generate(messages)
        return result.content.strip() or "I could not generate a response."

    async def _polish_with_llm(self, session_id: str, user_message: str, tool_summary: str, action_log: list[str]) -> str:
        history = self.conversation_store.get(session_id)
        messages = [
            LLMMessage(
                role="system",
                content=(
                    "You are the AI College local assistant. Rewrite the tool result as a concise user-facing response. "
                    "Do not add facts that are not in the tool result."
                ),
            ),
            *history,
            LLMMessage(role="assistant", content=f"Tool summary: {tool_summary}"),
            LLMMessage(role="user", content=user_message),
        ]
        action_log.append("llm_generate:polish")
        result = await self.llm_provider.generate(messages)
        return result.content.strip() or tool_summary
