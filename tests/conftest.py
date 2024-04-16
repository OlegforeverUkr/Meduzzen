import pytest
from httpx import AsyncClient, ASGITransport

from app.db.connect_db import get_session
from app.main import app


@pytest.fixture
def client():
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


@pytest.fixture
async def db():
    async with get_session() as session:
        yield session
