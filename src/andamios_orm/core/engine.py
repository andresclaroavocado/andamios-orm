"""
Database engine management for Andamios ORM - DuckDB optimized
"""

import uvloop
import asyncio
from typing import Optional, Any, Dict
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine


def create_engine(
    url: str = "duckdb+duckdb_engine:///:memory:",
    echo: bool = False,
    **kwargs: Any
) -> AsyncEngine:
    """
    Create an async DuckDB engine optimized for columnar operations.
    
    Args:
        url: DuckDB URL (defaults to in-memory database)
        echo: Whether to echo SQL statements
        **kwargs: Additional engine arguments
        
    Returns:
        AsyncEngine instance optimized for DuckDB
    """
    # Ensure uvloop is set as the event loop policy for optimal performance
    if hasattr(uvloop, 'install'):
        uvloop.install()
    
    # DuckDB-specific optimizations
    duckdb_kwargs: Dict[str, Any] = {
        "echo": echo,
        "future": True,  # SQLAlchemy 2.0 style
        **kwargs
    }
    
    # DuckDB doesn't use traditional connection pooling like PostgreSQL
    # Remove pool-related parameters that don't apply to DuckDB
    duckdb_kwargs.pop("pool_size", None)
    duckdb_kwargs.pop("max_overflow", None)
    
    return create_async_engine(url, **duckdb_kwargs)


def create_memory_engine(echo: bool = False, **kwargs: Any) -> AsyncEngine:
    """
    Create an in-memory DuckDB engine for testing and examples.
    
    Args:
        echo: Whether to echo SQL statements
        **kwargs: Additional engine arguments
        
    Returns:
        AsyncEngine instance with in-memory DuckDB
    """
    return create_engine("duckdb+duckdb_engine:///:memory:", echo=echo, **kwargs)


def create_file_engine(db_path: str, echo: bool = False, **kwargs: Any) -> AsyncEngine:
    """
    Create a file-based DuckDB engine for persistent storage.
    
    Args:
        db_path: Path to the DuckDB database file
        echo: Whether to echo SQL statements
        **kwargs: Additional engine arguments
        
    Returns:
        AsyncEngine instance with file-based DuckDB
    """
    return create_engine(f"duckdb+duckdb_engine:///{db_path}", echo=echo, **kwargs)