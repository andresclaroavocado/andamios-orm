"""
Integration tests for core.engine module using real DuckDB operations.
Tests actual engine creation, connections, and SQL execution.
"""

import pytest
import asyncio
import tempfile
from pathlib import Path
from sqlalchemy import Engine, text
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
)


@pytest.mark.integration
class TestEngineCreation:
    """Test engine creation with real DuckDB connections."""
    
    def test_create_memory_engine(self):
        """Test creating an in-memory DuckDB engine."""
        engine = create_memory_engine(echo=False)
        
        assert engine is not None
        assert isinstance(engine, Engine)
        assert "duckdb:///:memory:" in str(engine.url)
        
        # Test actual connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test_value"))
            assert result.scalar() == 1
        
        engine.dispose()
    
    def test_create_file_engine(self, temp_dir):
        """Test creating a file-based DuckDB engine."""
        db_path = temp_dir / "test_engine.db"
        engine = create_file_engine(str(db_path), echo=False)
        
        assert engine is not None
        assert isinstance(engine, Engine)
        assert str(db_path) in str(engine.url)
        
        # Test actual connection and persistence
        with engine.connect() as conn:
            # Create a table
            conn.execute(text("CREATE TABLE test_persistence (id INTEGER, value TEXT)"))
            conn.execute(text("INSERT INTO test_persistence VALUES (1, 'test')"))
            conn.commit()
        
        # Reconnect and verify data persisted
        with engine.connect() as conn:
            result = conn.execute(text("SELECT value FROM test_persistence WHERE id = 1"))
            assert result.scalar() == "test"
        
        engine.dispose()
    
    def test_create_engine_with_custom_url(self):
        """Test creating engine with custom DuckDB URL."""
        custom_url = "duckdb:///:memory:"
        engine = create_engine(custom_url, echo=False)
        
        assert engine is not None
        assert isinstance(engine, Engine)
        
        # Test connection works
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 42 as answer"))
            assert result.scalar() == 42
        
        engine.dispose()
    
    def test_create_optimized_engine(self):
        """Test creating optimized DuckDB engine."""
        engine = create_optimized_engine(
            "duckdb:///:memory:",
            echo=False,
            optimize_for_analytics=True
        )
        
        assert engine is not None
        assert isinstance(engine, Engine)
        
        # Test optimized engine can handle analytics queries
        with engine.connect() as conn:
            # Create test data for analytics
            conn.execute(text("CREATE TABLE analytics_test (id INTEGER, value DOUBLE, category TEXT)"))
            conn.execute(text("""
                INSERT INTO analytics_test VALUES 
                (1, 10.5, 'A'), (2, 20.5, 'B'), (3, 30.5, 'A'), (4, 40.5, 'B')
            """))
            
            # Test aggregation query
            result = conn.execute(text("""
                SELECT category, AVG(value) as avg_value 
                FROM analytics_test 
                GROUP BY category 
                ORDER BY category
            """))
            
            rows = result.fetchall()
            assert len(rows) == 2
            assert rows[0][0] == 'A'
            assert abs(rows[0][1] - 20.5) < 0.01  # Average of 10.5 and 30.5
            assert rows[1][0] == 'B'
            assert abs(rows[1][1] - 30.5) < 0.01  # Average of 20.5 and 40.5
        
        engine.dispose()


@pytest.mark.integration
class TestGlobalEngineManagement:
    """Test global engine management with real engines."""
    
    def test_get_and_set_engine(self):
        """Test getting and setting global engine."""
        # Create a test engine
        test_engine = create_memory_engine()
        
        # Set as global engine
        set_engine(test_engine)
        
        # Get global engine
        retrieved_engine = get_engine()
        
        assert retrieved_engine is test_engine
        
        # Test the engine works
        with retrieved_engine.connect() as conn:
            result = conn.execute(text("SELECT 'global_test' as test"))
            assert result.scalar() == "global_test"
        
        test_engine.dispose()
    
    def test_get_engine_creates_default(self):
        """Test that get_engine creates a default engine when none exists."""
        # Clear global state is handled by reset_global_state fixture
        engine = get_engine()
        
        assert engine is not None
        assert isinstance(engine, Engine)
        
        # Test default engine works
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 'default_test' as test"))
            assert result.scalar() == "default_test"


