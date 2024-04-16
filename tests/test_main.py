import pytest
from httpx import AsyncClient
from app.main import app
from app.db.connect_db import get_session
from app.schemas.users import UserCreateSchema, UserUpdateRequestSchema


@pytest.fixture
def client():
    return AsyncClient(app=app, base_url="http://test")


@pytest.fixture
async def db():
    async with get_session() as session:
        yield session


@pytest.mark.asyncio
async def test_create_user(client, db):
    user_data = UserCreateSchema(username="TestUser", email="testuser@example.com", password="password")
    response = await client.post("/users/", json=user_data.dict())
    assert response.status_code == 201
    created_user = response.json()
    assert created_user["username"] == "TestUser"
    assert created_user["email"] == "testuser@example.com"
    return created_user["id"]



@pytest.mark.asyncio
async def test_delete_user_router(client):
    user_id = await test_create_user(client, db=db())
    response = await client.delete(f"/users/{user_id}")
    assert response.status_code == 204
    await client.aclose()