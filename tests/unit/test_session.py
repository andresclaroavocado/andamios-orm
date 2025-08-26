"""
Unit tests for core.session module
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from sqlalchemy import Engine, text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from src.andamios_orm.core.session import (
    init_db,
    AsyncSessionWrapper,
    get_session,
    session_scope,
    transaction_scope,
    with_session,
    with_transaction,
    SessionManager,
    get_session_manager,
    set_session_manager,
    sessionmaker,
    _global_engine,
    _global_sessionmaker
)
from src.andamios_orm.exceptions import DatabaseConnectionError


class TestInitDb:
    """Test init_db function."""
    
    @patch('src.andamios_orm.core.session.sync_sessionmaker')
    @patch('src.andamios_orm.core.session.create_memory_engine')
    def test_init_db_no_engine(self, mock_create_engine, mock_sessionmaker):
        """Test init_db without providing engine."""
        mock_engine = Mock(spec=Engine)
        mock_session_maker = Mock()
        mock_create_engine.return_value = mock_engine
        mock_sessionmaker.return_value = mock_session_maker
        
        init_db()
        
        mock_create_engine.assert_called_once()
        mock_sessionmaker.assert_called_once_with(
            mock_engine,
            expire_on_commit=False
        )
        
        # Check global state
        import src.andamios_orm.core.session as session_module
        assert session_module._global_engine == mock_engine
        assert session_module._global_sessionmaker == mock_session_maker
    
    @patch('src.andamios_orm.core.session.sync_sessionmaker')
    def test_init_db_with_engine(self, mock_sessionmaker):
        """Test init_db with provided engine."""
        mock_engine = Mock(spec=Engine)
        mock_session_maker = Mock()
        mock_sessionmaker.return_value = mock_session_maker
        
        init_db(mock_engine)
        
        mock_sessionmaker.assert_called_once_with(
            mock_engine,
            expire_on_commit=False
        )
        
        # Check global state
        import src.andamios_orm.core.session as session_module
        assert session_module._global_engine == mock_engine
        assert session_module._global_sessionmaker == mock_session_maker


class TestAsyncSessionWrapper:
    """Test AsyncSessionWrapper class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_session = Mock(spec=Session)
        self.wrapper = AsyncSessionWrapper(self.mock_session)
    
    @pytest.mark.asyncio
    @patch('asyncio.to_thread')
    async def test_add(self, mock_to_thread):
        """Test add method."""
        mock_instance = Mock()
        mock_to_thread.return_value = None
        
        await self.wrapper.add(mock_instance)
        
        mock_to_thread.assert_called_once_with(
            self.mock_session.add, mock_instance
        )
    
    @pytest.mark.asyncio
    @patch('asyncio.to_thread')
    async def test_add_with_exception(self, mock_to_thread):
        """Test add method with SQLAlchemy exception."""
        mock_instance = Mock()
        mock_to_thread.side_effect = SQLAlchemyError("Test error")
        
        with pytest.raises(DatabaseConnectionError, match="Failed to add instance"):
            await self.wrapper.add(mock_instance)
    
    @pytest.mark.asyncio
    @patch('asyncio.to_thread')
    async def test_commit(self, mock_to_thread):
        """Test commit method."""
        mock_to_thread.return_value = None
        
        await self.wrapper.commit()
        
        mock_to_thread.assert_called_once_with(self.mock_session.commit)
    
    @pytest.mark.asyncio
    @patch('asyncio.to_thread')
    async def test_commit_with_exception(self, mock_to_thread):
        """Test commit method with exception."""
        mock_to_thread.side_effect = SQLAlchemyError("Test error")
        
        with pytest.raises(DatabaseConnectionError, match="Failed to commit"):
            await self.wrapper.commit()
    
    @pytest.mark.asyncio
    @patch('asyncio.to_thread')
    async def test_rollback(self, mock_to_thread):
        """Test rollback method."""
        mock_to_thread.return_value = None
        
        await self.wrapper.rollback()
        
        mock_to_thread.assert_called_once_with(self.mock_session.rollback)
    
    @pytest.mark.asyncio
    @patch('asyncio.to_thread')
    async def test_rollback_with_exception(self, mock_to_thread):
        """Test rollback method with exception."""
        mock_to_thread.side_effect = SQLAlchemyError("Test error")
        
        with pytest.raises(DatabaseConnectionError, match="Failed to rollback"):
            await self.wrapper.rollback()
    
    @pytest.mark.asyncio
    @patch('asyncio.to_thread')
    async def test_refresh(self, mock_to_thread):
        """Test refresh method."""
        mock_instance = Mock()
        mock_to_thread.return_value = None
        
        await self.wrapper.refresh(mock_instance)
        
        mock_to_thread.assert_called_once_with(
            self.mock_session.refresh, mock_instance
        )
    
    @pytest.mark.asyncio
    @patch('asyncio.to_thread')
    async def test_get(self, mock_to_thread):
        """Test get method."""
        mock_model_class = Mock()
        mock_id = 1
        mock_result = Mock()
        mock_to_thread.return_value = mock_result
        
        result = await self.wrapper.get(mock_model_class, mock_id)
        
        mock_to_thread.assert_called_once_with(
            self.mock_session.get, mock_model_class, mock_id
        )
        assert result == mock_result
    
    @pytest.mark.asyncio
    @patch('asyncio.to_thread')
    async def test_delete(self, mock_to_thread):
        """Test delete method."""
        mock_instance = Mock()
        mock_to_thread.return_value = None
        
        await self.wrapper.delete(mock_instance)
        
        mock_to_thread.assert_called_once_with(
            self.mock_session.delete, mock_instance
        )
    
    @pytest.mark.asyncio
    @patch('asyncio.to_thread')
    async def test_execute(self, mock_to_thread):
        """Test execute method."""
        mock_statement = Mock()
        mock_parameters = {"param": "value"}
        mock_result = Mock()
        mock_to_thread.return_value = mock_result
        
        result = await self.wrapper.execute(mock_statement, mock_parameters)
        
        mock_to_thread.assert_called_once_with(
            self.mock_session.execute, mock_statement, mock_parameters
        )
        assert result == mock_result
    
    @pytest.mark.asyncio
    @patch('asyncio.to_thread')
    async def test_execute_without_parameters(self, mock_to_thread):
        """Test execute method without parameters."""
        mock_statement = Mock()
        mock_result = Mock()
        mock_to_thread.return_value = mock_result
        
        result = await self.wrapper.execute(mock_statement)
        
        mock_to_thread.assert_called_once_with(
            self.mock_session.execute, mock_statement
        )
        assert result == mock_result
    
    @pytest.mark.asyncio
    @patch('asyncio.to_thread')
    async def test_bulk_insert_mappings(self, mock_to_thread):
        """Test bulk_insert_mappings method."""
        mock_model_class = Mock()
        mock_mappings = [{"field": "value"}]
        mock_to_thread.return_value = None
        
        await self.wrapper.bulk_insert_mappings(mock_model_class, mock_mappings)
        
        mock_to_thread.assert_called_once_with(
            self.mock_session.bulk_insert_mappings, mock_model_class, mock_mappings
        )
    
    @pytest.mark.asyncio
    @patch('asyncio.to_thread')
    async def test_bulk_update_mappings(self, mock_to_thread):
        """Test bulk_update_mappings method."""
        mock_model_class = Mock()
        mock_mappings = [{"id": 1, "field": "value"}]
        mock_to_thread.return_value = None
        
        await self.wrapper.bulk_update_mappings(mock_model_class, mock_mappings)
        
        mock_to_thread.assert_called_once_with(
            self.mock_session.bulk_update_mappings, mock_model_class, mock_mappings
        )
    
    @pytest.mark.asyncio
    @patch('asyncio.to_thread')
    async def test_close(self, mock_to_thread):
        """Test close method."""
        mock_to_thread.return_value = None
        
        await self.wrapper.close()
        
        mock_to_thread.assert_called_once_with(self.mock_session.close)
    
    def test_context_manager_sync(self):
        """Test synchronous context manager."""
        with self.wrapper as session:
            assert session == self.wrapper
    
    @pytest.mark.asyncio
    async def test_async_context_manager_success(self):
        """Test async context manager successful case."""
        with patch.object(self.wrapper, 'close', new_callable=AsyncMock) as mock_close:
            async with self.wrapper as session:
                assert session == self.wrapper
            
            mock_close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_async_context_manager_exception(self):
        """Test async context manager with exception."""
        with patch.object(self.wrapper, 'close', new_callable=AsyncMock) as mock_close:
            with patch.object(self.wrapper, 'rollback', new_callable=AsyncMock) as mock_rollback:
                with pytest.raises(ValueError):
                    async with self.wrapper as session:
                        raise ValueError("Test exception")
                
                mock_rollback.assert_called_once()
                mock_close.assert_called_once()


