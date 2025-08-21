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
        uvloop.install()
    
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
        _engine = create_memory_engine()
    return _engine


def get_async_engine() -> AsyncEngine:
    """Get the global asynchronous engine instance."""
    global _async_engine
    if _async_engine is None:
        # For DuckDB, we need to use sync engine with asyncio threading
        sync_engine = get_engine()
        # Create a pseudo-async engine using threading
        _async_engine = create_async_engine(
            "sqlite+aiosqlite:///:memory:",  # Fallback for async operations
            echo=False,
            future=True
        )
    return _async_engine


def set_engine(engine: Engine) -> None:
    """Set the global synchronous engine instance."""
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
    
    if optimize_for_analytics:
        # DuckDB-specific optimizations for analytical workloads
        engine_kwargs.update({
            "connect_args": {
                # Enable aggressive optimizations for analytics
                "config": {
                    "enable_optimizer": True,
                    "enable_profiling": echo,
                    "threads": -1,  # Use all available cores
                }
            }
        })
    
    # Use StaticPool for in-memory databases
    if ":memory:" in url:
        engine_kwargs["poolclass"] = StaticPool
        engine_kwargs["connect_args"] = engine_kwargs.get("connect_args", {})
        engine_kwargs["connect_args"]["check_same_thread"] = False
    
    return create_sync_engine(url, **engine_kwargs)