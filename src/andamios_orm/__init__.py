"""
Andamios ORM - A modern, async-first Python ORM library built for DuckDB

This is the main package for the Andamios ORM library, providing
a clean and intuitive interface for DuckDB database operations with
async/await support and uvloop optimization.
"""

from .core import create_engine, create_memory_engine, create_file_engine, sessionmaker, AsyncSession

__version__ = "0.1.0"
__author__ = "andresclaroavocado"
__email__ = "adnres.claro@avocadoblock.com"

__all__ = ["create_engine", "create_memory_engine", "create_file_engine", "sessionmaker", "AsyncSession"]