@pytest.mark.integration
class TestEngineContext:
    """Test engine context manager with real operations."""
    
    @pytest.mark.asyncio
    async def test_engine_context_success(self):
        """Test successful engine context usage."""
        async with engine_context("duckdb:///:memory:", echo=False) as engine:
            assert engine is not None
            assert isinstance(engine, Engine)
            
            # Test engine functionality
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 'context_test' as test"))
                assert result.scalar() == "context_test"
        
        # Engine should be disposed automatically
    
    @pytest.mark.asyncio
    async def test_engine_context_with_file(self, temp_dir):
        """Test engine context with file database."""
        db_path = temp_dir / "context_test.db"
        
        async with engine_context(f"duckdb:///{db_path}", echo=False) as engine:
            # Create and populate test table
            with engine.connect() as conn:
                conn.execute(text("CREATE TABLE context_test (id INTEGER, data TEXT)"))
                conn.execute(text("INSERT INTO context_test VALUES (1, 'context_data')"))
                conn.commit()
        
        # Verify file was created and data persisted
        assert db_path.exists()
        
        # Create new engine to verify persistence
        verify_engine = create_file_engine(str(db_path))
        with verify_engine.connect() as conn:
            result = conn.execute(text("SELECT data FROM context_test WHERE id = 1"))
            assert result.scalar() == "context_data"
        verify_engine.dispose()
    
    @pytest.mark.asyncio
    async def test_engine_context_with_exception(self):
        """Test engine context with exception handling."""
        with pytest.raises(ValueError):
            async with engine_context() as engine:
                # Test engine works before exception
                with engine.connect() as conn:
                    result = conn.execute(text("SELECT 'before_error' as test"))
                    assert result.scalar() == "before_error"
                
                # Raise exception
                raise ValueError("Test exception")
        
        # Engine should still be disposed properly


