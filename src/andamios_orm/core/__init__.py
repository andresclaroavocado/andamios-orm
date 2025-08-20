"""
Core ORM functionality for Andamios ORM - DuckDB optimized
"""

from .engine import create_engine, create_memory_engine, create_file_engine, get_engine, create_optimized_engine
from .session import sessionmaker, AsyncSession, get_session, init_db, session_scope, transaction_scope, SessionManager
from .database import (
    DatabaseInitializer, 
    initialize_database, 
    create_tables, 
    drop_tables, 
    verify_database_schema,
    get_database_initializer
)

__all__ = [
    # Engine
    "create_engine", 
    "create_memory_engine", 
    "create_file_engine", 
    "get_engine",
    "create_optimized_engine",
    # Session
    "sessionmaker", 
    "AsyncSession", 
    "get_session", 
    "init_db",
    "session_scope",
    "transaction_scope",
    "SessionManager",
    # Database
    "DatabaseInitializer",
    "initialize_database",
    "create_tables",
    "drop_tables", 
    "verify_database_schema",
    "get_database_initializer"
]