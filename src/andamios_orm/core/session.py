"""
Session management for Andamios ORM
"""

import asyncio
from typing import Type, Optional, Any
from sqlalchemy import Engine
from sqlalchemy.orm import sessionmaker as sync_sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

from .engine import create_memory_engine
from ..exceptions import DatabaseConnectionError
from ..logging import get_logger

# Global engine and session maker - initialized automatically
_global_engine: Optional[Engine] = None
_global_sessionmaker: Optional[sync_sessionmaker] = None

logger = get_logger("session")


def init_db(engine: Optional[Engine] = None) -> None:
    """Initialize the global database engine and session maker.
    
    Args:
        engine: Optional engine to use. If None, creates a memory engine.
    """
    global _global_engine, _global_sessionmaker
    
    if engine is None:
        engine = create_memory_engine()
    
    _global_engine = engine
    _global_sessionmaker = sync_sessionmaker(
        engine,
        expire_on_commit=False
    )


class AsyncSessionWrapper:
    """Wrapper to provide async interface for sync SQLAlchemy session."""
    
    def __init__(self, session: Session):
        self._session = session
    
    async def add(self, instance):
        """Add instance to session."""
        try:
            await asyncio.to_thread(self._session.add, instance)
        except SQLAlchemyError as e:
            logger.error(f"Failed to add instance to session: {e}")
            raise DatabaseConnectionError(f"Failed to add instance: {e}")
    
    async def commit(self):
        """Commit the session."""
        try:
            await asyncio.to_thread(self._session.commit)
        except SQLAlchemyError as e:
            logger.error(f"Failed to commit session: {e}")
            raise DatabaseConnectionError(f"Failed to commit: {e}")
    
    async def rollback(self):
        """Rollback the session."""
        try:
            await asyncio.to_thread(self._session.rollback)
        except SQLAlchemyError as e:
            logger.error(f"Failed to rollback session: {e}")
            raise DatabaseConnectionError(f"Failed to rollback: {e}")
    
    async def refresh(self, instance):
        """Refresh instance from database."""
        try:
            await asyncio.to_thread(self._session.refresh, instance)
        except SQLAlchemyError as e:
            logger.error(f"Failed to refresh instance: {e}")
            raise DatabaseConnectionError(f"Failed to refresh: {e}")
    
    async def get(self, model_class, id):
        """Get model by ID."""
        try:
            return await asyncio.to_thread(self._session.get, model_class, id)
        except SQLAlchemyError as e:
            logger.error(f"Failed to get instance: {e}")
            raise DatabaseConnectionError(f"Failed to get: {e}")
    
    async def delete(self, instance):
        """Delete instance from session."""
        try:
            await asyncio.to_thread(self._session.delete, instance)
        except SQLAlchemyError as e:
            logger.error(f"Failed to delete instance: {e}")
            raise DatabaseConnectionError(f"Failed to delete: {e}")
    
    async def close(self):
        """Close the session."""
        try:
            await asyncio.to_thread(self._session.close)
        except SQLAlchemyError as e:
            logger.error(f"Failed to close session: {e}")
            raise DatabaseConnectionError(f"Failed to close: {e}")


async def get_session() -> AsyncSessionWrapper:
    """Get a database session. Initializes DB automatically if needed."""
    global _global_engine, _global_sessionmaker
    
    if _global_sessionmaker is None:
        init_db()
    
    # Auto-create tables if they don't exist
    if _global_engine is not None:
        # Create tables using DuckDB-compatible DDL
        await _create_tables_duckdb_compatible(_global_engine)
    
    session = _global_sessionmaker()
    return AsyncSessionWrapper(session)


async def _create_tables_duckdb_compatible(engine):
    """Create tables using DuckDB-compatible DDL."""
    ddl_statements = [
        """
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            project_idea TEXT NOT NULL,
            architecture JSON,
            status VARCHAR(50) DEFAULT 'draft',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY,
            project_id INTEGER,
            phase VARCHAR(100) DEFAULT 'project_idea',
            messages JSON DEFAULT '[]',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY,
            project_id INTEGER,
            name VARCHAR(255) NOT NULL,
            content TEXT,
            doc_type VARCHAR(100),
            file_path VARCHAR(500),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS repositories (
            id INTEGER PRIMARY KEY,
            project_id INTEGER,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            repo_type VARCHAR(100),
            github_url VARCHAR(500),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP
        )
        """
    ]
    
    from sqlalchemy import text
    
    def execute_ddl():
        with engine.connect() as conn:
            for ddl in ddl_statements:
                conn.execute(text(ddl.strip()))
            conn.commit()
    
    await asyncio.to_thread(execute_ddl)


def sessionmaker(
    engine: Engine,
    **kwargs: Any
) -> sync_sessionmaker:
    """
    Create a session maker.
    
    Args:
        engine: Database engine
        **kwargs: Additional session arguments
        
    Returns:
        Session maker
    """
    return sync_sessionmaker(
        engine,
        **kwargs
    )


# Re-export AsyncSession wrapper for convenience
AsyncSession = AsyncSessionWrapper