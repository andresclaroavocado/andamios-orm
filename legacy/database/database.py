"""
Database setup for Web-Based Project Architect - DuckDB Reference
"""

import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

# Create declarative base for models
Base = declarative_base()

# Database configuration - DuckDB
DATABASE_URL = "duckdb+duckdb_engine:///:memory:"

# Create engine
engine = create_async_engine(DATABASE_URL, echo=False, future=True)

# Create session maker
SessionLocal = async_sessionmaker(engine, class_=AsyncSession)


async def get_database() -> AsyncGenerator[AsyncSession, None]:
    """Get database session"""
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_database():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)