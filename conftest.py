"""
Pytest configuration file.
"""

from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.database import Base
from app.core.database import get_session
from app.main import app


def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line(
        "markers", "asyncio: mark test as async"
    )


@pytest.fixture
def test_settings():
    """Fixture for test settings."""
    from app.core.config import Settings
    
    return Settings(
        DEBUG=True,
        ENVIRONMENT="testing",
        DATABASE_URL="sqlite+aiosqlite:///:memory:",
        DB_ECHO=False,
    )


@pytest.fixture
async def db_session() -> AsyncIterator[AsyncSession]:
    """Provide an isolated async SQLite session for service tests."""
    engine = create_async_engine("sqlite+aiosqlite:///./.test_db.sqlite3")
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    async with session_factory() as session:
        yield session
        await session.rollback()

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def api_client(db_session: AsyncSession) -> AsyncIterator[AsyncClient]:
    """Provide an async HTTP client against the FastAPI app with a test DB session."""

    async def override_get_session() -> AsyncIterator[AsyncSession]:
        try:
            yield db_session
            await db_session.commit()
        except Exception:
            await db_session.rollback()
            raise

    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        yield client

    app.dependency_overrides.pop(get_session, None)
