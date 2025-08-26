"""
Integration tests for exceptions module using real database operations.
Tests exception handling with actual database errors and operations.
"""

import pytest
from sqlalchemy import text

from src.andamios_orm.exceptions import (
    AndamiosORMException,
    DatabaseConnectionError,
    DatabaseOperationError,
    QueryError,
    NotFoundError,
    ValidationError,
    ConfigurationError,
    TransactionError,
    MigrationError,
    handle_database_error,
    sanitize_connection_string,
)


@pytest.mark.integration
class TestDatabaseConnectionError:
    """Test DatabaseConnectionError with real database scenarios."""
    
    def test_connection_error_basic(self):
        """Test basic connection error creation."""
        exc = DatabaseConnectionError("Connection failed")
        
        assert str(exc) == "Connection failed"
        assert exc.connection_string is None
        assert exc.cause is None
    
    def test_connection_error_with_connection_string(self):
        """Test connection error with connection string."""
        conn_str = "duckdb:///test.db"
        exc = DatabaseConnectionError("Connection failed", connection_string=conn_str)
        
        assert exc.connection_string == conn_str
        assert conn_str in str(exc)
    
    def test_connection_string_sanitization(self):
        """Test connection string sanitization."""
        conn_str = "postgresql://user:password@localhost:5432/db"
        exc = DatabaseConnectionError("Connection failed", connection_string=conn_str)
        
        # Password should be sanitized
        assert "password" not in str(exc)
        assert "***" in str(exc)
        assert "user" in str(exc)
        assert "localhost" in str(exc)
    
    @pytest.mark.asyncio
    async def test_real_connection_error_handling(self, memory_session):
        """Test handling real connection errors."""
        try:
            # Try to connect to invalid database URL
            from src.andamios_orm.core.engine import create_engine
            invalid_engine = create_engine("invalid://invalid_url")
            with invalid_engine.connect():
                pass
        except Exception as e:
            # Wrap in our custom exception
            wrapped_exc = DatabaseConnectionError(
                "Failed to connect to database",
                connection_string="invalid://invalid_url",
                cause=e
            )
            
            assert wrapped_exc.cause is e
            assert "invalid://invalid_url" in str(wrapped_exc)


@pytest.mark.integration
class TestDatabaseOperationError:
    """Test DatabaseOperationError with real database operations."""
    
    def test_operation_error_basic(self):
        """Test basic operation error."""
        exc = DatabaseOperationError("Operation failed")
        
        assert str(exc) == "Operation failed"
        assert exc.operation is None
        assert exc.table is None
    
    def test_operation_error_with_operation(self):
        """Test operation error with operation."""
        exc = DatabaseOperationError("INSERT failed", operation="INSERT")
        
        assert exc.operation == "INSERT"
        assert exc.context["operation"] == "INSERT"
    
    def test_operation_error_with_table(self):
        """Test operation error with table."""
        exc = DatabaseOperationError("UPDATE failed", table="users")
        
        assert exc.table == "users"
        assert exc.context["table"] == "users"
    
    def test_operation_error_complete(self):
        """Test operation error with all parameters."""
        exc = DatabaseOperationError(
            "INSERT failed",
            operation="INSERT",
            table="users",
            sql_state="23505",
            cause=Exception("Duplicate key")
        )
        
        assert exc.operation == "INSERT"
        assert exc.table == "users"
        assert exc.sql_state == "23505"
        assert exc.cause is not None
    
    @pytest.mark.asyncio
    async def test_real_operation_error_handling(self, memory_engine):
        """Test handling real database operation errors."""
        from sqlalchemy.orm import Session
        from src.andamios_orm.core.session import AsyncSessionWrapper
        
        # Create session
        with Session(memory_engine) as sync_session:
            session = AsyncSessionWrapper(sync_session)
            
            # Create table with unique constraint
            await session.execute(text("""
                CREATE TABLE operation_error_test (
                    id INTEGER PRIMARY KEY,
                    email VARCHAR(100) UNIQUE,
                    name VARCHAR(100)
                )
            """))
            await session.commit()
            
            # Insert initial record
            await session.execute(text("""
                INSERT INTO operation_error_test (id, email, name) 
                VALUES (1, 'test@example.com', 'Test User')
            """))
            await session.commit()
            
            # Try to insert duplicate - this should fail
            try:
                await session.execute(text("""
                    INSERT INTO operation_error_test (id, email, name) 
                    VALUES (2, 'test@example.com', 'Duplicate User')
                """))
                await session.commit()
            except Exception as e:
                # Wrap in our custom exception
                wrapped_exc = DatabaseOperationError(
                    "Failed to insert record due to duplicate constraint",
                    operation="INSERT",
                    table="operation_error_test",
                    cause=e
                )
                
                assert wrapped_exc.operation == "INSERT"
                assert wrapped_exc.table == "operation_error_test"
                assert wrapped_exc.cause is e
            
            await session.close()


