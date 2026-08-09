from __future__ import annotations

from backend.app.config import AppConfig
from backend.app.schemas import PermissionLevel, ToolSpec


def build_demo_tools(config: AppConfig) -> list[ToolSpec]:
    rooms = {
        "AI Lab": {
            "name": "AI Lab",
            "mode": "normal",
            "simulation": True,
            "devices": {
                "lights": "off",
                "leds": "off",
                "curtains": "open",
                "fan": "on",
            },
        },
        "Reception": {
            "name": "Reception",
            "mode": "normal",
            "simulation": True,
            "devices": {
                "lights": "on",
                "display": "idle",
            },
        },
        "Demo Room": {
            "name": "Demo Room",
            "mode": "presentation",
            "simulation": True,
            "devices": {
                "lights": "dim",
                "projector": "off",
                "curtains": "closed",
            },
        },
    }

    async def system_status(_: dict[str, object]) -> dict[str, object]:
        return {
            "service": "ok",
            "simulation": True,
            "llm_provider": config.llm_provider,
            "ollama_base_url": config.ollama_base_url,
            "ollama_model": config.ollama_model or None,
            "max_tool_calls": config.max_tool_calls,
            "rooms": list(rooms),
        }

    async def list_rooms(_: dict[str, object]) -> dict[str, object]:
        return {
            "rooms": [
                {"name": room["name"], "mode": room["mode"], "simulation": room["simulation"]}
                for room in rooms.values()
            ],
            "simulation": True,
        }

    async def get_room_status(arguments: dict[str, object]) -> dict[str, object]:
        room_name = str(arguments.get("room", "")).strip()
        room = rooms.get(room_name)
        if room is None:
            return {
                "success": False,
                "room": room_name or None,
                "message": f"Room '{room_name}' is not available in the demo registry.",
                "simulation": True,
            }
        return {
            "success": True,
            "room": room,
            "simulation": True,
        }

    return [
        ToolSpec(
            name="system_status",
            description="Return backend, LLM, and simulation status.",
            input_schema={"type": "object", "properties": {}},
            output_schema={"type": "object"},
            permission=PermissionLevel.read,
            simulation=True,
            execute=system_status,
            tags=["status", "health"],
        ),
        ToolSpec(
            name="list_rooms",
            description="List the simulated rooms available in the local hub.",
            input_schema={"type": "object", "properties": {}},
            output_schema={"type": "object"},
            permission=PermissionLevel.read,
            simulation=True,
            execute=list_rooms,
            tags=["rooms"],
        ),
        ToolSpec(
            name="get_room_status",
            description="Get the simulated status for a named room.",
            input_schema={"type": "object", "properties": {"room": {"type": "string"}}, "required": ["room"]},
            output_schema={"type": "object"},
            permission=PermissionLevel.read,
            simulation=True,
            execute=get_room_status,
            tags=["rooms", "status"],
        ),
    ]
