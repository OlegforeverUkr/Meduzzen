import pytest
from unittest.mock import MagicMock


@pytest.mark.asyncio
async def test_health_check(client, mocker):
    mocked_session = MagicMock()
    mocker.patch('app.routes.get_session', return_value=mocked_session)
    response = await client.get("/")

    assert response.status_code == 200
    assert response.json() == {"status_code": 200, "detail": "ok", "result": "working"}


@pytest.mark.asyncio
async def test_create_user(client, mocker):
    mocked_session = MagicMock()
    mocker.patch('app.routes.get_session', return_value=mocked_session)

    user_data = {"username": "testuser", "email": "testuser@example.com", "password": "test12453!"}
    response = await client.post("/users/", json=user_data)

    assert response.status_code == 201
    assert response.json()["username"] == user_data["username"]
    assert response.json()["email"] == user_data["email"]

    user_id = response.json()["id"]
    await client.delete(f"/users/{user_id}")

