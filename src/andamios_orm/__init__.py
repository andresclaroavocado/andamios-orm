"""
Andamios ORM - A modern, async-first Python ORM library built for DuckDB

This library provides a clean and intuitive interface for DuckDB database operations
with full async/await support, uvloop optimization, and comprehensive type safety.

Key Features:
- Async-first design with uvloop optimization for maximum performance
- Built specifically for DuckDB's columnar architecture  
- Comprehensive type safety with full mypy support
- Simple Active Record pattern with Model.create(), Model.read(), etc.
- Advanced session management with connection pooling
- Automatic table creation and schema management
- Comprehensive error handling and logging

Quick Start:
    ```python
    import asyncio
    from andamios_orm import Model, initialize_database
    
    class User(Model):
        __tablename__ = "users"
        id = Column(Integer, primary_key=True)
        name = Column(String(255), nullable=False)
        email = Column(String(255), unique=True)
    
    async def main():
        await initialize_database()
        user = await User.create(name="John", email="john@example.com")
        found_user = await User.read(user.id)
        print(f"Found: {found_user.name}")
    
    asyncio.run(main())
    ```

API Structure:
- Engine API: Database engine creation and configuration
- Session API: Session management and transaction handling  
- Database API: Schema management and initialization
- Models API: Active Record pattern and model definitions
- Exception API: Comprehensive error handling
- Logging API: Structured logging with configurable levels
"""

from .core import (
    # Engine
    create_engine, create_memory_engine, create_file_engine, get_engine, create_optimized_engine,
    # Session
    sessionmaker, AsyncSession, get_session, init_db, session_scope, transaction_scope, SessionManager,
    # Database
    DatabaseInitializer, initialize_database, create_tables, drop_tables, verify_database_schema
)
from .models import Model, Base, Project, Conversation, Document, Repository
from .exceptions import (
    AndamiosORMException, ValidationError, NotFoundError, 
    DatabaseConnectionError, DatabaseOperationError, ConfigurationError
)
from .logging import setup_logging, get_logger

# Package metadata
__version__ = "0.1.0"
__author__ = "andresclaroavocado"
__email__ = "andres.claro@avocadoblock.com"
__description__ = "A modern, async-first Python ORM library built for DuckDB"
__url__ = "https://github.com/andresclaroavocado/andamios-orm"
__license__ = "MIT"

# Compatibility imports for SQLAlchemy
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON

__all__ = [
    # Engine API
    "create_engine", 
    "create_memory_engine", 
    "create_file_engine", 
    "get_engine",
    "create_optimized_engine",
    
    # Session API
    "sessionmaker", 
    "AsyncSession", 
    "get_session", 
    "init_db",
    "session_scope",
    "transaction_scope", 
    "SessionManager",
    
    # Database API
    "DatabaseInitializer",
    "initialize_database",
    "create_tables", 
    "drop_tables", 
    "verify_database_schema",
    
    # Models API
    "Model", 
    "Base", 
    "Project", 
    "Conversation", 
    "Document", 
    "Repository",
    
    # Exception handling
    "AndamiosORMException", 
    "ValidationError", 
    "NotFoundError", 
    "DatabaseConnectionError", 
    "DatabaseOperationError", 
    "ConfigurationError",
    
    # Logging utilities  
    "setup_logging", 
    "get_logger",
    
    # SQLAlchemy column types (for convenience)
    "Column",
    "Integer", 
    "String", 
    "Text", 
    "DateTime", 
    "Boolean", 
    "JSON",
]