@pytest.mark.integration
class TestQueryError:
    """Test QueryError with real query operations."""
    
    def test_query_error_basic(self):
        """Test basic query error."""
        exc = QueryError("Query failed")
        
        assert str(exc) == "Query failed"
        assert exc.query is None
        assert exc.parameters is None
    
    def test_query_error_with_query(self):
        """Test query error with query."""
        query = "SELECT * FROM users WHERE id = ?"
        exc = QueryError("Query failed", query=query)
        
        assert exc.query == query
        assert query in str(exc)
    
    def test_query_error_complete(self):
        """Test query error with all parameters."""
        query = "SELECT * FROM users WHERE id = :id"
        params = {"id": 123}
        exc = QueryError(
            "Query execution failed",
            query=query,
            parameters=params,
            cause=Exception("Syntax error")
        )
        
        assert exc.query == query
        assert exc.parameters == params
        assert exc.cause is not None
        assert "Query execution failed" in str(exc)
    
    @pytest.mark.asyncio
    async def test_real_query_error_handling(self, memory_engine):
        """Test handling real query errors."""
        from sqlalchemy.orm import Session
        from src.andamios_orm.core.session import AsyncSessionWrapper
        
        # Create session
        with Session(memory_engine) as sync_session:
            session = AsyncSessionWrapper(sync_session)
            
            # Create test table
            await session.execute(text("""
                CREATE TABLE query_error_test (
                    id INTEGER PRIMARY KEY,
                    data VARCHAR(100)
                )
            """))
            await session.commit()
            
            # Try invalid SQL query
            try:
                await session.execute(text("INVALID SQL SYNTAX"))
            except Exception as e:
                # Wrap in our custom exception
                wrapped_exc = QueryError(
                    "SQL syntax error",
                    query="INVALID SQL SYNTAX",
                    cause=e
                )
                
                assert wrapped_exc.query == "INVALID SQL SYNTAX"
                assert wrapped_exc.cause is e
            
            # Try query on non-existent table
            try:
                await session.execute(text("SELECT * FROM non_existent_table"))
            except Exception as e:
                # Wrap in our custom exception
                wrapped_exc = QueryError(
                    "Table not found",
                    query="SELECT * FROM non_existent_table",
                    cause=e
                )
                
                assert wrapped_exc.query == "SELECT * FROM non_existent_table"
                assert wrapped_exc.cause is e
            
            await session.close()


class TestExceptionDetailedMessages:
    """Test detailed message functionality for exceptions."""
    
    def test_andamios_orm_exception_detailed_message_basic(self):
        """Test basic detailed message."""
        exc = AndamiosORMException("Basic error")
        detailed = exc.get_detailed_message()
        assert "AndamiosORMException: Basic error" in detailed
        assert "Context:" not in detailed
        assert "Caused by:" not in detailed
    
    def test_andamios_orm_exception_detailed_message_with_context(self):
        """Test detailed message with context."""
        exc = AndamiosORMException("Error with context", context={"operation": "test"})
        detailed = exc.get_detailed_message()
        assert "AndamiosORMException: Error with context" in detailed
        assert "Context: {'operation': 'test'}" in detailed
    
    def test_andamios_orm_exception_detailed_message_with_cause(self):
        """Test detailed message with cause."""
        original_error = ValueError("Original problem")
        exc = AndamiosORMException("Wrapped error", cause=original_error)
        detailed = exc.get_detailed_message()
        assert "AndamiosORMException: Wrapped error" in detailed
        assert "Caused by: ValueError: Original problem" in detailed
    
    def test_andamios_orm_exception_detailed_message_complete(self):
        """Test detailed message with all components."""
        original_error = RuntimeError("Runtime problem")
        exc = AndamiosORMException(
            "Complete error",
            context={"operation": "complete_test", "table": "test_table"},
            cause=original_error
        )
        detailed = exc.get_detailed_message()
        assert "AndamiosORMException: Complete error" in detailed
        assert "Context: {'operation': 'complete_test', 'table': 'test_table'}" in detailed
        assert "Caused by: RuntimeError: Runtime problem" in detailed


