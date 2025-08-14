"""
Session management for Andamios ORM
"""

from typing import Type, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession as SQLAlchemyAsyncSession, async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncEngine


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