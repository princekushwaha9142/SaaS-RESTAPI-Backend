import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_register(client: AsyncClient):
    resp = await client.post("/auth/register", json={
        "email": "newuser@example.com",
        "full_name": "New User",
        "password": "securepass",
    })
    assert resp.status_code == 201
    assert resp.json()["email"] == "newuser@example.com"
    assert "hashed_password" not in resp.json()


async def test_register_duplicate_email(client: AsyncClient):
    payload = {"email": "dup@example.com", "full_name": "Dup", "password": "pass1234"}
    await client.post("/auth/register", json=payload)
    resp = await client.post("/auth/register", json=payload)
    assert resp.status_code == 409


async def test_register_weak_password(client: AsyncClient):
    resp = await client.post("/auth/register", json={
        "email": "weak@example.com", "full_name": "Weak", "password": "short",
    })
    assert resp.status_code == 422


async def test_login_success(auth_client: AsyncClient):
    resp = await auth_client.get("/auth/me")
    assert resp.status_code == 200
    assert resp.json()["email"] == "test@example.com"


async def test_login_wrong_password(client: AsyncClient):
    await client.post("/auth/register", json={
        "email": "wrongpw@example.com", "full_name": "X", "password": "correct123",
    })
    resp = await client.post("/auth/login", data={
        "username": "wrongpw@example.com", "password": "wrongpass",
    })
    assert resp.status_code == 401


async def test_protected_without_token(client: AsyncClient):
    resp = await client.get("/auth/me")
    assert resp.status_code == 401


async def test_refresh_token(client: AsyncClient):
    await client.post("/auth/register", json={
        "email": "refresh@example.com", "full_name": "R", "password": "pass1234",
    })
    login = await client.post("/auth/login", data={
        "username": "refresh@example.com", "password": "pass1234",
    })
    refresh_token = login.json()["refresh_token"]
    resp = await client.post(f"/auth/refresh?refresh_token={refresh_token}")
    assert resp.status_code == 200
    assert "access_token" in resp.json()