"""
Database initialization and schema management for Andamios ORM
"""

import asyncio
from typing import Optional, List, Dict, Any
from sqlalchemy import Engine, text, MetaData, Table, inspect
from sqlalchemy.exc import SQLAlchemyError

from .engine import get_engine, ensure_uvloop
from .session import get_session_manager
from ..models.base import Base
from ..exceptions import DatabaseOperationError
from ..logging import get_logger

logger = get_logger("database")


class DatabaseInitializer:
    """Handles database initialization, table creation, and schema management."""
    
    def __init__(self, engine: Optional[Engine] = None):
        self.engine = engine or get_engine()
        self.metadata = Base.metadata
    
    async def initialize_database(self, create_tables: bool = True, drop_existing: bool = False) -> None:
        """
        Initialize the database with proper schema.
        
        Args:
            create_tables: Whether to create tables automatically
            drop_existing: Whether to drop existing tables first
        """
        ensure_uvloop()
        logger.info("Initializing database...")
        
        try:
            if drop_existing:
                await self.drop_all_tables()
            
            if create_tables:
                await self.create_all_tables()
            
            await self.verify_schema()
            logger.info("Database initialization completed successfully")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise DatabaseOperationError(f"Failed to initialize database: {e}")
    
    async def create_all_tables(self) -> None:
        """Create all tables defined in the metadata."""
        logger.info("Creating database tables...")
        
        def _create_tables():
            # Check if we're using Base metadata (our default) or custom metadata
            if self.metadata is Base.metadata:
                # Use DuckDB-compatible DDL statements for Base metadata
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
                
                with self.engine.connect() as conn:
                    for ddl in ddl_statements:
                        conn.execute(text(ddl.strip()))
                    conn.commit()
            else:
                # For custom metadata, ensure we're using DuckDB dialect
                # Create tables using DuckDB connection
                with self.engine.connect() as conn:
                    # Use the connection to create all tables from metadata
                    self.metadata.create_all(conn)
        
        try:
            await asyncio.to_thread(_create_tables)
            logger.info("All tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            raise DatabaseOperationError(f"Failed to create tables: {e}")
    
    async def drop_all_tables(self) -> None:
        """Drop all tables defined in the Base metadata."""
        logger.warning("Dropping all database tables...")
        
        def _drop_tables():
            # Drop tables in reverse order to handle dependencies
            table_names = ["repositories", "documents", "conversations", "projects"]
            
            with self.engine.connect() as conn:
                for table_name in table_names:
                    try:
                        conn.execute(text(f"DROP TABLE IF EXISTS {table_name}"))
                    except SQLAlchemyError:
                        # Ignore errors for tables that don't exist
                        pass
                conn.commit()
        
        try:
            await asyncio.to_thread(_drop_tables)
            logger.info("All tables dropped successfully")
        except Exception as e:
            logger.error(f"Failed to drop tables: {e}")
            raise DatabaseOperationError(f"Failed to drop tables: {e}")
    
    async def table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the database."""
        # Handle invalid table names
        if not table_name or table_name is None:
            return False
            
        logger.debug(f"Checking if table '{table_name}' exists")
        
        def _table_exists():
            inspector = inspect(self.engine)
            return inspector.has_table(table_name)
        
        try:
            exists = await asyncio.to_thread(_table_exists)
            logger.debug(f"Table '{table_name}' {'exists' if exists else 'does not exist'}")
            return exists
        except (SQLAlchemyError, TypeError) as e:
            logger.error(f"Failed to check table existence: {e}")
            return False
    
    async def get_table_names(self) -> List[str]:
        """Get list of all table names in the database."""
        logger.debug("Retrieving table names from database")
        
        def _get_table_names():
            inspector = inspect(self.engine)
            return inspector.get_table_names()
        
        try:
            tables = await asyncio.to_thread(_get_table_names)
            logger.debug(f"Found {len(tables)} tables: {tables}")
            return tables
        except SQLAlchemyError as e:
            logger.error(f"Failed to get table names: {e}")
            raise DatabaseOperationError(f"Failed to get table names: {e}")
    
    async def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """Get schema information for a specific table."""
        logger.debug(f"Retrieving schema for table '{table_name}'")
        
        def _get_table_schema():
            inspector = inspect(self.engine)
            if not inspector.has_table(table_name):
                return None
            
            columns = inspector.get_columns(table_name)
            primary_keys = inspector.get_pk_constraint(table_name)
            foreign_keys = inspector.get_foreign_keys(table_name)
            indexes = inspector.get_indexes(table_name)
            
            return {
                'columns': columns,
                'primary_keys': primary_keys,
                'foreign_keys': foreign_keys,
                'indexes': indexes
            }
        
        try:
            schema = await asyncio.to_thread(_get_table_schema)
            if schema is None:
                raise DatabaseOperationError(f"Table '{table_name}' does not exist")
            
            logger.debug(f"Retrieved schema for table '{table_name}'")
            return schema
        except DatabaseOperationError:
            # Re-raise DatabaseOperationError as-is
            raise
        except Exception as e:
            logger.error(f"Failed to get table schema: {e}")
            raise DatabaseOperationError(f"Failed to get table schema: {e}")
    
    async def recreate_all_tables(self) -> None:
        """Drop and recreate all tables."""
        logger.info("Recreating all database tables...")
        try:
            await self.drop_all_tables()
            await self.create_all_tables()
            logger.info("All tables recreated successfully")
        except Exception as e:
            logger.error(f"Failed to recreate tables: {e}")
            raise DatabaseOperationError(f"Failed to recreate tables: {e}")

    async def verify_schema(self, expected_tables: Optional[List[str]] = None) -> bool:
        """Verify that all expected tables exist with correct schema."""
        logger.info("Verifying database schema...")
        
        try:
            if expected_tables is None:
                expected_tables = list(self.metadata.tables.keys())
            existing_tables = await self.get_table_names()
            
            missing_tables = set(expected_tables) - set(existing_tables)
            if missing_tables:
                logger.warning(f"Missing tables: {missing_tables}")
                return False
            
            logger.info("Database schema verification passed")
            return True
            
        except Exception as e:
            logger.error(f"Schema verification failed: {e}")
            raise DatabaseOperationError(f"Schema verification failed: {e}")
    
    async def execute_sql_file(self, file_path: str) -> None:
        """Execute SQL commands from a file."""
        logger.info(f"Executing SQL file: {file_path}")
        
        try:
            with open(file_path, 'r') as f:
                sql_content = f.read()
            
            # Split by semicolons and execute each statement
            statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
            
            session_manager = get_session_manager()
            async with session_manager.transaction() as session:
                for statement in statements:
                    await session.execute(text(statement))
            
            logger.info(f"Successfully executed SQL file: {file_path}")
            
        except Exception as e:
            logger.error(f"Failed to execute SQL file: {e}")
            raise DatabaseOperationError(f"Failed to execute SQL file: {e}")
    
    async def seed_data(self, data: Dict[str, List[Dict[str, Any]]]) -> None:
        """Seed the database with initial data."""
        logger.info("Seeding database with initial data...")
        
        try:
            session_manager = get_session_manager()
            async with session_manager.transaction() as session:
                for table_name, records in data.items():
                    if records:
                        # Get the table class from metadata
                        table = self.metadata.tables.get(table_name)
                        if table is None:
                            logger.warning(f"Table '{table_name}' not found in metadata")
                            continue
                        
                        # Bulk insert records
                        await session.execute(table.insert(), records)
                        logger.debug(f"Seeded {len(records)} records into '{table_name}'")
            
            logger.info("Database seeding completed successfully")
            
        except Exception as e:
            logger.error(f"Failed to seed database: {e}")
            raise DatabaseOperationError(f"Failed to seed database: {e}")
    
    async def get_database_size(self) -> int:
        """Get the size of the database in bytes. Not implemented for DuckDB."""
        logger.warning("get_database_size is not implemented for DuckDB")
        raise NotImplementedError("Database size calculation not supported for DuckDB")
    
    async def backup_database(self, backup_path: str) -> None:
        """Backup the database. Not implemented for DuckDB."""
        logger.warning("backup_database is not implemented for DuckDB")
        raise NotImplementedError("Database backup not supported for DuckDB")
    
    async def restore_database(self, backup_path: str) -> None:
        """Restore the database from backup. Not implemented for DuckDB."""
        logger.warning("restore_database is not implemented for DuckDB")
        raise NotImplementedError("Database restore not supported for DuckDB")
    
    async def get_connection_info(self) -> Dict[str, Any]:
        """Get database connection information."""
        logger.debug("Retrieving database connection info")
        
        try:
            return {
                'engine': str(self.engine),
                'dialect': self.engine.dialect.name if hasattr(self.engine, 'dialect') else 'unknown',
                'driver': getattr(self.engine.dialect, 'driver', 'unknown'),
                'url': str(self.engine.url) if hasattr(self.engine, 'url') else 'unknown'
            }
        except Exception as e:
            logger.error(f"Failed to get connection info: {e}")
            raise DatabaseOperationError(f"Failed to get connection info: {e}")
    
    async def validate_database(self) -> bool:
        """Validate database connection and basic functionality."""
        logger.debug("Validating database connection")
        
        try:
            # Test basic connection
            def _test_connection():
                with self.engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                    return True
            
            await asyncio.to_thread(_test_connection)
            logger.debug("Database validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Database validation failed: {e}")
            return False


# Global database initializer instance
_db_initializer: Optional[DatabaseInitializer] = None


def get_database_initializer() -> DatabaseInitializer:
    """Get the global database initializer instance."""
    global _db_initializer
    if _db_initializer is None:
        _db_initializer = DatabaseInitializer()
    return _db_initializer


def set_database_initializer(initializer: Optional[DatabaseInitializer]) -> None:
    """Set the global database initializer instance."""
    global _db_initializer
    _db_initializer = initializer


async def initialize_database(
    engine: Optional[Engine] = None,
    create_tables: bool = True,
    drop_existing: bool = False
) -> None:
    """
    Convenience function to initialize the database.
    
    Args:
        engine: Optional engine to use
        create_tables: Whether to create tables automatically
        drop_existing: Whether to drop existing tables first
    """
    if engine:
        initializer = DatabaseInitializer(engine)
    else:
        initializer = get_database_initializer()
    
    await initializer.initialize_database(create_tables, drop_existing)


async def create_tables(engine: Optional[Engine] = None) -> None:
    """Convenience function to create all tables."""
    if engine:
        initializer = DatabaseInitializer(engine)
    else:
        initializer = get_database_initializer()
    
    await initializer.create_all_tables()


async def drop_tables(engine: Optional[Engine] = None) -> None:
    """Convenience function to drop all tables."""
    if engine:
        initializer = DatabaseInitializer(engine)
    else:
        initializer = get_database_initializer()
    
    await initializer.drop_all_tables()


async def verify_database_schema(engine: Optional[Engine] = None) -> bool:
    """Convenience function to verify database schema."""
    if engine:
        initializer = DatabaseInitializer(engine)
    else:
        initializer = get_database_initializer()
    
    return await initializer.verify_schema()