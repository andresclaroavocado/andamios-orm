"""
Session management for Andamios ORM
"""

import asyncio
from typing import Type, Optional, Any, AsyncContextManager, Callable
from contextlib import asynccontextmanager
from sqlalchemy import Engine, text
from sqlalchemy.orm import sessionmaker as sync_sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession as SQLAlchemyAsyncSession

from .engine import get_engine, set_engine, create_memory_engine
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
    
    async def execute(self, statement, parameters=None):
        """Execute a SQL statement."""
        try:
            if parameters:
                return await asyncio.to_thread(self._session.execute, statement, parameters)
            else:
                return await asyncio.to_thread(self._session.execute, statement)
        except SQLAlchemyError as e:
            logger.error(f"Failed to execute statement: {e}")
            raise DatabaseConnectionError(f"Failed to execute: {e}")
    
    async def bulk_insert_mappings(self, model_class, mappings):
        """Bulk insert mappings."""
        try:
            await asyncio.to_thread(self._session.bulk_insert_mappings, model_class, mappings)
        except SQLAlchemyError as e:
            logger.error(f"Failed to bulk insert: {e}")
            raise DatabaseConnectionError(f"Failed to bulk insert: {e}")
    
    async def bulk_update_mappings(self, model_class, mappings):
        """Bulk update mappings."""
        try:
            await asyncio.to_thread(self._session.bulk_update_mappings, model_class, mappings)
        except SQLAlchemyError as e:
            logger.error(f"Failed to bulk update: {e}")
            raise DatabaseConnectionError(f"Failed to bulk update: {e}")
    
    async def close(self):
        """Close the session."""
        try:
            await asyncio.to_thread(self._session.close)
        except SQLAlchemyError as e:
            logger.error(f"Failed to close session: {e}")
            raise DatabaseConnectionError(f"Failed to close: {e}")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        asyncio.create_task(self.close())
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if exc_type is not None:
            await self.rollback()
        await self.close()


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


@asynccontextmanager
async def session_scope() -> AsyncContextManager[AsyncSessionWrapper]:
    """
    Provide a transactional scope around a series of operations.
    
    Usage:
        async with session_scope() as session:
            # do work
            await session.commit()
    """
    session = await get_session()
    try:
        yield session
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


@asynccontextmanager
async def transaction_scope() -> AsyncContextManager[AsyncSessionWrapper]:
    """
    Provide an auto-committing transactional scope.
    
    Usage:
        async with transaction_scope() as session:
            # do work - auto commits on success, rollbacks on exception
    """
    session = await get_session()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


async def with_session(func: Callable[[AsyncSessionWrapper], Any]) -> Any:
    """
    Execute a function with a session, handling cleanup automatically.
    
    Args:
        func: Function that takes a session and returns a value
        
    Returns:
        Result of the function
    """
    async with session_scope() as session:
        return await func(session)


async def with_transaction(func: Callable[[AsyncSessionWrapper], Any]) -> Any:
    """
    Execute a function within a transaction, handling commit/rollback automatically.
    
    Args:
        func: Function that takes a session and returns a value
        
    Returns:
        Result of the function
    """
    async with transaction_scope() as session:
        return await func(session)


class SessionManager:
    """Advanced session manager with connection pooling and lifecycle management."""
    
    def __init__(self, engine: Optional[Engine] = None):
        self.engine = engine or get_engine()
        self.sessionmaker = sync_sessionmaker(
            self.engine,
            expire_on_commit=False
        )
    
    @asynccontextmanager
    async def session(self) -> AsyncContextManager[AsyncSessionWrapper]:
        """Get a session with automatic cleanup."""
        session = AsyncSessionWrapper(self.sessionmaker())
        try:
            yield session
        finally:
            await session.close()
    
    @asynccontextmanager
    async def transaction(self) -> AsyncContextManager[AsyncSessionWrapper]:
        """Get a session with automatic transaction handling."""
        async with self.session() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
    
    async def execute_raw_sql(self, sql: str, parameters: Optional[dict] = None) -> Any:
        """Execute raw SQL with proper session management."""
        async with self.session() as session:
            result = await session.execute(text(sql), parameters)
            return result
    
    async def bulk_operations(self, operations: list[Callable[[AsyncSessionWrapper], Any]]) -> list[Any]:
        """Execute multiple operations in a single transaction."""
        async with self.transaction() as session:
            results = []
            for operation in operations:
                result = await operation(session)
                results.append(result)
            return results


# Global session manager instance
_session_manager: Optional[SessionManager] = None


def get_session_manager() -> SessionManager:
    """Get the global session manager instance."""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager


def set_session_manager(manager: SessionManager) -> None:
    """Set the global session manager instance."""
    global _session_manager
    _session_manager = manager


# Re-export AsyncSession wrapper for convenience
AsyncSession = AsyncSessionWrapper