import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch, MagicMock
from app.main import app

# ---- mock Redis so tests run without a real Redis server ----
@pytest.fixture(autouse=True)
def mock_redis(monkeypatch):
    mock_r = AsyncMock()
    mock_r.publish = AsyncMock()
    mock_r.lpush = AsyncMock()
    mock_r.ltrim = AsyncMock()
    mock_r.lrange = AsyncMock(return_value=[b'{"username":"Alice","message":"hi","room":"general"}'])
    mock_r.aclose = AsyncMock()

    mock_from_url = MagicMock(return_value=mock_r)
    monkeypatch.setattr("app.main.aioredis.from_url", mock_from_url)
    return mock_r

@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@pytest.mark.asyncio
async def test_send_message():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/send", params={
            "room": "general",
            "username": "Alice",
            "message": "Hello World"
        })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "sent"
    assert data["room"] == "general"
    assert data["username"] == "Alice"

@pytest.mark.asyncio
async def test_get_history():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/history/general")
    assert response.status_code == 200
    data = response.json()
    assert data["room"] == "general"
    assert isinstance(data["messages"], list)
    assert data["messages"][0]["username"] == "Alice"
