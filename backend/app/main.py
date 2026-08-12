import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import access, ai, devices, events, health, rooms, speech, system
from app.config import get_settings
from app.database import Base, SessionLocal, engine
from app import models  # noqa: F401 - registers SQLAlchemy models
from app.seed import seed_database

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")
logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_database(db)
    logger.info("AI College database initialized")
    yield


app = FastAPI(title=settings.app_name, version=settings.app_version, description="Local AI College infrastructure foundation.", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origin_list, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(health.router, prefix="/api")
app.include_router(access.router, prefix="/api")
app.include_router(system.router, prefix="/api")
app.include_router(ai.router, prefix="/api")
app.include_router(speech.router, prefix="/api")
app.include_router(rooms.router, prefix="/api")
app.include_router(devices.router, prefix="/api")
app.include_router(events.router, prefix="/api")