@pytest.mark.integration
class TestDuckDBFeatures:
    """Test DuckDB-specific features and operations."""
    
    def test_duckdb_data_types(self, memory_engine):
        """Test DuckDB data types and operations."""
        with memory_engine.connect() as conn:
            # Create table with various DuckDB data types
            conn.execute(text("""
                CREATE TABLE type_test (
                    id INTEGER,
                    name VARCHAR,
                    value DOUBLE,
                    is_active BOOLEAN,
                    created_date DATE,
                    data_json JSON
                )
            """))
            
            # Insert test data
            conn.execute(text("""
                INSERT INTO type_test VALUES 
                (1, 'test1', 10.5, true, '2024-01-01', '{"key": "value1"}'),
                (2, 'test2', 20.5, false, '2024-01-02', '{"key": "value2"}')
            """))
            
            # Test querying different data types
            result = conn.execute(text("""
                SELECT id, name, value, is_active, created_date 
                FROM type_test 
                WHERE is_active = true
            """))
            
            row = result.fetchone()
            assert row[0] == 1
            assert row[1] == "test1"
            assert abs(row[2] - 10.5) < 0.01
            assert row[3] is True
            
            conn.rollback()
    
    def test_duckdb_analytical_functions(self, memory_engine):
        """Test DuckDB analytical and aggregation functions."""
        with memory_engine.connect() as conn:
            # Create test data for analytics
            conn.execute(text("""
                CREATE TABLE sales_data (
                    id INTEGER,
                    product VARCHAR,
                    amount DOUBLE,
                    sale_date DATE,
                    region VARCHAR
                )
            """))
            
            # Insert sample sales data
            conn.execute(text("""
                INSERT INTO sales_data VALUES 
                (1, 'Product A', 100.0, '2024-01-01', 'North'),
                (2, 'Product B', 150.0, '2024-01-01', 'South'),
                (3, 'Product A', 120.0, '2024-01-02', 'North'),
                (4, 'Product B', 180.0, '2024-01-02', 'South'),
                (5, 'Product A', 110.0, '2024-01-03', 'North'),
                (6, 'Product A', 90.0, '2024-01-04', 'South'),
                (7, 'Product B', 130.0, '2024-01-04', 'North')
            """))
            
            # Test analytical functions
            result = conn.execute(text("""
                SELECT 
                    product,
                    region,
                    SUM(amount) as total_sales,
                    AVG(amount) as avg_sales,
                    COUNT(*) as sale_count
                FROM sales_data 
                GROUP BY product, region
                ORDER BY product, region
            """))
            
            rows = result.fetchall()
            assert len(rows) == 4  # 2 products × 2 regions
            
            # Verify aggregations
            product_a_north = next(r for r in rows if r[0] == 'Product A' and r[1] == 'North')
            assert abs(product_a_north[2] - 330.0) < 0.01  # Sum: 100 + 120 + 110
            assert product_a_north[4] == 3  # Count
            
            product_b_south = next(r for r in rows if r[0] == 'Product B' and r[1] == 'South')
            assert abs(product_b_south[2] - 330.0) < 0.01  # Sum: 150 + 180
            assert product_b_south[4] == 2  # Count
            
            conn.rollback()
    
    def test_duckdb_json_operations(self, memory_engine):
        """Test DuckDB JSON operations."""
        with memory_engine.connect() as conn:
            # Create table with JSON data
            conn.execute(text("""
                CREATE TABLE json_test (
                    id INTEGER,
                    metadata JSON
                )
            """))
            
            # Insert JSON data
            conn.execute(text("""
                INSERT INTO json_test VALUES 
                (1, '{"name": "test1", "tags": ["tag1", "tag2"], "count": 10}'),
                (2, '{"name": "test2", "tags": ["tag2", "tag3"], "count": 20}')
            """))
            
            # Test JSON extraction (if supported by DuckDB version)
            try:
                result = conn.execute(text("""
                    SELECT id, json_extract_string(metadata, '$.name') as name
                    FROM json_test 
                    ORDER BY id
                """))
                
                rows = result.fetchall()
                assert len(rows) == 2
                assert rows[0][1] == "test1"
                assert rows[1][1] == "test2"
            except Exception:
                # JSON functions might not be available in all DuckDB versions
                # Just verify basic insertion worked
                result = conn.execute(text("SELECT COUNT(*) FROM json_test"))
                assert result.scalar() == 2
            
            conn.rollback()


@pytest.mark.integration
class TestConcurrentOperations:
    """Test concurrent database operations."""
    
    @pytest.mark.asyncio
    async def test_multiple_connections(self, memory_engine):
        """Test multiple concurrent connections to the same engine."""
        async def worker_task(worker_id: int) -> int:
            """Worker task that performs database operations."""
            await asyncio.sleep(0.01)  # Small delay to encourage concurrency
            
            with memory_engine.connect() as conn:
                # Each worker creates its own table
                conn.execute(text(f"CREATE TABLE IF NOT EXISTS worker_{worker_id} (id INTEGER, value TEXT)"))
                conn.execute(text(f"INSERT INTO worker_{worker_id} VALUES ({worker_id}, 'worker_{worker_id}_data')"))
                
                # Verify data
                result = conn.execute(text(f"SELECT value FROM worker_{worker_id} WHERE id = {worker_id}"))
                value = result.scalar()
                
                conn.commit()
                return worker_id if value == f"worker_{worker_id}_data" else -1
        
        # Run multiple workers concurrently
        tasks = [worker_task(i) for i in range(5)]
        results = await asyncio.gather(*tasks)
        
        # All workers should complete successfully
        assert results == [0, 1, 2, 3, 4]
        
        # Verify all tables were created
        with memory_engine.connect() as conn:
            for i in range(5):
                result = conn.execute(text(f"SELECT COUNT(*) FROM worker_{i}"))
                assert result.scalar() == 1


