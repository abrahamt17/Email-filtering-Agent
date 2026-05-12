"""
Database connection and session management.
Provides async SQLAlchemy setup with connection pooling and lifecycle management.
"""

from typing import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool, QueuePool

from app.core.config import get_settings

# Base class for all ORM models
Base = declarative_base()

settings = get_settings()


async def create_db_engine() -> AsyncEngine:
    """
    Create async SQLAlchemy engine with proper configuration.
    
    Returns:
        AsyncEngine: Configured async SQLAlchemy engine
    """
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DB_ECHO,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        pool_pre_ping=settings.DB_POOL_PRE_PING,
        pool_recycle=3600,  # Recycle connections every hour
        # In production, use QueuePool; in testing, use NullPool
        poolclass=NullPool if settings.DEBUG else QueuePool,
    )
    return engine


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting database session in FastAPI routes.
    Automatically manages transaction lifecycle.
    
    Yields:
        AsyncSession: Database session for queries
    """
    engine = await create_db_engine()
    async_session = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
            await engine.dispose()


class DatabaseManager:
    """Manager class for database lifecycle and operations."""

    def __init__(self):
        self.engine: AsyncEngine | None = None
        self.async_session_maker: sessionmaker | None = None

    async def initialize(self):
        """Initialize database engine and session factory."""
        self.engine = await create_db_engine()
        self.async_session_maker = sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    async def dispose(self):
        """Dispose of database connections."""
        if self.engine:
            await self.engine.dispose()

    async def create_all_tables(self):
        """Create all database tables based on models."""
        if not self.engine:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_all_tables(self):
        """Drop all database tables. USE WITH CAUTION - Only for testing/development."""
        if not self.engine:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    def get_session_maker(self):
        """Get session factory."""
        if not self.async_session_maker:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        return self.async_session_maker

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Get a database session.
        
        Yields:
            AsyncSession: Database session
        """
        if not self.async_session_maker:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        
        async with self.async_session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()


# Global database manager instance
db_manager = DatabaseManager()