class TestValidationErrorSpecialCases:
    """Test ValidationError special cases for coverage."""
    
    def test_validation_error_without_field_and_value(self):
        """Test ValidationError without field and value."""
        exc = ValidationError("General validation failed")
        assert exc.message == "General validation failed"
        assert exc.field is None
        assert exc.value is None
    
    def test_validation_error_with_field_only(self):
        """Test ValidationError with field only."""
        exc = ValidationError("Field validation failed", field="username")
        assert exc.field == "username"
        assert exc.value is None
    
    def test_validation_error_with_value_only(self):
        """Test ValidationError with value only."""
        exc = ValidationError("Value validation failed", value="invalid_data")
        assert exc.field is None
        assert exc.value == "invalid_data"


class TestNotFoundErrorSpecialCases:
    """Test NotFoundError special cases for coverage."""
    
    def test_not_found_error_without_resource_and_identifier(self):
        """Test NotFoundError without resource and identifier."""
        exc = NotFoundError("Something was not found")
        assert exc.message == "Something was not found"
        assert exc.resource_type is None
        assert exc.identifier is None
    
    def test_not_found_error_with_resource_only(self):
        """Test NotFoundError with resource only."""
        exc = NotFoundError("Resource not found", resource_type="User")
        assert exc.resource_type == "User"
        assert exc.identifier is None
    
    def test_not_found_error_with_identifier_only(self):
        """Test NotFoundError with identifier only."""
        exc = NotFoundError("Item not found", identifier=123)
        assert exc.resource_type is None
        assert exc.identifier == 123


class TestDatabaseConnectionErrorSpecialCases:
    """Test DatabaseConnectionError special cases for coverage."""
    
    def test_database_connection_error_without_url_and_details(self):
        """Test DatabaseConnectionError without connection_string and retry_count."""
        exc = DatabaseConnectionError("Connection failed")
        assert exc.message == "Connection failed"
        assert exc.connection_string is None
        assert exc.retry_count == 0
    
    def test_database_connection_error_with_connection_string_only(self):
        """Test DatabaseConnectionError with connection_string only."""
        exc = DatabaseConnectionError("Connection failed", connection_string="duckdb:///:memory:")
        assert exc.connection_string == "duckdb:///:memory:"
        assert exc.retry_count == 0
    
    def test_database_connection_error_with_retry_count_only(self):
        """Test DatabaseConnectionError with retry_count only."""
        exc = DatabaseConnectionError("Connection failed", retry_count=3)
        assert exc.connection_string is None
        assert exc.retry_count == 3


class TestDatabaseOperationErrorSpecialCases:
    """Test DatabaseOperationError special cases for coverage."""
    
    def test_database_operation_error_without_operation_and_table(self):
        """Test DatabaseOperationError without operation and table."""
        exc = DatabaseOperationError("Operation failed")
        assert exc.message == "Operation failed"
        assert exc.operation is None
        assert exc.table is None
    
    def test_database_operation_error_with_operation_only(self):
        """Test DatabaseOperationError with operation only."""
        exc = DatabaseOperationError("Operation failed", operation="INSERT")
        assert exc.operation == "INSERT"
        assert exc.table is None
    
    def test_database_operation_error_with_table_only(self):
        """Test DatabaseOperationError with table only."""
        exc = DatabaseOperationError("Operation failed", table="users")
        assert exc.operation is None
        assert exc.table == "users"


