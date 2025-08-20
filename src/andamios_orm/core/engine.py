"""
Database engine management for Andamios ORM - DuckDB optimized
"""

import uvloop
import asyncio
from typing import Optional, Any, Dict
from sqlalchemy import create_engine as create_sync_engine, Engine
from sqlalchemy.pool import StaticPool


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
    if hasattr(uvloop, 'install'):
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