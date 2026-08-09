from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.app.agent.core import AgentCore
from backend.app.api.routes import build_router
from backend.app.config import load_config
from backend.app.llm.service import build_llm_provider
from backend.app.services.context_store import ConversationStore
from backend.app.tools.demo import build_demo_tools
from backend.app.tools.registry import ToolRegistry


def create_app() -> FastAPI:
    config = load_config()
    tools = build_demo_tools(config)
    tool_registry = ToolRegistry.from_tools(tools)
    llm_provider = build_llm_provider(config)
    conversation_store = ConversationStore()
    agent = AgentCore(
        llm_provider=llm_provider,
        tool_registry=tool_registry,
        conversation_store=conversation_store,
        max_tool_calls=config.max_tool_calls,
    )

    app = FastAPI(title=config.app_title)
    app.state.config = config
    app.state.agent = agent
    app.state.tool_registry = tool_registry
    app.include_router(build_router(agent, tools), prefix="/api")

    frontend_dir = Path(__file__).resolve().parents[2] / "frontend"
    if frontend_dir.exists():
        app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

        @app.get("/")
        async def index() -> FileResponse:
            return FileResponse(frontend_dir / "index.html")

    return app


app = create_app()


def main() -> None:
    import uvicorn

    uvicorn.run("backend.app.main:app", host=os.environ.get("HOST", "127.0.0.1"), port=int(os.environ.get("PORT", "8000")), reload=False)


if __name__ == "__main__":
    main()