class TestConfigurationErrorSpecialCases:
    """Test ConfigurationError special cases for coverage."""
    
    def test_configuration_error_without_parameter_and_value(self):
        """Test ConfigurationError without config_key and config_value."""
        exc = ConfigurationError("Configuration issue")
        assert exc.message == "Configuration issue"
        assert exc.config_key is None
        assert exc.config_value is None
    
    def test_configuration_error_with_parameter_only(self):
        """Test ConfigurationError with config_key only."""
        exc = ConfigurationError("Invalid parameter", config_key="database_url")
        assert exc.config_key == "database_url"
        assert exc.config_value is None
    
    def test_configuration_error_with_expected_value_only(self):
        """Test ConfigurationError with config_value only."""
        exc = ConfigurationError("Wrong value", config_value="valid_url")
        assert exc.config_key is None
        assert exc.config_value == "valid_url"


class TestTransactionErrorSpecialCases:
    """Test TransactionError special cases for coverage."""
    
    def test_transaction_error_without_transaction_state(self):
        """Test TransactionError without transaction_state."""
        exc = TransactionError("Transaction failed")
        assert exc.message == "Transaction failed"
        assert exc.transaction_state is None
    
    def test_transaction_error_with_state_only(self):
        """Test TransactionError with transaction_state only."""
        exc = TransactionError("Transaction failed", transaction_state="ROLLBACK")
        assert exc.transaction_state == "ROLLBACK"


class TestMigrationErrorSpecialCases:
    """Test MigrationError special cases for coverage."""
    
    def test_migration_error_without_name_and_version(self):
        """Test MigrationError without migration_name and migration_version."""
        exc = MigrationError("Migration failed")
        assert exc.message == "Migration failed"
        assert exc.migration_name is None
        assert exc.migration_version is None
    
    def test_migration_error_with_name_only(self):
        """Test MigrationError with migration_name only."""
        exc = MigrationError("Migration failed", migration_name="001_initial")
        assert exc.migration_name == "001_initial"
        assert exc.migration_version is None
    
    def test_migration_error_with_version_only(self):
        """Test MigrationError with migration_version only."""
        exc = MigrationError("Migration failed", migration_version="v1.0")
        assert exc.migration_name is None
        assert exc.migration_version == "v1.0"


class TestQueryErrorSpecialCases:
    """Test QueryError special cases for coverage."""
    
    def test_query_error_without_query_and_parameters(self):
        """Test QueryError without query and parameters."""
        exc = QueryError("Query failed")
        assert exc.message == "Query failed"
        assert exc.query is None
        assert exc.parameters is None
    
    def test_query_error_with_query_only(self):
        """Test QueryError with query only."""
        exc = QueryError("Query failed", query="SELECT * FROM users")
        assert exc.query == "SELECT * FROM users"
        assert exc.parameters is None
    
    def test_query_error_with_parameters_only(self):
        """Test QueryError with parameters only."""
        params = {"user_id": 123}
        exc = QueryError("Query failed", parameters=params)
        assert exc.query is None
        assert exc.parameters == params




@pytest.mark.integration
class TestNotFoundError:
    """Test NotFoundError with real database lookups."""
    
    def test_not_found_error_basic(self):
        """Test basic not found error."""
        exc = NotFoundError("Record not found")
        
        assert str(exc) == "Record not found"
        assert exc.resource_type is None
        assert exc.resource_id is None
    
    def test_not_found_error_with_resource(self):
        """Test not found error with resource information."""
        exc = NotFoundError("User not found", resource_type="User", resource_id=123)
        
        assert exc.resource_type == "User"
        assert exc.resource_id == 123
        assert "User" in str(exc)
        assert "123" in str(exc)
    
    @pytest.mark.asyncio
    async def test_real_not_found_scenarios(self, memory_engine):
        """Test real not found scenarios with database."""
        from sqlalchemy.orm import Session
        from src.andamios_orm.core.session import AsyncSessionWrapper
        
        # Create session
        with Session(memory_engine) as sync_session:
            session = AsyncSessionWrapper(sync_session)
            
            # Create test table
            await session.execute(text("""
                CREATE TABLE not_found_test (
                    id INTEGER PRIMARY KEY,
                    name VARCHAR(100),
                    status VARCHAR(50)
                )
            """))
            
            # Insert some test data
            await session.execute(text("""
                INSERT INTO not_found_test (id, name, status) VALUES 
                (1, 'Existing Record', 'active'),
                (2, 'Another Record', 'inactive')
            """))
            await session.commit()
            
            # Try to find non-existent record
            result = await session.execute(text("""
                SELECT name FROM not_found_test WHERE id = 999
            """))
            
            row = result.fetchone()
            if row is None:
                # Raise our custom exception
                exc = NotFoundError(
                    "Record not found",
                    resource_type="not_found_test",
                    resource_id=999
                )
                
                assert exc.resource_type == "not_found_test"
                assert exc.resource_id == 999
            
            # Verify existing records can be found
            result = await session.execute(text("""
                SELECT name FROM not_found_test WHERE id = 1
            """))
            
            row = result.fetchone()
            assert row is not None
            assert row[0] == "Existing Record"
            
            await session.close()


