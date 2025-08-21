"""
Unit tests for core.engine module
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy import Engine
from sqlalchemy.pool import StaticPool

from src.andamios_orm.core.engine import (
    create_engine,
    create_memory_engine,
    create_file_engine,
    get_engine,
    set_engine,
    engine_context,
    ensure_uvloop,
    create_optimized_engine,
    _engine,
    _async_engine
)


class TestCreateEngine:
    """Test create_engine function."""
    
    @patch('src.andamios_orm.core.engine.create_sync_engine')
    @patch('src.andamios_orm.core.engine.uvloop')
    def test_create_engine_default(self, mock_uvloop, mock_create_sync):
        """Test create_engine with default parameters."""
        mock_engine = Mock(spec=Engine)
        mock_create_sync.return_value = mock_engine
        
        result = create_engine()
        
        mock_uvloop.install.assert_called_once()
        mock_create_sync.assert_called_once_with(
            "duckdb:///:memory:",
            echo=False,
            future=True,
            poolclass=StaticPool
        )
        assert result == mock_engine
    
    @patch('src.andamios_orm.core.engine.create_sync_engine')
    @patch('src.andamios_orm.core.engine.uvloop')
    def test_create_engine_custom_url(self, mock_uvloop, mock_create_sync):
        """Test create_engine with custom URL."""
        mock_engine = Mock(spec=Engine)
        mock_create_sync.return_value = mock_engine
        custom_url = "duckdb:///test.db"
        
        result = create_engine(custom_url, echo=True)
        
        mock_create_sync.assert_called_once_with(
            custom_url,
            echo=True,
            future=True,
            poolclass=None
        )
        assert result == mock_engine
    
    @patch('src.andamios_orm.core.engine.create_sync_engine')
    @patch('src.andamios_orm.core.engine.uvloop')
    def test_create_engine_removes_pool_params(self, mock_uvloop, mock_create_sync):
        """Test that pool parameters are removed for DuckDB."""
        mock_engine = Mock(spec=Engine)
        mock_create_sync.return_value = mock_engine
        
        create_engine(pool_size=10, max_overflow=20)
        
        # Check that pool_size and max_overflow are not passed
        call_kwargs = mock_create_sync.call_args[1]
        assert "pool_size" not in call_kwargs
        assert "max_overflow" not in call_kwargs


class TestCreateMemoryEngine:
    """Test create_memory_engine function."""
    
    @patch('src.andamios_orm.core.engine.create_engine')
    def test_create_memory_engine_default(self, mock_create_engine):
        """Test create_memory_engine with default parameters."""
        mock_engine = Mock(spec=Engine)
        mock_create_engine.return_value = mock_engine
        
        result = create_memory_engine()
        
        mock_create_engine.assert_called_once_with("duckdb:///:memory:", echo=False)
        assert result == mock_engine
    
    @patch('src.andamios_orm.core.engine.create_engine')
    def test_create_memory_engine_with_echo(self, mock_create_engine):
        """Test create_memory_engine with echo enabled."""
        mock_engine = Mock(spec=Engine)
        mock_create_engine.return_value = mock_engine
        
        result = create_memory_engine(echo=True)
        
        mock_create_engine.assert_called_once_with("duckdb:///:memory:", echo=True)
        assert result == mock_engine


class TestCreateFileEngine:
    """Test create_file_engine function."""
    
    @patch('src.andamios_orm.core.engine.create_engine')
    def test_create_file_engine(self, mock_create_engine):
        """Test create_file_engine with file path."""
        mock_engine = Mock(spec=Engine)
        mock_create_engine.return_value = mock_engine
        db_path = "/path/to/test.db"
        
        result = create_file_engine(db_path)
        
        mock_create_engine.assert_called_once_with(f"duckdb:///{db_path}", echo=False)
        assert result == mock_engine
    
    @patch('src.andamios_orm.core.engine.create_engine')
    def test_create_file_engine_with_options(self, mock_create_engine):
        """Test create_file_engine with additional options."""
        mock_engine = Mock(spec=Engine)
        mock_create_engine.return_value = mock_engine
        db_path = "/path/to/test.db"
        
        result = create_file_engine(db_path, echo=True, custom_param="value")
        
        mock_create_engine.assert_called_once_with(
            f"duckdb:///{db_path}", 
            echo=True, 
            custom_param="value"
        )
        assert result == mock_engine


class TestGlobalEngineManagement:
    """Test global engine management functions."""
    
    def test_get_engine_creates_default(self):
        """Test that get_engine creates default engine when none exists."""
        # Clear global state
        import src.andamios_orm.core.engine as engine_module
        engine_module._engine = None
        
        with patch('src.andamios_orm.core.engine.create_memory_engine') as mock_create:
            mock_engine = Mock(spec=Engine)
            mock_create.return_value = mock_engine
            
            result = get_engine()
            
            mock_create.assert_called_once()
            assert result == mock_engine
            assert engine_module._engine == mock_engine
    
    def test_get_engine_returns_existing(self):
        """Test that get_engine returns existing engine."""
        import src.andamios_orm.core.engine as engine_module
        mock_engine = Mock(spec=Engine)
        engine_module._engine = mock_engine
        
        result = get_engine()
        
        assert result == mock_engine
    
    def test_set_engine(self):
        """Test set_engine function."""
        import src.andamios_orm.core.engine as engine_module
        mock_engine = Mock(spec=Engine)
        
        set_engine(mock_engine)
        
        assert engine_module._engine == mock_engine
    
    @patch('src.andamios_orm.core.engine.create_async_engine')
    def test_get_async_engine_creates_default(self, mock_create_async):
        """Test that get_async_engine creates default async engine."""
        from src.andamios_orm.core.engine import get_async_engine
        import src.andamios_orm.core.engine as engine_module
        
        # Clear global state
        engine_module._async_engine = None
        
        mock_async_engine = Mock()
        mock_create_async.return_value = mock_async_engine
        
        with patch('src.andamios_orm.core.engine.get_engine') as mock_get_engine:
            mock_get_engine.return_value = Mock(spec=Engine)
            
            result = get_async_engine()
            
            mock_create_async.assert_called_once_with(
                "sqlite+aiosqlite:///:memory:",
                echo=False,
                future=True
            )
            assert result == mock_async_engine


class TestEngineContext:
    """Test engine_context async context manager."""
    
    @pytest.mark.asyncio
    @patch('src.andamios_orm.core.engine.create_engine')
    async def test_engine_context_success(self, mock_create_engine):
        """Test successful engine context usage."""
        mock_engine = Mock(spec=Engine)
        mock_engine.dispose = Mock()
        mock_create_engine.return_value = mock_engine
        
        async with engine_context("test://url", echo=True) as engine:
            assert engine == mock_engine
        
        mock_create_engine.assert_called_once_with("test://url", echo=True)
        mock_engine.dispose.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('src.andamios_orm.core.engine.create_engine')
    async def test_engine_context_exception(self, mock_create_engine):
        """Test engine context with exception."""
        mock_engine = Mock(spec=Engine)
        mock_engine.dispose = Mock()
        mock_create_engine.return_value = mock_engine
        
        with pytest.raises(ValueError):
            async with engine_context() as engine:
                raise ValueError("Test exception")
        
        # Engine should still be disposed
        mock_engine.dispose.assert_called_once()


class TestEnsureUvloop:
    """Test ensure_uvloop function."""
    
    @patch('src.andamios_orm.core.engine.uvloop')
    @patch('src.andamios_orm.core.engine.asyncio')
    def test_ensure_uvloop_not_installed(self, mock_asyncio, mock_uvloop):
        """Test ensure_uvloop when uvloop is not installed."""
        mock_uvloop.install = Mock()
        mock_uvloop.EventLoopPolicy = Mock()
        mock_asyncio.get_event_loop_policy.return_value = Mock()
        
        ensure_uvloop()
        
        mock_uvloop.install.assert_called_once()
    
    @patch('src.andamios_orm.core.engine.uvloop')
    @patch('src.andamios_orm.core.engine.asyncio')
    def test_ensure_uvloop_already_installed(self, mock_asyncio, mock_uvloop):
        """Test ensure_uvloop when uvloop is already installed."""
        mock_uvloop.install = Mock()
        mock_uvloop.EventLoopPolicy = Mock()
        mock_policy = Mock(spec=mock_uvloop.EventLoopPolicy)
        mock_asyncio.get_event_loop_policy.return_value = mock_policy
        
        ensure_uvloop()
        
        # install should not be called if already using uvloop policy
        mock_uvloop.install.assert_not_called()
    
    @patch('src.andamios_orm.core.engine.uvloop')
    def test_ensure_uvloop_exception_handling(self, mock_uvloop):
        """Test ensure_uvloop handles exceptions gracefully."""
        mock_uvloop.install = Mock(side_effect=Exception("Test exception"))
        
        # Should not raise exception
        ensure_uvloop()
    
    @patch('src.andamios_orm.core.engine.uvloop', None)
    def test_ensure_uvloop_no_uvloop_module(self):
        """Test ensure_uvloop when uvloop module is not available."""
        # Should not raise exception when uvloop is not available
        ensure_uvloop()


class TestCreateOptimizedEngine:
    """Test create_optimized_engine function."""
    
    @patch('src.andamios_orm.core.engine.ensure_uvloop')
    @patch('src.andamios_orm.core.engine.create_sync_engine')
    def test_create_optimized_engine_analytics(self, mock_create_sync, mock_ensure_uvloop):
        """Test create_optimized_engine with analytics optimizations."""
        mock_engine = Mock(spec=Engine)
        mock_create_sync.return_value = mock_engine
        
        result = create_optimized_engine(
            "duckdb:///test.db",
            echo=True,
            optimize_for_analytics=True
        )
        
        mock_ensure_uvloop.assert_called_once()
        mock_create_sync.assert_called_once()
        
        # Check that analytics config is included
        call_kwargs = mock_create_sync.call_args[1]
        assert "connect_args" in call_kwargs
        assert "config" in call_kwargs["connect_args"]
        assert call_kwargs["connect_args"]["config"]["enable_optimizer"] is True
        assert result == mock_engine
    
    @patch('src.andamios_orm.core.engine.ensure_uvloop')
    @patch('src.andamios_orm.core.engine.create_sync_engine')
    def test_create_optimized_engine_memory(self, mock_create_sync, mock_ensure_uvloop):
        """Test create_optimized_engine with memory database."""
        mock_engine = Mock(spec=Engine)
        mock_create_sync.return_value = mock_engine
        
        result = create_optimized_engine("duckdb:///:memory:")
        
        call_kwargs = mock_create_sync.call_args[1]
        assert call_kwargs["poolclass"] == StaticPool
        assert "check_same_thread" in call_kwargs["connect_args"]
        assert call_kwargs["connect_args"]["check_same_thread"] is False
    
    @patch('src.andamios_orm.core.engine.ensure_uvloop')
    @patch('src.andamios_orm.core.engine.create_sync_engine')
    def test_create_optimized_engine_no_analytics(self, mock_create_sync, mock_ensure_uvloop):
        """Test create_optimized_engine without analytics optimizations."""
        mock_engine = Mock(spec=Engine)
        mock_create_sync.return_value = mock_engine
        
        result = create_optimized_engine(optimize_for_analytics=False)
        
        call_kwargs = mock_create_sync.call_args[1]
        # Should not have analytics config when disabled
        if "connect_args" in call_kwargs and "config" in call_kwargs["connect_args"]:
            assert "enable_optimizer" not in call_kwargs["connect_args"]["config"]


class TestEngineIntegration:
    """Integration tests for engine functionality."""
    
    def test_engine_creation_and_disposal(self):
        """Test actual engine creation and disposal."""
        engine = create_memory_engine()
        
        assert engine is not None
        assert isinstance(engine, Engine)
        
        # Test disposal
        engine.dispose()
    
    def test_file_engine_creation(self, temp_dir):
        """Test file engine creation with temporary file."""
        db_path = temp_dir / "test.db"
        engine = create_file_engine(str(db_path))
        
        assert engine is not None
        assert isinstance(engine, Engine)
        
        engine.dispose()
    
    @pytest.mark.asyncio
    async def test_engine_context_integration(self):
        """Test engine context manager integration."""
        async with engine_context() as engine:
            assert engine is not None
            assert isinstance(engine, Engine)
            
            # Engine should be usable
            with engine.connect() as conn:
                result = conn.execute("SELECT 1 as test")
                assert result.scalar() == 1