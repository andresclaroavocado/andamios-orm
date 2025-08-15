"""
Simple high-level API for andamios-orm

Provides easy-to-use functions that hide session/engine complexity from users.
This is what Grok suggested - abstract away the boilerplate setup.
"""

from typing import Optional, Type, TypeVar, Any
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

from .core import create_memory_engine, sessionmaker, AsyncSession
import asyncio

# Global setup - initialized once
_engine = None
_session_maker = None
_base = declarative_base()

T = TypeVar('T')

def init_simple_orm(database_url: Optional[str] = None):
    """Initialize the ORM with minimal setup. Call this once at app start."""
    global _engine, _session_maker
    
    if database_url:
        from .core import create_engine
        _engine = create_engine(database_url)
    else:
        _engine = create_memory_engine()
    
    _session_maker = sessionmaker(_engine, class_=AsyncSession)

def get_session():
    """Get a pre-configured session - hides all the complexity."""
    global _session_maker
    
    if _session_maker is None:
        init_simple_orm()  # Auto-initialize if not done
    
    return _session_maker()

# Simple base model
class SimpleModel(_base):
    """Simple base model that users can inherit from."""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)

# Synchronous wrapper functions for ultra-simple usage
def create_tables():
    """Create all tables - call once to set up database."""
    global _engine, _base
    
    if _engine is None:
        init_simple_orm()
    
    async def _create():
        async with _engine.begin() as conn:
            await conn.run_sync(_base.metadata.create_all)
    
    asyncio.run(_create())

def save(obj: Any) -> Any:
    """Save an object to database - ultra simple."""
    async def _save():
        session = get_session()
        try:
            session.add(obj)
            await session.commit()
            await session.refresh(obj)
            return obj
        finally:
            await session.close()
    
    return asyncio.run(_save())

def find_by_id(model_class: Type[T], id: int) -> Optional[T]:
    """Find object by ID - ultra simple."""
    async def _find():
        session = get_session()
        try:
            return await session.get(model_class, id)
        finally:
            await session.close()
    
    return asyncio.run(_find())

def find_all(model_class: Type[T]) -> list[T]:
    """Find all objects of a type - ultra simple."""
    async def _find_all():
        from sqlalchemy import select
        session = get_session()
        try:
            result = await session.execute(select(model_class))
            return result.scalars().all()
        finally:
            await session.close()
    
    return asyncio.run(_find_all())

def delete(obj: Any) -> None:
    """Delete an object - ultra simple."""
    async def _delete():
        session = get_session()
        try:
            await session.delete(obj)
            await session.commit()
        finally:
            await session.close()
    
    return asyncio.run(_delete())

# Export the base for user models
Base = _base