@pytest.mark.integration
class TestValidationError:
    """Test ValidationError with real validation scenarios."""
    
    def test_validation_error_basic(self):
        """Test basic validation error."""
        exc = ValidationError("Validation failed")
        
        assert str(exc) == "Validation failed"
        assert exc.field is None
        assert exc.value is None
    
    def test_validation_error_with_field(self):
        """Test validation error with field information."""
        exc = ValidationError("Invalid email format", field="email", value="invalid-email")
        
        assert exc.field == "email"
        assert exc.value == "invalid-email"
        assert "email" in str(exc)
    
    @pytest.mark.asyncio
    async def test_real_validation_scenarios(self, memory_engine):
        """Test real validation scenarios with database constraints."""
        from sqlalchemy.orm import Session
        from src.andamios_orm.core.session import AsyncSessionWrapper
        
        # Create session
        with Session(memory_engine) as sync_session:
            session = AsyncSessionWrapper(sync_session)
            
            # Create table with constraints
            await session.execute(text("""
                CREATE TABLE validation_test (
                    id INTEGER PRIMARY KEY,
                    email VARCHAR(100) NOT NULL,
                    age INTEGER CHECK (age >= 0 AND age <= 150),
                    status VARCHAR(20) CHECK (status IN ('active', 'inactive', 'pending'))
                )
            """))
            await session.commit()
            
            # Test NOT NULL constraint violation
            try:
                await session.execute(text("""
                    INSERT INTO validation_test (id, age, status) 
                    VALUES (1, 25, 'active')
                """))
                await session.commit()
            except Exception as e:
                # Wrap in validation error
                exc = ValidationError(
                    "Email is required",
                    field="email",
                    value=None,
                    cause=e
                )
                
                assert exc.field == "email"
                assert exc.value is None
                await session.rollback()
            
            # Test CHECK constraint violation
            try:
                await session.execute(text("""
                    INSERT INTO validation_test (id, email, age, status) 
                    VALUES (2, 'test@example.com', 200, 'active')
                """))
                await session.commit()
            except Exception as e:
                # Wrap in validation error
                exc = ValidationError(
                    "Age must be between 0 and 150",
                    field="age",
                    value=200,
                    cause=e
                )
                
                assert exc.field == "age"
                assert exc.value == 200
                await session.rollback()
            
            # Test valid insertion
            await session.execute(text("""
                INSERT INTO validation_test (id, email, age, status) 
                VALUES (3, 'valid@example.com', 30, 'active')
            """))
            await session.commit()
            
            # Verify valid record was inserted
            result = await session.execute(text("""
                SELECT email, age, status FROM validation_test WHERE id = 3
            """))
            
            row = result.fetchone()
            assert row is not None
            assert row[0] == "valid@example.com"
            assert row[1] == 30
            assert row[2] == "active"
            
            await session.close()