class TestGetSession:
    """Test get_session function."""
    
    @pytest.mark.asyncio
    @patch('src.andamios_orm.core.session._create_tables_duckdb_compatible')
    @patch('src.andamios_orm.core.session.init_db')
    async def test_get_session_auto_init(self, mock_init_db, mock_create_tables):
        """Test get_session with automatic initialization."""
        import src.andamios_orm.core.session as session_module
        
        # Clear global state
        session_module._global_sessionmaker = None
        session_module._global_engine = None
        
        mock_session = Mock(spec=Session)
        mock_sessionmaker = Mock(return_value=mock_session)
        mock_engine = Mock(spec=Engine)
        
        def init_side_effect():
            session_module._global_sessionmaker = mock_sessionmaker
            session_module._global_engine = mock_engine
        
        mock_init_db.side_effect = init_side_effect
        mock_create_tables.return_value = None
        
        result = await get_session()
        
        mock_init_db.assert_called_once()
        mock_create_tables.assert_called_once_with(mock_engine)
        assert isinstance(result, AsyncSessionWrapper)
        assert result._session == mock_session
    
    @pytest.mark.asyncio
    @patch('src.andamios_orm.core.session._create_tables_duckdb_compatible')
    async def test_get_session_existing_sessionmaker(self, mock_create_tables):
        """Test get_session with existing sessionmaker."""
        import src.andamios_orm.core.session as session_module
        
        mock_session = Mock(spec=Session)
        mock_sessionmaker = Mock(return_value=mock_session)
        mock_engine = Mock(spec=Engine)
        
        session_module._global_sessionmaker = mock_sessionmaker
        session_module._global_engine = mock_engine
        
        result = await get_session()
        
        mock_create_tables.assert_called_once_with(mock_engine)
        assert isinstance(result, AsyncSessionWrapper)
        assert result._session == mock_session