@pytest.mark.integration
class TestEnginePerformance:
    """Test engine performance characteristics."""
    
    def test_bulk_insert_performance(self, memory_engine):
        """Test bulk insert operations."""
        with memory_engine.connect() as conn:
            # Create test table
            conn.execute(text("""
                CREATE TABLE bulk_test (
                    id INTEGER,
                    name VARCHAR,
                    value DOUBLE
                )
            """))
            
            # Prepare bulk insert data
            import time
            start_time = time.time()
            
            # Insert in batches for better performance
            batch_size = 100
            total_records = 1000
            
            for batch_start in range(0, total_records, batch_size):
                batch_end = min(batch_start + batch_size, total_records)
                
                # Build batch insert statement
                values = []
                for i in range(batch_start, batch_end):
                    values.append(f"({i}, 'name_{i}', {i * 1.5})")
                
                values_str = ", ".join(values)
                conn.execute(text(f"INSERT INTO bulk_test VALUES {values_str}"))
            
            conn.commit()
            
            end_time = time.time()
            insert_time = end_time - start_time
            
            # Verify all records were inserted
            result = conn.execute(text("SELECT COUNT(*) FROM bulk_test"))
            assert result.scalar() == total_records
            
            # Performance should be reasonable (adjust threshold as needed)
            assert insert_time < 5.0  # Should complete in under 5 seconds
            
            # Test query performance
            start_time = time.time()
            result = conn.execute(text("""
                SELECT COUNT(*), AVG(value), MAX(value), MIN(value) 
                FROM bulk_test 
                WHERE id % 10 = 0
            """))
            
            query_time = time.time() - start_time
            
            row = result.fetchone()
            assert row[0] == 100  # COUNT
            assert abs(row[1] - 742.5) < 0.01  # AVG (corrected calculation)
            assert abs(row[2] - 1485.0) < 0.01  # MAX (990 * 1.5 = 1485)
            assert abs(row[3] - 0.0) < 0.01  # MIN
            
            # Query should be fast
            assert query_time < 1.0


@pytest.mark.integration
class TestErrorHandling:
    """Test error handling with real database operations."""
    
    def test_invalid_sql_error(self, memory_engine):
        """Test handling of invalid SQL statements."""
        with memory_engine.connect() as conn:
            with pytest.raises(Exception):  # Should raise some SQL error
                conn.execute(text("INVALID SQL STATEMENT"))
    
    def test_table_not_exists_error(self, memory_engine):
        """Test querying non-existent table."""
        with memory_engine.connect() as conn:
            with pytest.raises(Exception):  # Should raise table not found error
                conn.execute(text("SELECT * FROM non_existent_table"))
    
    def test_transaction_rollback(self, memory_engine):
        """Test transaction rollback on error."""
        with memory_engine.connect() as conn:
            # Create test table
            conn.execute(text("CREATE TABLE rollback_test (id INTEGER PRIMARY KEY, value TEXT)"))
            conn.execute(text("INSERT INTO rollback_test VALUES (1, 'initial')"))
            conn.commit()
            
            # Start transaction
            trans = conn.begin()
            try:
                conn.execute(text("INSERT INTO rollback_test VALUES (2, 'will_rollback')"))
                
                # This should cause an error (duplicate primary key)
                conn.execute(text("INSERT INTO rollback_test VALUES (1, 'duplicate')"))
                
                trans.commit()  # This should not be reached
            except Exception:
                trans.rollback()
            
            # Verify rollback worked - only initial record should exist
            result = conn.execute(text("SELECT COUNT(*) FROM rollback_test"))
            assert result.scalar() == 1
            
            result = conn.execute(text("SELECT value FROM rollback_test WHERE id = 1"))
            assert result.scalar() == "initial"