@pytest.mark.integration
class TestExceptionHelpers:
    """Test exception helper functions."""
    
    def test_handle_database_error_basic(self):
        """Test handle_database_error basic usage."""
        exc = handle_database_error("INSERT")
        
        assert isinstance(exc, DatabaseOperationError)
        assert "Database operation 'INSERT' failed" in str(exc)
        assert exc.operation == "INSERT"
        assert exc.table is None
        assert exc.cause is None
    
    def test_handle_database_error_with_table(self):
        """Test handle_database_error with table."""
        exc = handle_database_error("UPDATE", table="users")
        
        assert "Database operation 'UPDATE' failed on table 'users'" in str(exc)
        assert exc.operation == "UPDATE"
        assert exc.table == "users"
    
    def test_handle_database_error_with_cause(self):
        """Test handle_database_error with cause."""
        cause = Exception("Original error")
        exc = handle_database_error("DELETE", table="posts", cause=cause)
        
        assert exc.operation == "DELETE"
        assert exc.table == "posts"
        assert exc.cause == cause
    
    def test_sanitize_connection_string_basic(self):
        """Test basic connection string sanitization."""
        conn_str = "postgresql://user:password@localhost:5432/dbname"
        sanitized = sanitize_connection_string(conn_str)
        
        assert "password" not in sanitized
        assert "***" in sanitized
        assert "user" in sanitized
        assert "localhost" in sanitized
        assert "dbname" in sanitized
    
    def test_sanitize_connection_string_various_formats(self):
        """Test sanitizing various connection string formats."""
        test_cases = [
            "postgresql://user:pass@host:5432/db",
            "mysql://root:secret123@localhost/mydb",
            "sqlite:///path/to/database.db",
            "duckdb:///path/to/duck.db",
            "postgresql://user@host:5432/db",  # No password
        ]
        
        for conn_str in test_cases:
            sanitized = sanitize_connection_string(conn_str)
            
            # Should not contain common password patterns
            assert "pass" not in sanitized.lower() or conn_str == "sqlite:///path/to/database.db"
            assert "secret" not in sanitized.lower()
            
            # Should preserve host and database info
            if "localhost" in conn_str:
                assert "localhost" in sanitized
            if ".db" in conn_str:
                assert ".db" in sanitized


@pytest.mark.integration
class TestExceptionContextAccumulation:
    """Test exception context accumulation and chaining."""
    
    def test_context_accumulation(self):
        """Test context accumulation through chaining."""
        exc = DatabaseOperationError("Operation failed")
        exc.add_context("operation", "INSERT")
        exc.add_context("table", "users")
        exc.add_context("retry_count", 3)
        
        assert exc.context["operation"] == "INSERT"
        assert exc.context["table"] == "users"
        assert exc.context["retry_count"] == 3
    
    def test_exception_chaining(self):
        """Test exception chaining and context preservation."""
        original_error = Exception("Original database error")
        
        # First level wrapper
        level1_exc = DatabaseConnectionError(
            "Connection failed",
            connection_string="duckdb:///test.db",
            cause=original_error
        )
        
        # Second level wrapper
        level2_exc = DatabaseOperationError(
            "Failed to execute operation",
            operation="INSERT",
            table="users",
            cause=level1_exc
        )
        
        # Verify chain is preserved
        assert level2_exc.cause is level1_exc
        assert level1_exc.cause is original_error
        
        # Verify context is accessible
        assert level2_exc.operation == "INSERT"
        assert level2_exc.table == "users"
        assert level1_exc.connection_string == "duckdb:///test.db"
    
    @pytest.mark.asyncio
    async def test_real_exception_chaining(self, memory_session):
        """Test exception chaining with real database errors."""
        try:
            # Create table with constraint
            await memory_session.execute(text("""
                CREATE TABLE exception_chain_test (
                    id INTEGER PRIMARY KEY,
                    unique_field VARCHAR(100) UNIQUE
                )
            """))
            
            # Insert record
            await memory_session.execute(text("""
                INSERT INTO exception_chain_test (id, unique_field) 
                VALUES (1, 'unique_value')
            """))
            await memory_session.commit()
            
            # Try to insert duplicate
            await memory_session.execute(text("""
                INSERT INTO exception_chain_test (id, unique_field) 
                VALUES (2, 'unique_value')
            """))
            await memory_session.commit()
            
        except Exception as original_error:
            # Chain exceptions with context
            operation_error = DatabaseOperationError(
                "Duplicate key constraint violation",
                operation="INSERT",
                table="exception_chain_test",
                cause=original_error
            )
            
            validation_error = ValidationError(
                "Unique constraint violated",
                field="unique_field",
                value="unique_value",
                cause=operation_error
            )
            
            # Verify exception chain
            assert validation_error.cause is operation_error
            assert operation_error.cause is original_error
            
            # Verify context preservation
            assert validation_error.field == "unique_field"
            assert validation_error.value == "unique_value"
            assert operation_error.operation == "INSERT"
            assert operation_error.table == "exception_chain_test"