class TestSessionScope:
    """Test session_scope context manager."""
    
    @pytest.mark.asyncio
    @patch('src.andamios_orm.core.session.get_session_manager')
    async def test_session_scope_success(self, mock_get_session_manager):
        """Test successful session_scope usage."""
        mock_session = AsyncMock(spec=AsyncSessionWrapper)
        mock_manager = AsyncMock()
        mock_manager.get_session.return_value = mock_session
        mock_get_session_manager.return_value = mock_manager
        
        async with session_scope() as session:
            assert session == mock_session
        
        mock_manager.get_session.assert_called_once()
        mock_session.close.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('src.andamios_orm.core.session.get_session_manager')
    async def test_session_scope_exception(self, mock_get_session_manager):
        """Test session_scope with exception."""
        mock_session = AsyncMock(spec=AsyncSessionWrapper)
        mock_manager = AsyncMock()
        mock_manager.get_session.return_value = mock_session
        mock_get_session_manager.return_value = mock_manager
        
        with pytest.raises(ValueError):
            async with session_scope() as session:
                raise ValueError("Test exception")
        
        mock_manager.get_session.assert_called_once()
        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()


class TestTransactionScope:
    """Test transaction_scope context manager."""
    
    @pytest.mark.asyncio
    @patch('src.andamios_orm.core.session.get_session_manager')
    async def test_transaction_scope_success(self, mock_get_session_manager):
        """Test successful transaction_scope usage."""
        mock_session = AsyncMock(spec=AsyncSessionWrapper)
        mock_manager = Mock()
        mock_transaction_context = AsyncMock()
        mock_transaction_context.__aenter__.return_value = mock_session
        mock_transaction_context.__aexit__.return_value = None
        mock_manager.transaction.return_value = mock_transaction_context
        mock_get_session_manager.return_value = mock_manager
        
        async with transaction_scope() as session:
            assert session == mock_session
        
        mock_manager.transaction.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('src.andamios_orm.core.session.get_session_manager')
    async def test_transaction_scope_exception(self, mock_get_session_manager):
        """Test transaction_scope with exception."""
        mock_session = AsyncMock(spec=AsyncSessionWrapper)
        mock_manager = Mock()
        mock_transaction_context = AsyncMock()
        mock_transaction_context.__aenter__.return_value = mock_session
        mock_transaction_context.__aexit__.return_value = None
        mock_manager.transaction.return_value = mock_transaction_context
        mock_get_session_manager.return_value = mock_manager
        
        with pytest.raises(ValueError):
            async with transaction_scope() as session:
                raise ValueError("Test exception")
        
        mock_manager.transaction.assert_called_once()


