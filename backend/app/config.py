from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    app_name: str = "hazrat"
    app_version: str = "0.1.0"
    debug: bool = True
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174"
    llm_provider: str = "ollama"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:1.5b"
    llm_system_prompt: str = (
        "You are AI College Assistant, a helpful local general-purpose assistant. "
        "Answer normally and concisely. Do not invent facts about the college. must give the answer in very few lines like one or tell unlesss asked specifically to answer in detail. Always answer concisely and fast" 
    )
    llm_temperature: float = 0.7
    llm_max_tokens: int = 512
    llm_timeout: float = 120.0
    llm_max_input_characters: int = 8000

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env", env_file_encoding="utf-8", extra="ignore"
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