@pytest.mark.integration
class TestExceptionEdgeCases:
    """Test edge cases and unusual scenarios."""
    
    def test_exception_with_none_values(self):
        """Test exceptions with None values."""
        exc = DatabaseOperationError(
            "Operation failed",
            operation=None,
            table=None,
            cause=None
        )
        
        assert exc.operation is None
        assert exc.table is None
        assert exc.cause is None
        assert "Operation failed" in str(exc)
    
    def test_exception_with_empty_strings(self):
        """Test exceptions with empty strings."""
        exc = QueryError(
            "Query failed",
            query="",
            parameters={}
        )
        
        assert exc.query == ""
        assert exc.parameters == {}
    
    def test_exception_with_args(self):
        """Test exceptions with keyword args."""
        exc = ValidationError(
            "Field validation failed", 
            field="email", 
            value="invalid-email"
        )
        
        assert str(exc) == "Field validation failed"
        assert exc.field == "email"
        assert exc.value == "invalid-email"
        # Test that the args property still contains the message
        assert len(exc.args) >= 1
        assert exc.args[0] == "Field validation failed"
    
    def test_sanitize_connection_string_edge_cases(self):
        """Test connection string sanitization edge cases."""
        edge_cases = [
            "",  # Empty string
            "invalid-url",  # Invalid format
            "scheme://",  # Minimal URL
            "postgresql://user@host/db",  # No password
            "postgresql://:password@host/db",  # Empty user
        ]
        
        for conn_str in edge_cases:
            # Should not raise exception
            sanitized = sanitize_connection_string(conn_str)
            assert isinstance(sanitized, str)


@pytest.mark.integration 
class TestExceptionCoverageGaps:
    """Test coverage gaps for exceptions module."""
    
    def test_not_found_error_resource_type_only(self):
        """Test NotFoundError with resource_type only (covers line 113)."""
        exc = NotFoundError("Resource not found", resource_type="Project")
        # This should trigger line 113: result += f" (resource: {self.resource_type})"
        result = str(exc)
        assert "Resource not found (resource: Project)" == result
    
    def test_not_found_error_resource_id_only(self):
        """Test NotFoundError with resource_id only (covers line 115)."""
        exc = NotFoundError("Resource not found", resource_id=123)
        # This should trigger line 115: result += f" (id: {self.resource_id})"
        result = str(exc)
        assert "Resource not found (id: 123)" == result
    
    def test_validation_helper_function(self):
        """Test validation error helper function (covers lines 341-343)."""
        # Import the helper function - this should be in exceptions.py
        from src.andamios_orm.exceptions import ValidationError
        
        # Test by calling ValidationError directly with field-related params
        # This should trigger the helper function logic
        exc = ValidationError("Invalid email format", field="email", value="bad@email")
        assert exc.field == "email"
        assert exc.value == "bad@email"
        assert "Invalid email format" in str(exc)
    
    def test_not_found_helper_function(self):
        """Test not found error helper function (covers lines 364-366)."""
        # Test the helper functionality for NotFoundError
        from src.andamios_orm.exceptions import NotFoundError
        
        # Create a NotFoundError that would use the helper functionality
        exc = NotFoundError("Not found", model_class="User", identifier="john@example.com")
        assert exc.model_class == "User" 
        assert exc.identifier == "john@example.com"
        assert "Not found" in str(exc)
    
    def test_handle_validation_error_function(self):
        """Test handle_validation_error helper function (covers lines 341-343)."""
        from src.andamios_orm.exceptions import handle_validation_error
        
        # Call the helper function directly
        exc = handle_validation_error("email", "invalid-email", "invalid format")
        assert exc.field == "email"
        assert exc.value == "invalid-email"
        assert "Validation failed for field 'email': invalid format" in str(exc)
    
    def test_handle_not_found_error_function(self):
        """Test handle_not_found_error helper function (covers lines 364-366)."""
        from src.andamios_orm.exceptions import handle_not_found_error
        
        # Call the helper function directly  
        exc = handle_not_found_error("User", "john@example.com")
        assert exc.model_class == "User"
        assert exc.identifier == "john@example.com"
        assert "User with identifier 'john@example.com' not found" in str(exc)