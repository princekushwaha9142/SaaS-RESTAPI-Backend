import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.main import app, limiter
from app.models.base import Base
from app.dependencies import get_db

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"


@pytest_asyncio.fixture(scope="session")
async def db_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(db_engine):
    session_factory = async_sessionmaker(db_engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    limiter.enabled = False

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c

    app.dependency_overrides.clear()
    limiter.enabled = True


@pytest_asyncio.fixture(scope="function")
async def auth_client(client: AsyncClient):
    await client.post("/auth/register", json={
        "email": "test@example.com",
        "full_name": "Test User",
        "password": "password123",
    })
    resp = await client.post("/auth/login", data={
        "username": "test@example.com",
        "password": "password123",
    })
    data = resp.json()
    token = data["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    return client