"""
Unit tests for core.database module
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from pathlib import Path
from sqlalchemy import Engine, MetaData, Table, inspect
from sqlalchemy.exc import SQLAlchemyError

from src.andamios_orm.core.database import (
    DatabaseInitializer,
    get_database_initializer,
    set_database_initializer,
    initialize_database,
    create_tables,
    drop_tables,
    verify_database_schema,
    _db_initializer
)
from src.andamios_orm.exceptions import DatabaseOperationError


class TestDatabaseInitializer:
    """Test DatabaseInitializer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_engine = Mock(spec=Engine)
        self.mock_metadata = Mock(spec=MetaData)
        
        with patch('src.andamios_orm.core.database.Base') as mock_base:
            mock_base.metadata = self.mock_metadata
            self.db_init = DatabaseInitializer(self.mock_engine)
    
    def test_init_with_engine(self):
        """Test DatabaseInitializer initialization with engine."""
        assert self.db_init.engine == self.mock_engine
        assert self.db_init.metadata == self.mock_metadata
    
    @patch('src.andamios_orm.core.database.get_engine')
    def test_init_without_engine(self, mock_get_engine):
        """Test DatabaseInitializer initialization without engine."""
        mock_default_engine = Mock(spec=Engine)
        mock_get_engine.return_value = mock_default_engine
        
        with patch('src.andamios_orm.core.database.Base') as mock_base:
            mock_base.metadata = self.mock_metadata
            db_init = DatabaseInitializer()
        
        mock_get_engine.assert_called_once()
        assert db_init.engine == mock_default_engine
    
    @pytest.mark.asyncio
    @patch('src.andamios_orm.core.database.ensure_uvloop')
    async def test_initialize_database_success(self, mock_ensure_uvloop):
        """Test successful database initialization."""
        with patch.object(self.db_init, 'create_all_tables', new_callable=AsyncMock) as mock_create:
            with patch.object(self.db_init, 'verify_schema', new_callable=AsyncMock) as mock_verify:
                mock_verify.return_value = True
                
                await self.db_init.initialize_database()
                
                mock_ensure_uvloop.assert_called_once()
                mock_create.assert_called_once()
                mock_verify.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_initialize_database_with_drop_existing(self):
        """Test database initialization with drop_existing=True."""
        with patch.object(self.db_init, 'drop_all_tables', new_callable=AsyncMock) as mock_drop:
            with patch.object(self.db_init, 'create_all_tables', new_callable=AsyncMock) as mock_create:
                with patch.object(self.db_init, 'verify_schema', new_callable=AsyncMock) as mock_verify:
                    mock_verify.return_value = True
                    
                    await self.db_init.initialize_database(drop_existing=True)
                    
                    mock_drop.assert_called_once()
                    mock_create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_initialize_database_skip_create_tables(self):
        """Test database initialization with create_tables=False."""
        with patch.object(self.db_init, 'create_all_tables', new_callable=AsyncMock) as mock_create:
            with patch.object(self.db_init, 'verify_schema', new_callable=AsyncMock) as mock_verify:
                mock_verify.return_value = True
                
                await self.db_init.initialize_database(create_tables=False)
                
                mock_create.assert_not_called()
                mock_verify.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_initialize_database_exception(self):
        """Test database initialization with exception."""
        with patch.object(self.db_init, 'create_all_tables', new_callable=AsyncMock) as mock_create:
            mock_create.side_effect = Exception("Test error")
            
            with pytest.raises(DatabaseOperationError, match="Failed to initialize database"):
                await self.db_init.initialize_database()
    
    @pytest.mark.asyncio
    @patch('asyncio.to_thread')
    async def test_create_all_tables_success(self, mock_to_thread):
        """Test successful table creation."""
        mock_to_thread.return_value = None
        
        await self.db_init.create_all_tables()
        
        mock_to_thread.assert_called_once()
        # Verify the function passed to to_thread
        create_func = mock_to_thread.call_args[0][0]
        create_func()
        self.mock_metadata.create_all.assert_called_once_with(self.mock_engine)
    
    @pytest.mark.asyncio
    @patch('asyncio.to_thread')
    async def test_create_all_tables_exception(self, mock_to_thread):
        """Test table creation with SQLAlchemy exception."""
        mock_to_thread.side_effect = SQLAlchemyError("Test error")
        
        with pytest.raises(DatabaseOperationError, match="Failed to create tables"):
            await self.db_init.create_all_tables()
    
    @pytest.mark.asyncio
    @patch('asyncio.to_thread')
    async def test_drop_all_tables_success(self, mock_to_thread):
        """Test successful table dropping."""
        mock_to_thread.return_value = None
        
        await self.db_init.drop_all_tables()
        
        mock_to_thread.assert_called_once()
        # Verify the function passed to to_thread
        drop_func = mock_to_thread.call_args[0][0]
        drop_func()
        self.mock_metadata.drop_all.assert_called_once_with(self.mock_engine)
    
    @pytest.mark.asyncio
    @patch('asyncio.to_thread')
    async def test_drop_all_tables_exception(self, mock_to_thread):
        """Test table dropping with SQLAlchemy exception."""
        mock_to_thread.side_effect = SQLAlchemyError("Test error")
        
        with pytest.raises(DatabaseOperationError, match="Failed to drop tables"):
            await self.db_init.drop_all_tables()
    
    @pytest.mark.asyncio
    @patch('asyncio.to_thread')
    async def test_table_exists_true(self, mock_to_thread):
        """Test table_exists returns True when table exists."""
        mock_inspector = Mock()
        mock_inspector.has_table.return_value = True
        mock_to_thread.return_value = True
        
        with patch('src.andamios_orm.core.database.inspect', return_value=mock_inspector):
            result = await self.db_init.table_exists("test_table")
            
            assert result is True
            mock_inspector.has_table.assert_called_once_with("test_table")
    
    @pytest.mark.asyncio
    @patch('asyncio.to_thread')
    async def test_table_exists_false(self, mock_to_thread):
        """Test table_exists returns False when table doesn't exist."""
        mock_inspector = Mock()
        mock_inspector.has_table.return_value = False
        mock_to_thread.return_value = False
        
        with patch('src.andamios_orm.core.database.inspect', return_value=mock_inspector):
            result = await self.db_init.table_exists("test_table")
            
            assert result is False
    
    @pytest.mark.asyncio
    @patch('asyncio.to_thread')
    async def test_table_exists_exception(self, mock_to_thread):
        """Test table_exists with SQLAlchemy exception."""
        mock_to_thread.side_effect = SQLAlchemyError("Test error")
        
        with pytest.raises(DatabaseOperationError, match="Failed to check table existence"):
            await self.db_init.table_exists("test_table")
    
    @pytest.mark.asyncio
    @patch('asyncio.to_thread')
    async def test_get_table_names_success(self, mock_to_thread):
        """Test successful get_table_names."""
        expected_tables = ["table1", "table2", "table3"]
        mock_inspector = Mock()
        mock_inspector.get_table_names.return_value = expected_tables
        mock_to_thread.return_value = expected_tables
        
        with patch('src.andamios_orm.core.database.inspect', return_value=mock_inspector):
            result = await self.db_init.get_table_names()
            
            assert result == expected_tables
            mock_inspector.get_table_names.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('asyncio.to_thread')
    async def test_get_table_names_exception(self, mock_to_thread):
        """Test get_table_names with SQLAlchemy exception."""
        mock_to_thread.side_effect = SQLAlchemyError("Test error")
        
        with pytest.raises(DatabaseOperationError, match="Failed to get table names"):
            await self.db_init.get_table_names()
    
    @pytest.mark.asyncio
    @patch('asyncio.to_thread')
    async def test_get_table_schema_success(self, mock_to_thread):
        """Test successful get_table_schema."""
        expected_schema = {
            'columns': [{'name': 'id', 'type': 'INTEGER'}],
            'primary_keys': {'constrained_columns': ['id']},
            'foreign_keys': [],
            'indexes': []
        }
        
        def mock_get_schema():
            mock_inspector = Mock()
            mock_inspector.has_table.return_value = True
            mock_inspector.get_columns.return_value = expected_schema['columns']
            mock_inspector.get_pk_constraint.return_value = expected_schema['primary_keys']
            mock_inspector.get_foreign_keys.return_value = expected_schema['foreign_keys']
            mock_inspector.get_indexes.return_value = expected_schema['indexes']
            return expected_schema
        
        mock_to_thread.return_value = expected_schema
        
        with patch('src.andamios_orm.core.database.inspect'):
            result = await self.db_init.get_table_schema("test_table")
            
            assert result == expected_schema
    
    @pytest.mark.asyncio
    @patch('asyncio.to_thread')
    async def test_get_table_schema_table_not_exists(self, mock_to_thread):
        """Test get_table_schema when table doesn't exist."""
        mock_to_thread.return_value = None
        
        with pytest.raises(DatabaseOperationError, match="Table 'test_table' does not exist"):
            await self.db_init.get_table_schema("test_table")
    
    @pytest.mark.asyncio
    @patch('asyncio.to_thread')
    async def test_get_table_schema_exception(self, mock_to_thread):
        """Test get_table_schema with SQLAlchemy exception."""
        mock_to_thread.side_effect = SQLAlchemyError("Test error")
        
        with pytest.raises(DatabaseOperationError, match="Failed to get table schema"):
            await self.db_init.get_table_schema("test_table")
    
    @pytest.mark.asyncio
    async def test_verify_schema_success(self):
        """Test successful schema verification."""
        self.mock_metadata.tables.keys.return_value = ["table1", "table2"]
        
        with patch.object(self.db_init, 'get_table_names', new_callable=AsyncMock) as mock_get_tables:
            mock_get_tables.return_value = ["table1", "table2", "extra_table"]
            
            result = await self.db_init.verify_schema()
            
            assert result is True
    
    @pytest.mark.asyncio
    async def test_verify_schema_missing_tables(self):
        """Test schema verification with missing tables."""
        self.mock_metadata.tables.keys.return_value = ["table1", "table2", "table3"]
        
        with patch.object(self.db_init, 'get_table_names', new_callable=AsyncMock) as mock_get_tables:
            mock_get_tables.return_value = ["table1", "table2"]  # missing table3
            
            result = await self.db_init.verify_schema()
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_verify_schema_exception(self):
        """Test schema verification with exception."""
        with patch.object(self.db_init, 'get_table_names', new_callable=AsyncMock) as mock_get_tables:
            mock_get_tables.side_effect = Exception("Test error")
            
            with pytest.raises(DatabaseOperationError, match="Schema verification failed"):
                await self.db_init.verify_schema()
    
    @pytest.mark.asyncio
    async def test_execute_sql_file_success(self, temp_dir):
        """Test successful SQL file execution."""
        sql_file = temp_dir / "test.sql"
        sql_content = "CREATE TABLE test (id INTEGER); INSERT INTO test VALUES (1); SELECT * FROM test;"
        sql_file.write_text(sql_content)
        
        mock_session = AsyncMock()
        mock_session_manager = Mock()
        mock_session_manager.transaction.return_value.__aenter__.return_value = mock_session
        mock_session_manager.transaction.return_value.__aexit__ = AsyncMock()
        
        with patch('src.andamios_orm.core.database.get_session_manager', return_value=mock_session_manager):
            await self.db_init.execute_sql_file(str(sql_file))
            
            # Should execute 3 statements
            assert mock_session.execute.call_count == 3
    
    @pytest.mark.asyncio
    async def test_execute_sql_file_not_found(self):
        """Test SQL file execution with file not found."""
        with pytest.raises(DatabaseOperationError, match="Failed to execute SQL file"):
            await self.db_init.execute_sql_file("/nonexistent/file.sql")
    
    @pytest.mark.asyncio
    async def test_seed_data_success(self):
        """Test successful data seeding."""
        seed_data = {
            "test_table": [
                {"id": 1, "name": "test1"},
                {"id": 2, "name": "test2"}
            ]
        }
        
        mock_table = Mock()
        mock_table.insert.return_value = "INSERT_STATEMENT"
        self.mock_metadata.tables = {"test_table": mock_table}
        
        mock_session = AsyncMock()
        mock_session_manager = Mock()
        mock_session_manager.transaction.return_value.__aenter__.return_value = mock_session
        mock_session_manager.transaction.return_value.__aexit__ = AsyncMock()
        
        with patch('src.andamios_orm.core.database.get_session_manager', return_value=mock_session_manager):
            await self.db_init.seed_data(seed_data)
            
            mock_session.execute.assert_called_once_with(
                "INSERT_STATEMENT",
                seed_data["test_table"]
            )
    
    @pytest.mark.asyncio
    async def test_seed_data_table_not_found(self):
        """Test data seeding with table not found."""
        seed_data = {"nonexistent_table": [{"id": 1}]}
        self.mock_metadata.tables = {}
        
        mock_session = AsyncMock()
        mock_session_manager = Mock()
        mock_session_manager.transaction.return_value.__aenter__.return_value = mock_session
        mock_session_manager.transaction.return_value.__aexit__ = AsyncMock()
        
        with patch('src.andamios_orm.core.database.get_session_manager', return_value=mock_session_manager):
            # Should not raise exception, just log warning
            await self.db_init.seed_data(seed_data)
            
            mock_session.execute.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_seed_data_exception(self):
        """Test data seeding with exception."""
        seed_data = {"test_table": [{"id": 1}]}
        
        mock_session_manager = Mock()
        mock_session_manager.transaction.side_effect = Exception("Test error")
        
        with patch('src.andamios_orm.core.database.get_session_manager', return_value=mock_session_manager):
            with pytest.raises(DatabaseOperationError, match="Failed to seed database"):
                await self.db_init.seed_data(seed_data)


