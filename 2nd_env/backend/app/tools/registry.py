from __future__ import annotations

from dataclasses import dataclass

from backend.app.schemas import ToolResult, ToolSpec


@dataclass(slots=True)
class ToolRegistry:
    tools: dict[str, ToolSpec]

    @classmethod
    def from_tools(cls, tools: list[ToolSpec]) -> "ToolRegistry":
        return cls({tool.name: tool for tool in tools})

    def get(self, name: str) -> ToolSpec | None:
        return self.tools.get(name)

    def list(self) -> list[ToolSpec]:
        return list(self.tools.values())

    async def execute(self, name: str, arguments: dict[str, object]) -> ToolResult:
        tool = self.get(name)
        if tool is None:
            return ToolResult(success=False, message=f"Tool '{name}' is not registered.")
        payload = await tool.execute(arguments)
        if payload.get("success") is False:
            return ToolResult(success=False, message=str(payload.get("message", "Tool failed.")), payload=payload)
        return ToolResult(success=True, message=f"Tool '{name}' completed.", payload=payload)
