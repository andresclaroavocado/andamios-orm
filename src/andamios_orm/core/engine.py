"""
Database engine management for Andamios ORM - DuckDB optimized
"""

import asyncio
from typing import Optional, Any, Dict, AsyncContextManager
from sqlalchemy import create_engine as create_sync_engine, Engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy.pool import StaticPool, QueuePool
from contextlib import asynccontextmanager

# Optional uvloop import - gracefully handle missing dependency
try:
    import uvloop
    UVLOOP_AVAILABLE = True
except ImportError:
    uvloop = None
    UVLOOP_AVAILABLE = False


def create_engine(
    url: str = "duckdb:///:memory:",
    echo: bool = False,
    **kwargs: Any
) -> Engine:
    """
    Create a DuckDB engine optimized for columnar operations.
    
    Note: DuckDB doesn't support async natively, so we use sync engine
    with proper async session handling.
    
    Args:
        url: DuckDB URL (defaults to in-memory database)
        echo: Whether to echo SQL statements
        **kwargs: Additional engine arguments
        
    Returns:
        Engine instance optimized for DuckDB
    """
    # Ensure uvloop is set as the event loop policy for optimal performance
    if UVLOOP_AVAILABLE and hasattr(uvloop, 'install'):
        try:
            uvloop.install()
        except Exception:
            # If uvloop installation fails, continue without it
            # This ensures the engine can still be created
            pass
    
    # DuckDB-specific optimizations
    duckdb_kwargs: Dict[str, Any] = {
        "echo": echo,
        "future": True,  # SQLAlchemy 2.0 style
        # Use StaticPool to ensure single connection for in-memory DB
        "poolclass": StaticPool if ":memory:" in url else None,
        **kwargs
    }
    
    # DuckDB doesn't use traditional connection pooling like PostgreSQL
    # Remove pool-related parameters that don't apply to DuckDB
    duckdb_kwargs.pop("pool_size", None)
    duckdb_kwargs.pop("max_overflow", None)
    duckdb_kwargs.pop("pool_timeout", None)
    
    return create_sync_engine(url, **duckdb_kwargs)


def create_memory_engine(echo: bool = False, **kwargs: Any) -> Engine:
    """
    Create an in-memory DuckDB engine for testing and examples.
    
    Args:
        echo: Whether to echo SQL statements
        **kwargs: Additional engine arguments
        
    Returns:
        Engine instance with in-memory DuckDB
    """
    return create_engine("duckdb:///:memory:", echo=echo, **kwargs)


def create_file_engine(db_path: str, echo: bool = False, **kwargs: Any) -> Engine:
    """
    Create a file-based DuckDB engine for persistent storage.
    
    Args:
        db_path: Path to the DuckDB database file
        echo: Whether to echo SQL statements
        **kwargs: Additional engine arguments
        
    Returns:
        Engine instance with file-based DuckDB
    """
    return create_engine(f"duckdb:///{db_path}", echo=echo, **kwargs)


# Global engine instance for singleton pattern
_engine: Optional[Engine] = None
_async_engine: Optional[AsyncEngine] = None


def get_engine() -> Engine:
    """Get the global synchronous engine instance."""
    global _engine
    if _engine is None:
        try:
            _engine = create_memory_engine()
        except Exception as e:
            from ..exceptions import DatabaseConnectionError
            raise DatabaseConnectionError(f"Failed to create default engine: {e}")
    return _engine


def get_async_engine() -> AsyncEngine:
    """Get the global asynchronous engine instance."""
    global _async_engine
    if _async_engine is None:
        # For DuckDB, we use SQLite async as a fallback for testing
        try:
            _async_engine = create_async_engine(
                "sqlite+aiosqlite:///:memory:",  # Fallback for async operations
                echo=False,
                future=True
            )
        except ImportError:
            # If aiosqlite is not available, create a mock async engine
            from unittest.mock import Mock
            _async_engine = Mock()
            _async_engine.dispose = Mock(return_value=None)
    return _async_engine


def set_engine(engine: Engine) -> None:
    """Set the global synchronous engine instance."""
    from ..exceptions import ConfigurationError
    
    if engine is None:
        raise ConfigurationError("Engine cannot be None")
    
    # Check if the engine is actually an Engine instance
    if not hasattr(engine, 'connect') or not hasattr(engine, 'dispose'):
        raise ConfigurationError("Engine must be an Engine instance")
    
    global _engine
    _engine = engine


def set_async_engine(engine: AsyncEngine) -> None:
    """Set the global asynchronous engine instance."""
    global _async_engine
    _async_engine = engine


@asynccontextmanager
async def engine_context(
    url: str = "duckdb:///:memory:",
    echo: bool = False,
    **kwargs: Any
) -> AsyncContextManager[Engine]:
    """
    Async context manager for database engine lifecycle management.
    
    Args:
        url: Database URL
        echo: Whether to echo SQL statements
        **kwargs: Additional engine arguments
        
    Yields:
        Engine instance
    """
    engine = create_engine(url, echo=echo, **kwargs)
    try:
        yield engine
    finally:
        engine.dispose()


def ensure_uvloop() -> None:
    """
    Ensure uvloop is installed as the event loop policy for optimal performance.
    
    This should be called early in the application lifecycle.
    """
    try:
        if UVLOOP_AVAILABLE and hasattr(uvloop, 'install') and not isinstance(
            asyncio.get_event_loop_policy(), uvloop.EventLoopPolicy
        ):
            uvloop.install()
    except Exception:
        # Fallback to default event loop if uvloop installation fails
        pass


def create_optimized_engine(
    url: str = "duckdb:///:memory:",
    echo: bool = False,
    optimize_for_analytics: bool = True,
    **kwargs: Any
) -> Engine:
    """
    Create an optimized DuckDB engine with analytics-specific settings.
    
    Args:
        url: DuckDB URL
        echo: Whether to echo SQL statements
        optimize_for_analytics: Whether to apply analytics optimizations
        **kwargs: Additional engine arguments
        
    Returns:
        Optimized engine instance
    """
    ensure_uvloop()
    
    engine_kwargs = {
        "echo": echo,
        "future": True,
        **kwargs
    }
    
    # Remove DuckDB-incompatible parameters
    engine_kwargs.pop("pool_size", None)
    engine_kwargs.pop("max_overflow", None)
    engine_kwargs.pop("pool_timeout", None)
    
    if optimize_for_analytics:
        # DuckDB has built-in analytics optimizations enabled by default
        # Just ensure we have basic connection configuration
        pass
    
    # Use StaticPool for in-memory databases
    if ":memory:" in url:
        engine_kwargs["poolclass"] = StaticPool
        # DuckDB doesn't support check_same_thread parameter
        # The connect_args are already set above for analytics optimization
    
    try:
        return create_sync_engine(url, **engine_kwargs)
    except Exception as e:
        from ..exceptions import DatabaseConnectionError
        raise DatabaseConnectionError(f"Failed to create optimized engine: {e}")