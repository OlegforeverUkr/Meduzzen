import pytest


@pytest.mark.asyncio
async def test_health_check(client):
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status_code": 200, "detail": "ok", "result": "working"}


@pytest.mark.asyncio
async def test_create_user(client):
    user_data = {"username": "testuser", "email": "testuser@example.com", "password": "testpassword"}
    response = await client.post("/users/", json=user_data)
    assert response.status_code == 201
    assert response.json()["username"] == user_data["username"]
    assert response.json()["email"] == user_data["email"]