class TestSessionHelpers:
    """Test session helper functions."""
    
    @pytest.mark.asyncio
    @patch('src.andamios_orm.core.session.session_scope')
    async def test_with_session(self, mock_session_scope):
        """Test with_session helper function."""
        mock_session = AsyncMock(spec=AsyncSessionWrapper)
        mock_session_scope.return_value.__aenter__.return_value = mock_session
        mock_session_scope.return_value.__aexit__ = AsyncMock()
        
        async def test_func(session):
            return "test_result"
        
        result = await with_session(test_func)
        
        assert result == "test_result"
    
    @pytest.mark.asyncio
    @patch('src.andamios_orm.core.session.transaction_scope')
    async def test_with_transaction(self, mock_transaction_scope):
        """Test with_transaction helper function."""
        mock_session = AsyncMock(spec=AsyncSessionWrapper)
        mock_transaction_scope.return_value.__aenter__.return_value = mock_session
        mock_transaction_scope.return_value.__aexit__ = AsyncMock()
        
        async def test_func(session):
            return "test_result"
        
        result = await with_transaction(test_func)
        
        assert result == "test_result"


class TestSessionManager:
    """Test SessionManager class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_engine = Mock(spec=Engine)
        self.session_manager = SessionManager(self.mock_engine)
    
    @patch('src.andamios_orm.core.session.sync_sessionmaker')
    def test_session_manager_init(self, mock_sessionmaker):
        """Test SessionManager initialization."""
        mock_sessionmaker.return_value = Mock()
        
        manager = SessionManager(self.mock_engine)
        
        mock_sessionmaker.assert_called_once_with(
            self.mock_engine,
            expire_on_commit=False
        )
        assert manager.engine == self.mock_engine
    
    @patch('src.andamios_orm.core.session.get_engine')
    @patch('src.andamios_orm.core.session.sync_sessionmaker')
    def test_session_manager_init_default_engine(self, mock_sessionmaker, mock_get_engine):
        """Test SessionManager initialization with default engine."""
        mock_get_engine.return_value = self.mock_engine
        mock_sessionmaker.return_value = Mock()
        
        manager = SessionManager()
        
        mock_get_engine.assert_called_once()
        assert manager.engine == self.mock_engine
    
    @pytest.mark.asyncio
    async def test_session_context_manager(self):
        """Test SessionManager session context manager."""
        mock_session = Mock(spec=Session)
        self.session_manager.sessionmaker = Mock(return_value=mock_session)
        
        with patch.object(AsyncSessionWrapper, 'close', new_callable=AsyncMock) as mock_close:
            async with self.session_manager.session() as session:
                assert isinstance(session, AsyncSessionWrapper)
                assert session._session == mock_session
            
            mock_close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_transaction_context_manager(self):
        """Test SessionManager transaction context manager."""
        mock_session = Mock(spec=Session)
        self.session_manager.sessionmaker = Mock(return_value=mock_session)
        
        with patch.object(AsyncSessionWrapper, 'close', new_callable=AsyncMock) as mock_close:
            with patch.object(AsyncSessionWrapper, 'commit', new_callable=AsyncMock) as mock_commit:
                async with self.session_manager.transaction() as session:
                    assert isinstance(session, AsyncSessionWrapper)
                
                mock_commit.assert_called_once()
                mock_close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_transaction_context_manager_exception(self):
        """Test SessionManager transaction context manager with exception."""
        mock_session = Mock(spec=Session)
        self.session_manager.sessionmaker = Mock(return_value=mock_session)
        
        with patch.object(AsyncSessionWrapper, 'close', new_callable=AsyncMock) as mock_close:
            with patch.object(AsyncSessionWrapper, 'rollback', new_callable=AsyncMock) as mock_rollback:
                with pytest.raises(ValueError):
                    async with self.session_manager.transaction() as session:
                        raise ValueError("Test exception")
                
                mock_rollback.assert_called_once()
                mock_close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_execute_raw_sql(self):
        """Test SessionManager execute_raw_sql method."""
        mock_session = Mock(spec=Session)
        mock_result = Mock()
        self.session_manager.sessionmaker = Mock(return_value=mock_session)
        
        with patch.object(AsyncSessionWrapper, 'close', new_callable=AsyncMock):
            with patch.object(AsyncSessionWrapper, 'execute', new_callable=AsyncMock) as mock_execute:
                mock_execute.return_value = mock_result
                
                result = await self.session_manager.execute_raw_sql("SELECT 1", {"param": "value"})
                
                # Check that execute was called once with the right SQL and parameters
                mock_execute.assert_called_once()
                call_args = mock_execute.call_args
                assert str(call_args[0][0]) == "SELECT 1"  # Check SQL text
                assert call_args[0][1] == {"param": "value"}  # Check parameters
                assert result == mock_result
    
    @pytest.mark.asyncio
    async def test_bulk_operations(self):
        """Test SessionManager bulk_operations method."""
        mock_session = Mock(spec=Session)
        self.session_manager.sessionmaker = Mock(return_value=mock_session)
        
        async def operation1(session):
            return "result1"
        
        async def operation2(session):
            return "result2"
        
        operations = [operation1, operation2]
        
        with patch.object(AsyncSessionWrapper, 'close', new_callable=AsyncMock):
            with patch.object(AsyncSessionWrapper, 'commit', new_callable=AsyncMock):
                results = await self.session_manager.bulk_operations(operations)
                
                assert results == ["result1", "result2"]


class TestGlobalSessionManager:
    """Test global session manager functions."""
    
    def test_get_session_manager_creates_default(self):
        """Test that get_session_manager creates default manager."""
        import src.andamios_orm.core.session as session_module
        session_module._session_manager = None
        
        with patch('src.andamios_orm.core.session.SessionManager') as mock_sm_class:
            mock_manager = Mock()
            mock_sm_class.return_value = mock_manager
            
            result = get_session_manager()
            
            mock_sm_class.assert_called_once()
            assert result == mock_manager
            assert session_module._session_manager == mock_manager
    
    def test_get_session_manager_returns_existing(self):
        """Test that get_session_manager returns existing manager."""
        import src.andamios_orm.core.session as session_module
        mock_manager = Mock()
        session_module._session_manager = mock_manager
        
        result = get_session_manager()
        
        assert result == mock_manager
    
    def test_set_session_manager(self):
        """Test set_session_manager function."""
        import src.andamios_orm.core.session as session_module
        mock_manager = Mock()
        
        set_session_manager(mock_manager)
        
        assert session_module._session_manager == mock_manager


class TestSessionmaker:
    """Test sessionmaker function."""
    
    @patch('src.andamios_orm.core.session.sync_sessionmaker')
    def test_sessionmaker(self, mock_sync_sessionmaker):
        """Test sessionmaker function."""
        mock_engine = Mock(spec=Engine)
        mock_session_maker = Mock()
        mock_sync_sessionmaker.return_value = mock_session_maker
        
        result = sessionmaker(mock_engine, custom_param="value")
        
        mock_sync_sessionmaker.assert_called_once_with(
            mock_engine,
            custom_param="value"
        )
        assert result == mock_session_maker


class TestCreateTablesDuckDBCompatible:
    """Test _create_tables_duckdb_compatible function."""
    
    @pytest.mark.asyncio
    @patch('asyncio.to_thread')
    @patch('src.andamios_orm.core.session.text')
    async def test_create_tables_duckdb_compatible(self, mock_text, mock_to_thread):
        """Test _create_tables_duckdb_compatible function."""
        from src.andamios_orm.core.session import _create_tables_duckdb_compatible
        
        mock_engine = Mock(spec=Engine)
        mock_conn = Mock()
        mock_context = Mock()
        mock_context.__enter__ = Mock(return_value=mock_conn)
        mock_context.__exit__ = Mock(return_value=None)
        mock_engine.connect.return_value = mock_context
        mock_to_thread.return_value = None
        
        await _create_tables_duckdb_compatible(mock_engine)
        
        # Should call to_thread with execute_ddl function
        mock_to_thread.assert_called_once()
        
        # Verify the DDL execution function works
        execute_ddl_func = mock_to_thread.call_args[0][0]
        execute_ddl_func()
        
        # Should have executed multiple DDL statements
        assert mock_conn.execute.call_count == 4  # projects, conversations, documents, repositories
        mock_conn.commit.assert_called_once()


class TestSessionCoverageEnhancements:
    """Additional tests to ensure comprehensive coverage of session.py"""
    
    @pytest.mark.asyncio
    async def test_async_session_wrapper_bulk_operations_error_handling(self, memory_engine):
        """Test AsyncSessionWrapper bulk operations error handling"""
        from src.andamios_orm.core.session import init_db, AsyncSessionWrapper
        from src.andamios_orm.models.project import Project
        from unittest.mock import patch, AsyncMock
        from sqlalchemy.exc import SQLAlchemyError
        
        init_db(memory_engine)
        
        from src.andamios_orm.core.session import _global_sessionmaker
        session = _global_sessionmaker()
        wrapper = AsyncSessionWrapper(session)
        
        # Test bulk_insert_mappings error handling
        with patch.object(session, 'bulk_insert_mappings', side_effect=SQLAlchemyError("Bulk insert failed", None, None)):
            with pytest.raises(DatabaseConnectionError, match="Failed to bulk insert"):
                await wrapper.bulk_insert_mappings(Project, [{"id": 1, "name": "test"}])
        
        # Test bulk_update_mappings error handling
        with patch.object(session, 'bulk_update_mappings', side_effect=SQLAlchemyError("Bulk update failed", None, None)):
            with pytest.raises(DatabaseConnectionError, match="Failed to bulk update"):
                await wrapper.bulk_update_mappings(Project, [{"id": 1, "name": "updated"}])
    
    @pytest.mark.asyncio
    async def test_async_session_wrapper_close_error_handling(self, memory_engine):
        """Test AsyncSessionWrapper close error handling"""
        from src.andamios_orm.core.session import init_db, AsyncSessionWrapper
        from unittest.mock import patch
        from sqlalchemy.exc import SQLAlchemyError
        
        init_db(memory_engine)
        
        from src.andamios_orm.core.session import _global_sessionmaker
        session = _global_sessionmaker()
        wrapper = AsyncSessionWrapper(session)
        
        # Test close error handling
        with patch.object(session, 'close', side_effect=SQLAlchemyError("Close failed", None, None)):
            with pytest.raises(DatabaseConnectionError, match="Failed to close"):
                await wrapper.close()
    
    @pytest.mark.asyncio
    async def test_session_scope_error_handling(self, memory_engine):
        """Test session_scope error handling during session creation"""
        from src.andamios_orm.core.session import session_scope, init_db
        from unittest.mock import patch
        
        init_db(memory_engine)
        
        # Mock get_session to raise exception
        with patch('src.andamios_orm.core.session.get_session') as mock_get_session:
            mock_get_session.side_effect = Exception("Session creation failed")
            
            try:
                async with session_scope() as session:
                    # Should not reach this point
                    assert False, "Should have raised exception"
            except Exception as e:
                assert "Session creation failed" in str(e)
    
    @pytest.mark.asyncio
    async def test_transaction_scope_rollback_on_exception(self, memory_engine):
        """Test transaction_scope properly rolls back on exception"""
        from src.andamios_orm.core.session import transaction_scope, init_db
        from unittest.mock import AsyncMock, patch
        
        init_db(memory_engine)
        
        mock_session = AsyncMock()
        
        with patch('src.andamios_orm.core.session.get_session', return_value=mock_session):
            try:
                async with transaction_scope() as session:
                    assert session is mock_session
                    raise Exception("Test exception")
            except Exception as e:
                assert "Test exception" in str(e)
        
        # Verify rollback was called
        mock_session.rollback.assert_called_once()
    
    def test_init_db_with_none_engine(self):
        """Test init_db creates memory engine when None provided"""
        from src.andamios_orm.core.session import init_db
        
        # Should create memory engine when None is passed
        init_db(None)
        
        from src.andamios_orm.core.session import _global_engine, _global_sessionmaker
        assert _global_engine is not None
        assert _global_sessionmaker is not None
    
    @pytest.mark.asyncio
    async def test_get_session_with_existing_global_state(self, memory_engine):
        """Test get_session uses existing global sessionmaker"""
        from src.andamios_orm.core.session import init_db, get_session
        
        # Initialize with specific engine
        init_db(memory_engine)
        
        # Get session should use existing global state
        session = await get_session()
        assert session is not None
        
        # Get another session - should reuse sessionmaker
        session2 = await get_session()
        assert session2 is not None