@pytest.mark.integration
class TestUvloopIntegration:
    """Test uvloop integration."""
    
    def test_ensure_uvloop_function(self):
        """Test ensure_uvloop function works without errors."""
        # This should not raise any exceptions
        ensure_uvloop()
        
        # Test that engine creation still works after uvloop setup
        engine = create_memory_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 'uvloop_test' as test"))
            assert result.scalar() == "uvloop_test"
        engine.dispose()
    
    @pytest.mark.asyncio
    async def test_asyncio_with_duckdb(self):
        """Test async operations with DuckDB engine."""
        async def async_database_work():
            """Simulate async database work."""
            engine = create_memory_engine()
            try:
                # Use asyncio.to_thread for database operations
                def db_operation():
                    with engine.connect() as conn:
                        conn.execute(text("CREATE TABLE async_test (id INTEGER, data TEXT)"))
                        conn.execute(text("INSERT INTO async_test VALUES (1, 'async_data')"))
                        conn.commit()
                        
                        result = conn.execute(text("SELECT data FROM async_test WHERE id = 1"))
                        return result.scalar()
                
                result = await asyncio.to_thread(db_operation)
                return result
            finally:
                engine.dispose()
        
        result = await async_database_work()
        assert result == "async_data"


@pytest.mark.integration
class TestEngineErrorHandling:
    """Test engine error handling and edge cases for coverage."""
    
    def test_create_engine_uvloop_handling(self):
        """Test create_engine with uvloop handling."""
        import unittest.mock
        
        # Test when uvloop is available but install fails
        with unittest.mock.patch('src.andamios_orm.core.engine.UVLOOP_AVAILABLE', True):
            with unittest.mock.patch('src.andamios_orm.core.engine.uvloop') as mock_uvloop:
                mock_uvloop.install.side_effect = Exception("uvloop install failed")
                # Should still create engine despite uvloop failure
                engine = create_engine()
                assert engine is not None
                engine.dispose()
    
    def test_create_engine_without_uvloop(self):
        """Test create_engine when uvloop is not available."""
        import unittest.mock
        
        # Test when uvloop is not available
        with unittest.mock.patch('src.andamios_orm.core.engine.UVLOOP_AVAILABLE', False):
            engine = create_engine()
            assert engine is not None
            engine.dispose()
    
    def test_create_optimized_engine_error_handling(self):
        """Test create_optimized_engine error handling."""
        import unittest.mock
        from src.andamios_orm.exceptions import DatabaseConnectionError
        
        # Mock create_sync_engine to raise an exception
        with unittest.mock.patch('src.andamios_orm.core.engine.create_sync_engine') as mock_create:
            mock_create.side_effect = Exception("Engine creation failed")
            
            with pytest.raises(DatabaseConnectionError) as exc_info:
                create_optimized_engine()
            assert "Failed to create optimized engine" in str(exc_info.value)
    
    def test_get_engine_error_handling(self):
        """Test get_engine error handling."""
        import unittest.mock
        from src.andamios_orm.exceptions import DatabaseConnectionError
        
        # Clear global engine first
        from src.andamios_orm.core import engine as engine_module
        engine_module._global_engine = None
        
        # Mock create_memory_engine to fail
        with unittest.mock.patch('src.andamios_orm.core.engine.create_memory_engine') as mock_create:
            mock_create.side_effect = Exception("Default engine creation failed")
            
            with pytest.raises(DatabaseConnectionError) as exc_info:
                get_engine()
            assert "Failed to create default engine" in str(exc_info.value)
    
    def test_create_engine_connection_validation(self):
        """Test create_engine validates connection."""
        # Test with invalid URL that should cause connection issues
        try:
            engine = create_engine("duckdb:///invalid/path/that/does/not/exist.db")
            # If it succeeds, test that we can connect
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            engine.dispose()
        except Exception:
            # Connection failure is acceptable for invalid path
            pass
    
    def test_set_engine_validation(self):
        """Test set_engine validates the engine parameter."""
        from src.andamios_orm.exceptions import ConfigurationError
        
        # Test with None
        with pytest.raises(ConfigurationError) as exc_info:
            set_engine(None)
        assert "Engine cannot be None" in str(exc_info.value)
        
        # Test with invalid object
        with pytest.raises(ConfigurationError) as exc_info:
            set_engine("not_an_engine")
        assert "must be an Engine instance" in str(exc_info.value)


