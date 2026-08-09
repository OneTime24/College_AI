from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class PermissionLevel(str, Enum):
    read = "read"
    control = "control"
    high_risk = "high_risk"


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    session_id: str = Field(default="default")


class ToolCallRecord(BaseModel):
    tool_name: str
    tool_args: dict[str, Any] = Field(default_factory=dict)
    success: bool
    result: dict[str, Any] = Field(default_factory=dict)


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    used_llm: bool
    tool_calls: list[ToolCallRecord] = Field(default_factory=list)
    action_log: list[str] = Field(default_factory=list)


class LLMMessage(BaseModel):
    role: str
    content: str


class LLMResult(BaseModel):
    content: str
    model: str | None = None
    provider: str | None = None
    raw: dict[str, Any] = Field(default_factory=dict)


class ToolResult(BaseModel):
    success: bool
    message: str
    payload: dict[str, Any] = Field(default_factory=dict)


@dataclass(slots=True)
class ToolSpec:
    name: str
    description: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    permission: PermissionLevel
    simulation: bool
    execute: Any
    tags: list[str] = field(default_factory=list)
