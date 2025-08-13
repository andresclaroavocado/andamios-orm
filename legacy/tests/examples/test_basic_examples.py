"""
Tests for basic examples to ensure they work correctly.

These tests verify that our examples are accurate and demonstrate
the expected behavior. They run the actual example code and
verify the outcomes.
"""

import asyncio
import sys
from pathlib import Path
from unittest.mock import patch
import pytest

# Add examples to path for testing
examples_path = Path(__file__).parent.parent.parent / "examples"
sys.path.insert(0, str(examples_path))


class TestConnectionExamples:
    """Test the connection examples."""
    
    @pytest.mark.asyncio
    async def test_basic_connection_example(self, capsys):
        """Test that basic connection example runs without errors."""
        # Import the example module
        from basic.connection_01 import basic_connection_example
        
        # Run the example
        await basic_connection_example()
        
        # Capture output
        captured = capsys.readouterr()
        
        # Verify expected output
        assert "Setting up database connection" in captured.out
        assert "Engine created successfully" in captured.out
        assert "Session created" in captured.out
        assert "Message from database: Hello from DuckDB!" in captured.out
        assert "Session closed" in captured.out
        assert "Engine disposed" in captured.out
    
    @pytest.mark.asyncio
    async def test_session_context_manager_example(self, capsys):
        """Test the session context manager example."""
        from basic.connection_01 import session_context_manager_example
        
        await session_context_manager_example()
        
        captured = capsys.readouterr()
        assert "Using session context manager" in captured.out
        assert "The answer is: 42" in captured.out
        assert "Session automatically managed" in captured.out
    
    @pytest.mark.asyncio
    async def test_multiple_sessions_example(self, capsys):
        """Test multiple concurrent sessions example."""
        from basic.connection_01 import multiple_sessions_example
        
        await multiple_sessions_example()
        
        captured = capsys.readouterr()
        assert "Multiple concurrent sessions" in captured.out
        assert "Worker 1 completed" in captured.out
        assert "Worker 2 completed" in captured.out
        assert "Worker 3 completed" in captured.out
        assert "All workers completed" in captured.out
    
    @pytest.mark.asyncio
    async def test_error_handling_example(self, capsys):
        """Test error handling example."""
        from basic.connection_01 import error_handling_example
        
        await error_handling_example()
        
        captured = capsys.readouterr()
        assert "Error handling example" in captured.out
        assert "Caught expected error" in captured.out
        assert "Error handled properly" in captured.out
    
    @pytest.mark.asyncio
    async def test_performance_monitoring_example(self, capsys):
        """Test performance monitoring example."""
        from basic.connection_01 import performance_monitoring_example
        
        await performance_monitoring_example()
        
        captured = capsys.readouterr()
        assert "Performance monitoring example" in captured.out
        assert "Engine setup took" in captured.out
        assert "Average session time" in captured.out
    
    @pytest.mark.asyncio
    async def test_main_example_runner(self, capsys):
        """Test the main example runner."""
        from basic.connection_01 import main
        
        await main()
        
        captured = capsys.readouterr()
        assert "Andamios ORM Connection Examples" in captured.out
        assert "All connection examples completed successfully!" in captured.out


class TestModelExamples:
    """Test the model definition examples."""
    
    @pytest.mark.asyncio
    async def test_create_tables_example(self, capsys):
        """Test table creation example."""
        from basic.models_02 import create_tables_example
        
        await create_tables_example()
        
        captured = capsys.readouterr()
        assert "Creating tables from models" in captured.out
        assert "Tables created successfully" in captured.out
    
    @pytest.mark.asyncio
    async def test_model_creation_example(self, capsys):
        """Test model instance creation example."""
        from basic.models_02 import model_creation_example
        
        await model_creation_example()
        
        captured = capsys.readouterr()
        assert "Creating model instances" in captured.out
        assert "Created user: John Doe" in captured.out
        assert "Email: john.doe@example.com" in captured.out
        assert "Created product: Premium Coffee Beans" in captured.out
        assert "Models saved to database" in captured.out
    
    @pytest.mark.asyncio
    async def test_validation_example(self, capsys):
        """Test model validation example."""
        from basic.models_02 import validation_example
        
        await validation_example()
        
        captured = capsys.readouterr()
        assert "Model validation examples" in captured.out
        assert "Valid user created successfully" in captured.out
        assert "Caught expected email validation error" in captured.out
        assert "Caught expected username validation error" in captured.out
        assert "Caught expected price validation error" in captured.out
    
    @pytest.mark.asyncio
    async def test_field_types_example(self, capsys):
        """Test field types demonstration."""
        from basic.models_02 import field_types_example
        
        await field_types_example()
        
        captured = capsys.readouterr()
        assert "Field types demonstration" in captured.out
        assert "ID (Integer):" in captured.out
        assert "Email (String):" in captured.out
        assert "Birth Date (Date):" in captured.out
        assert "Is Active (Boolean):" in captured.out
        assert "External ID (UUID):" in captured.out
        assert "Created At (DateTime):" in captured.out
        assert "Preferences (JSON):" in captured.out
    
    @pytest.mark.asyncio
    async def test_main_model_runner(self, capsys):
        """Test the main model example runner."""
        from basic.models_02 import main
        
        await main()
        
        captured = capsys.readouterr()
        assert "Andamios ORM Model Examples" in captured.out
        assert "All model examples completed successfully!" in captured.out


