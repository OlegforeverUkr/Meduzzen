import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from unittest.mock import MagicMock


@pytest.fixture
def client():
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


@pytest.fixture
async def mocker():
    session = MagicMock()
    yield session