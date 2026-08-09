import os
from pathlib import Path

TEST_DB = Path(__file__).parent / "test_ai_college.db"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB}"

import pytest
from httpx import ASGITransport, AsyncClient

from app.database import Base, SessionLocal, engine
from app.main import app
from app.seed import seed_database


@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_database(db)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as test_client:
        yield test_client
