from __future__ import annotations

from fastapi import APIRouter, HTTPException

from backend.app.agent.core import AgentCore
from backend.app.schemas import ChatRequest, ChatResponse, ToolSpec


def build_router(agent: AgentCore, tools: list[ToolSpec]) -> APIRouter:
    router = APIRouter()

    @router.get("/health")
    async def health() -> dict[str, object]:
        return {"status": "ok", "tool_count": len(tools), "llm_available": agent.llm_provider is not None}

    @router.get("/system/status")
    async def system_status() -> dict[str, object]:
        result = await agent.tool_registry.execute("system_status", {})
        return result.payload

    @router.get("/rooms")
    async def list_rooms() -> dict[str, object]:
        result = await agent.tool_registry.execute("list_rooms", {})
        return result.payload

    @router.get("/rooms/{room_name}")
    async def room_status(room_name: str) -> dict[str, object]:
        result = await agent.tool_registry.execute("get_room_status", {"room": room_name})
        if not result.success:
            raise HTTPException(status_code=404, detail=result.message)
        return result.payload

    @router.post("/agent/chat", response_model=ChatResponse)
    async def chat(request: ChatRequest) -> ChatResponse:
        return await agent.handle(request.session_id, request.message)

    return router
