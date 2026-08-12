from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import ai, health
from app.config import get_settings
settings = get_settings()

app = FastAPI(title=settings.app_name, version=settings.app_version, description="Minimal local LLM chat API.")
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origin_list, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(health.router, prefix="/api")
app.include_router(ai.router, prefix="/api")
