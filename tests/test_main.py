import pytest
from httpx import AsyncClient
from app.main import app
from app.schemas.users import UserCreateSchema


@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "status_code": 200,
        "detail": "ok",
        "result": "working"
    }


@pytest.mark.asyncio
async def test_get_all_users_router():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/users/")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_create_user():
    user_data = UserCreateSchema(username="Вася", email="testuser@example.com", password="password")
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/users/", json=user_data.dict())
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "Вася"
    assert data["email"] == "testuser@example.com"