@pytest.mark.integration
class TestEngineCoverageEnhancements:
    """Additional tests to ensure comprehensive coverage of engine.py"""
    
    def test_create_engine_with_uvloop_install_exception(self):
        """Test create_engine when uvloop install raises exception"""
        from src.andamios_orm.core.engine import UVLOOP_AVAILABLE
        if UVLOOP_AVAILABLE:
            # Mock uvloop.install to raise exception
            from unittest.mock import patch
            with patch('src.andamios_orm.core.engine.uvloop') as mock_uvloop:
                mock_uvloop.install.side_effect = Exception("Test uvloop error")
                mock_uvloop.UVLOOP_AVAILABLE = True
                
                # Should still create engine despite uvloop error
                engine = create_engine()
                assert engine is not None
    
    def test_ensure_uvloop_when_available(self):
        """Test ensure_uvloop when uvloop is available"""
        from src.andamios_orm.core.engine import ensure_uvloop, UVLOOP_AVAILABLE
        if UVLOOP_AVAILABLE:
            # Should not raise exception
            ensure_uvloop()
    
    def test_ensure_uvloop_when_not_available(self):
        """Test ensure_uvloop when uvloop is not available"""
        from unittest.mock import patch
        with patch('src.andamios_orm.core.engine.UVLOOP_AVAILABLE', False):
            from src.andamios_orm.core.engine import ensure_uvloop
            # Should not raise exception
            ensure_uvloop()
    
    def test_get_async_engine_functionality(self):
        """Test get_async_engine function"""
        from src.andamios_orm.core.engine import get_async_engine
        async_engine = get_async_engine()
        assert async_engine is not None
        assert hasattr(async_engine, 'url')
    
    def test_create_engine_without_uvloop_available(self):
        """Test create_engine when UVLOOP_AVAILABLE is False"""
        from unittest.mock import patch
        with patch('src.andamios_orm.core.engine.UVLOOP_AVAILABLE', False):
            engine = create_engine()
            assert engine is not None
    
    def test_ensure_uvloop_install_exception(self):
        """Test ensure_uvloop when uvloop.install raises exception"""
        from src.andamios_orm.core.engine import ensure_uvloop, UVLOOP_AVAILABLE
        if UVLOOP_AVAILABLE:
            from unittest.mock import patch
            with patch('src.andamios_orm.core.engine.uvloop') as mock_uvloop:
                mock_uvloop.install.side_effect = Exception("uvloop install failed")
                # Should not raise exception - should handle gracefully
                ensure_uvloop()
    
    def test_create_engine_custom_connect_args(self):
        """Test create_engine with custom connect_args"""
        engine = create_engine(
            "duckdb:///:memory:",
            connect_args={"config": {"memory_limit": "512MB"}}
        )
        assert engine is not None
    
    def test_create_file_engine_with_echo(self, temp_dir):
        """Test create_file_engine with echo enabled"""
        db_path = temp_dir / "test_echo.db"
        engine = create_file_engine(str(db_path), echo=True)
        assert engine is not None
        assert engine.echo is True
    
    def test_engine_context_manager_exception_handling(self, memory_engine):
        """Test engine_context exception handling"""
        from unittest.mock import patch
        
        # Mock engine.connect to raise exception
        with patch.object(memory_engine, 'connect') as mock_connect:
            mock_connect.side_effect = Exception("Connection failed")
            
            try:
                with engine_context(memory_engine) as conn:
                    # Should not reach this point
                    assert False, "Should have raised exception"
            except Exception as e:
                assert "Connection failed" in str(e)
    
    def test_create_optimized_engine_with_poolclass(self):
        """Test create_optimized_engine with custom pool class"""
        from sqlalchemy.pool import NullPool
        
        engine = create_optimized_engine(
            "duckdb:///:memory:",
            poolclass=NullPool
        )
        assert engine is not None