class TestGlobalDatabaseInitializer:
    """Test global database initializer functions."""
    
    def test_get_database_initializer_creates_default(self):
        """Test that get_database_initializer creates default initializer."""
        import src.andamios_orm.core.database as database_module
        database_module._db_initializer = None
        
        with patch('src.andamios_orm.core.database.DatabaseInitializer') as mock_di_class:
            mock_initializer = Mock()
            mock_di_class.return_value = mock_initializer
            
            result = get_database_initializer()
            
            mock_di_class.assert_called_once()
            assert result == mock_initializer
            assert database_module._db_initializer == mock_initializer
    
    def test_get_database_initializer_returns_existing(self):
        """Test that get_database_initializer returns existing initializer."""
        import src.andamios_orm.core.database as database_module
        mock_initializer = Mock()
        database_module._db_initializer = mock_initializer
        
        result = get_database_initializer()
        
        assert result == mock_initializer
    
    def test_set_database_initializer(self):
        """Test set_database_initializer function."""
        import src.andamios_orm.core.database as database_module
        mock_initializer = Mock()
        
        set_database_initializer(mock_initializer)
        
        assert database_module._db_initializer == mock_initializer


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    @pytest.mark.asyncio
    async def test_initialize_database_with_engine(self):
        """Test initialize_database with provided engine."""
        mock_engine = Mock(spec=Engine)
        
        with patch('src.andamios_orm.core.database.DatabaseInitializer') as mock_di_class:
            mock_initializer = Mock()
            mock_initializer.initialize_database = AsyncMock()
            mock_di_class.return_value = mock_initializer
            
            await initialize_database(mock_engine, create_tables=False, drop_existing=True)
            
            mock_di_class.assert_called_once_with(mock_engine)
            mock_initializer.initialize_database.assert_called_once_with(False, True)
    
    @pytest.mark.asyncio
    async def test_initialize_database_without_engine(self):
        """Test initialize_database without provided engine."""
        mock_initializer = Mock()
        mock_initializer.initialize_database = AsyncMock()
        
        with patch('src.andamios_orm.core.database.get_database_initializer', return_value=mock_initializer):
            await initialize_database()
            
            mock_initializer.initialize_database.assert_called_once_with(True, False)
    
    @pytest.mark.asyncio
    async def test_create_tables_with_engine(self):
        """Test create_tables with provided engine."""
        mock_engine = Mock(spec=Engine)
        
        with patch('src.andamios_orm.core.database.DatabaseInitializer') as mock_di_class:
            mock_initializer = Mock()
            mock_initializer.create_all_tables = AsyncMock()
            mock_di_class.return_value = mock_initializer
            
            await create_tables(mock_engine)
            
            mock_di_class.assert_called_once_with(mock_engine)
            mock_initializer.create_all_tables.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_tables_without_engine(self):
        """Test create_tables without provided engine."""
        mock_initializer = Mock()
        mock_initializer.create_all_tables = AsyncMock()
        
        with patch('src.andamios_orm.core.database.get_database_initializer', return_value=mock_initializer):
            await create_tables()
            
            mock_initializer.create_all_tables.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_drop_tables_with_engine(self):
        """Test drop_tables with provided engine."""
        mock_engine = Mock(spec=Engine)
        
        with patch('src.andamios_orm.core.database.DatabaseInitializer') as mock_di_class:
            mock_initializer = Mock()
            mock_initializer.drop_all_tables = AsyncMock()
            mock_di_class.return_value = mock_initializer
            
            await drop_tables(mock_engine)
            
            mock_di_class.assert_called_once_with(mock_engine)
            mock_initializer.drop_all_tables.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_drop_tables_without_engine(self):
        """Test drop_tables without provided engine."""
        mock_initializer = Mock()
        mock_initializer.drop_all_tables = AsyncMock()
        
        with patch('src.andamios_orm.core.database.get_database_initializer', return_value=mock_initializer):
            await drop_tables()
            
            mock_initializer.drop_all_tables.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_verify_database_schema_with_engine(self):
        """Test verify_database_schema with provided engine."""
        mock_engine = Mock(spec=Engine)
        
        with patch('src.andamios_orm.core.database.DatabaseInitializer') as mock_di_class:
            mock_initializer = Mock()
            mock_initializer.verify_schema = AsyncMock(return_value=True)
            mock_di_class.return_value = mock_initializer
            
            result = await verify_database_schema(mock_engine)
            
            mock_di_class.assert_called_once_with(mock_engine)
            mock_initializer.verify_schema.assert_called_once()
            assert result is True
    
    @pytest.mark.asyncio
    async def test_verify_database_schema_without_engine(self):
        """Test verify_database_schema without provided engine."""
        mock_initializer = Mock()
        mock_initializer.verify_schema = AsyncMock(return_value=False)
        
        with patch('src.andamios_orm.core.database.get_database_initializer', return_value=mock_initializer):
            result = await verify_database_schema()
            
            mock_initializer.verify_schema.assert_called_once()
            assert result is False


class TestIntegration:
    """Integration tests for database functionality."""
    
    @pytest.mark.asyncio
    async def test_database_lifecycle(self, memory_engine):
        """Test complete database lifecycle."""
        db_init = DatabaseInitializer(memory_engine)
        
        # Initialize database
        await db_init.initialize_database()
        
        # Verify tables exist
        table_names = await db_init.get_table_names()
        assert len(table_names) >= 4  # projects, conversations, documents, repositories
        
        # Verify schema
        schema_valid = await db_init.verify_schema()
        assert schema_valid is True
        
        # Test table existence
        for table_name in ["projects", "conversations", "documents", "repositories"]:
            exists = await db_init.table_exists(table_name)
            assert exists is True
        
        # Drop tables
        await db_init.drop_all_tables()
        
        # Verify tables are gone
        table_names_after = await db_init.get_table_names()
        assert len(table_names_after) == 0