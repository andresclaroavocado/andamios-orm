"""
Session management for Andamios ORM
"""

from typing import Type, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession as SQLAlchemyAsyncSession, async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncEngine

from .engine import create_memory_engine

# Global engine and session maker - initialized automatically
_global_engine: Optional[AsyncEngine] = None
_global_sessionmaker: Optional[async_sessionmaker] = None


def init_db(engine: Optional[AsyncEngine] = None) -> None:
    """Initialize the global database engine and session maker.
    
    Args:
        engine: Optional engine to use. If None, creates a memory engine.
    """
    global _global_engine, _global_sessionmaker
    
    if engine is None:
        engine = create_memory_engine()
    
    _global_engine = engine
    _global_sessionmaker = async_sessionmaker(
        engine,
        class_=SQLAlchemyAsyncSession,
        expire_on_commit=False
    )


async def get_session() -> SQLAlchemyAsyncSession:
    """Get a database session. Initializes DB automatically if needed."""
    global _global_engine, _global_sessionmaker
    
    if _global_sessionmaker is None:
        init_db()
    
    # Auto-create tables if they don't exist
    if _global_engine is not None:
        from ..models.base import Base
        async with _global_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    return _global_sessionmaker()


def sessionmaker(
    engine: AsyncEngine,
    class_: Type[SQLAlchemyAsyncSession] = SQLAlchemyAsyncSession,
    **kwargs: Any
) -> async_sessionmaker[SQLAlchemyAsyncSession]:
    """
    Create an async session maker.
    
    Args:
        engine: Database engine
        class_: Session class to use
        **kwargs: Additional session arguments
        
    Returns:
        Async session maker
    """
    return async_sessionmaker(
        engine,
        class_=class_,
        **kwargs
    )


# Re-export AsyncSession for convenience
AsyncSession = SQLAlchemyAsyncSession