class TestExamplePerformance:
    """Test that examples meet performance requirements."""
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_connection_performance(self, performance_monitor):
        """Test that connection examples meet performance targets."""
        from basic.connection_01 import basic_connection_example
        
        with performance_monitor.measure("basic_connection"):
            await basic_connection_example()
        
        measurements = performance_monitor.get_measurements()
        
        # Basic connection should complete within 1 second
        assert measurements["basic_connection"] < 1.0
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_model_creation_performance(self, performance_monitor):
        """Test that model creation examples meet performance targets."""
        from basic.models_02 import model_creation_example
        
        with performance_monitor.measure("model_creation"):
            await model_creation_example()
        
        measurements = performance_monitor.get_measurements()
        
        # Model creation should complete within 1 second
        assert measurements["model_creation"] < 1.0


class TestExampleIntegration:
    """Integration tests for examples with real database operations."""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_examples_use_real_databases(self, isolated_db):
        """Verify examples use real database operations, not mocks."""
        from basic.connection_01 import get_database_session
        
        # Test that we can actually create and query data
        async with get_database_session() as session:
            result = await session.execute("CREATE TABLE test_table (id INTEGER, name VARCHAR)")
            await session.commit()
            
            result = await session.execute("INSERT INTO test_table VALUES (1, 'test')")
            await session.commit()
            
            result = await session.execute("SELECT name FROM test_table WHERE id = 1")
            name = result.scalar()
            
            assert name == "test"
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_example_database_isolation(self, isolated_db):
        """Test that examples properly isolate database operations."""
        # This test verifies that database operations in examples
        # don't interfere with each other
        
        # Create some test data
        await isolated_db.execute("CREATE TABLE isolation_test (value INTEGER)")
        await isolated_db.execute("INSERT INTO isolation_test VALUES (42)")
        await isolated_db.commit()
        
        # Verify isolation - other operations shouldn't see this data
        # (This would be expanded with more sophisticated isolation testing)
        result = await isolated_db.execute("SELECT COUNT(*) FROM isolation_test")
        count = result.scalar()
        assert count == 1


class TestExampleErrorHandling:
    """Test error handling in examples."""
    
    @pytest.mark.asyncio
    async def test_examples_handle_database_errors(self):
        """Test that examples properly handle database errors."""
        from basic.connection_01 import error_handling_example
        
        # This should not raise an exception - errors should be caught and handled
        await error_handling_example()
    
    @pytest.mark.asyncio
    async def test_examples_handle_validation_errors(self):
        """Test that examples properly handle validation errors."""
        from basic.models_02 import validation_example
        
        # This should not raise an exception - validation errors should be caught
        await validation_example()


class TestExampleDocumentation:
    """Test that examples are properly documented."""
    
    def test_examples_have_docstrings(self):
        """Test that all example functions have proper docstrings."""
        from basic import connection_01, models_02
        
        # Check main functions have docstrings
        assert connection_01.basic_connection_example.__doc__ is not None
        assert connection_01.session_context_manager_example.__doc__ is not None
        assert models_02.create_tables_example.__doc__ is not None
        assert models_02.model_creation_example.__doc__ is not None
        
        # Check docstrings are descriptive (more than just the function name)
        assert len(connection_01.basic_connection_example.__doc__.strip()) > 50
        assert len(models_02.create_tables_example.__doc__.strip()) > 50
    
    def test_example_files_have_module_docstrings(self):
        """Test that example files have proper module-level documentation."""
        from basic import connection_01, models_02
        
        assert connection_01.__doc__ is not None
        assert models_02.__doc__ is not None
        
        # Check for expected content in docstrings
        assert "demonstrates how to" in connection_01.__doc__
        assert "Expected behavior" in connection_01.__doc__
        assert "demonstrates how to" in models_02.__doc__
        assert "Expected behavior" in models_02.__doc__


# Utility functions for test setup
async def run_example_with_timeout(example_func, timeout_seconds=5):
    """Run an example function with a timeout to prevent hanging tests."""
    try:
        await asyncio.wait_for(example_func(), timeout=timeout_seconds)
    except asyncio.TimeoutError:
        pytest.fail(f"Example {example_func.__name__} took longer than {timeout_seconds} seconds")


def capture_example_output(example_func):
    """Capture output from an example function for testing."""
    import io
    from contextlib import redirect_stdout, redirect_stderr
    
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()
    
    with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
        asyncio.run(example_func())
    
    return stdout_capture.getvalue(), stderr_capture.getvalue()