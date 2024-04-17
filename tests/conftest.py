import asyncio

import pytest
from httpx import AsyncClient, ASGITransport

from app.db.connect_db import get_session
from app.main import app


@pytest.fixture
async def event_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture
def client():
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


@pytest.fixture
async def db():
    async with get_session() as session:
        yield session
