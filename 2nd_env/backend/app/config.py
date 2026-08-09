from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path


@dataclass(slots=True)
class AppConfig:
    llm_provider: str = "ollama"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = ""
    max_tool_calls: int = 3
    app_title: str = "AI College Local"
    data_dir: Path = Path("data")


def load_config() -> AppConfig:
    return AppConfig(
        llm_provider=os.environ.get("LLM_PROVIDER", "ollama").strip() or "ollama",
        ollama_base_url=os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434").strip(),
        ollama_model=os.environ.get("OLLAMA_MODEL", "").strip(),
        max_tool_calls=max(1, int(os.environ.get("AGENT_MAX_TOOL_CALLS", "3"))),
        app_title=os.environ.get("APP_TITLE", "AI College Local").strip() or "AI College Local",
        data_dir=Path(os.environ.get("APP_DATA_DIR", "data")),
    )
