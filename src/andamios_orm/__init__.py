"""
Andamios ORM - A modern, async-first Python ORM library built for DuckDB

This is the main package for the Andamios ORM library, providing
a clean and intuitive interface for DuckDB database operations with
async/await support and uvloop optimization.
"""

from .core import create_engine, create_memory_engine, create_file_engine, sessionmaker, AsyncSession, get_session, init_db
from .models import Model, Base, Project, Conversation, Document, Repository
from .simple import SimpleModel, save, find_by_id, find_all, delete, create_tables, init_simple_orm
from .exceptions import (
    AndamiosORMException, ValidationError, NotFoundError, 
    DatabaseConnectionError, DatabaseOperationError, ConfigurationError
)
from .logging import setup_logging, get_logger

__version__ = "0.1.0"
__author__ = "andresclaroavocado"
__email__ = "andres.claro@avocadoblock.com"

__all__ = [
    # Core API (for advanced users)
    "create_engine", "create_memory_engine", "create_file_engine", "sessionmaker", "AsyncSession", "get_session", "init_db",
    # Models API (main API for examples)
    "Model", "Base", "Project", "Conversation", "Document", "Repository",
    # Exception handling
    "AndamiosORMException", "ValidationError", "NotFoundError", "DatabaseConnectionError", "DatabaseOperationError", "ConfigurationError",
    # Logging utilities
    "setup_logging", "get_logger",
    # Simple API (for easy examples)
    "SimpleModel", "save", "find_by_id", "find_all", "delete", "create_tables", "init_simple_orm"
]