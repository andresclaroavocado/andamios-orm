"""
Andamios ORM - A modern, async-first Python ORM library built for DuckDB

This is the main package for the Andamios ORM library, providing
a clean and intuitive interface for DuckDB database operations with
async/await support and uvloop optimization.
"""

from .core import create_engine, create_memory_engine, create_file_engine, sessionmaker, AsyncSession, get_session, init_db
from .models.base import Model
from .simple import SimpleModel, Base, save, find_by_id, find_all, delete, create_tables, init_simple_orm

__version__ = "0.1.0"
__author__ = "andresclaroavocado"
__email__ = "andres.claro@avocadoblock.com"

__all__ = [
    # Core API (for advanced users)
    "create_engine", "create_memory_engine", "create_file_engine", "sessionmaker", "AsyncSession", "get_session", "init_db", "Model",
    # Simple API (for easy examples)
    "SimpleModel", "Base", "save", "find_by_id", "find_all", "delete", "create_tables", "init_simple_orm"
]