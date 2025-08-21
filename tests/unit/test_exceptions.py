"""
Unit tests for exceptions module
"""

import pytest
import traceback
from unittest.mock import Mock, patch

from src.andamios_orm.exceptions import (
    AndamiosORMException,
    ValidationError,
    NotFoundError,
    DatabaseConnectionError,
    DatabaseOperationError,
    ConfigurationError,
    TransactionError,
    MigrationError,
    QueryError,
    handle_database_error,
    handle_validation_error,
    handle_not_found_error
)


class TestAndamiosORMException:
    """Test base AndamiosORMException class."""
    
    def test_basic_exception(self):
        """Test basic exception creation."""
        exc = AndamiosORMException("Test message")
        
        assert str(exc) == "Test message"
        assert exc.message == "Test message"
        assert exc.cause is None
        assert exc.context == {}
        assert exc.stack_trace is not None
        assert isinstance(exc.stack_trace, list)
    
    def test_exception_with_cause(self):
        """Test exception creation with cause."""
        cause = ValueError("Original error")
        exc = AndamiosORMException("Test message", cause=cause)
        
        assert exc.cause == cause
    
    def test_exception_with_context(self):
        """Test exception creation with context."""
        context = {"operation": "test", "table": "test_table"}
        exc = AndamiosORMException("Test message", context=context)
        
        assert exc.context == context
    
    def test_add_context(self):
        """Test adding context to exception."""
        exc = AndamiosORMException("Test message")
        result = exc.add_context("key", "value")
        
        assert exc.context["key"] == "value"
        assert result == exc  # Should return self for chaining
    
    def test_add_multiple_context(self):
        """Test adding multiple context items."""
        exc = AndamiosORMException("Test message")
        exc.add_context("key1", "value1")
        exc.add_context("key2", "value2")
        
        assert exc.context["key1"] == "value1"
        assert exc.context["key2"] == "value2"
    
    def test_get_detailed_message_basic(self):
        """Test detailed message without context or cause."""
        exc = AndamiosORMException("Test message")
        detailed = exc.get_detailed_message()
        
        assert "AndamiosORMException: Test message" in detailed
    
    def test_get_detailed_message_with_context(self):
        """Test detailed message with context."""
        exc = AndamiosORMException("Test message", context={"key": "value"})
        detailed = exc.get_detailed_message()
        
        assert "AndamiosORMException: Test message" in detailed
        assert "Context: {'key': 'value'}" in detailed
    
    def test_get_detailed_message_with_cause(self):
        """Test detailed message with cause."""
        cause = ValueError("Original error")
        exc = AndamiosORMException("Test message", cause=cause)
        detailed = exc.get_detailed_message()
        
        assert "AndamiosORMException: Test message" in detailed
        assert "Caused by: ValueError: Original error" in detailed
    
    def test_get_detailed_message_complete(self):
        """Test detailed message with both context and cause."""
        cause = ValueError("Original error")
        context = {"key": "value"}
        exc = AndamiosORMException("Test message", cause=cause, context=context)
        detailed = exc.get_detailed_message()
        
        assert "AndamiosORMException: Test message" in detailed
        assert "Context: {'key': 'value'}" in detailed
        assert "Caused by: ValueError: Original error" in detailed
    
    def test_stack_trace_capture(self):
        """Test that stack trace is properly captured."""
        exc = AndamiosORMException("Test message")
        
        assert isinstance(exc.stack_trace, list)
        assert len(exc.stack_trace) > 0
        # Should contain current test method in stack trace
        stack_str = ''.join(exc.stack_trace)
        assert "test_stack_trace_capture" in stack_str


class TestValidationError:
    """Test ValidationError class."""
    
    def test_basic_validation_error(self):
        """Test basic validation error creation."""
        exc = ValidationError("Validation failed")
        
        assert isinstance(exc, AndamiosORMException)
        assert str(exc) == "Validation failed"
        assert exc.field is None
        assert exc.value is None
    
    def test_validation_error_with_field(self):
        """Test validation error with field."""
        exc = ValidationError("Invalid email", field="email")
        
        assert exc.field == "email"
        assert exc.context["field"] == "email"
    
    def test_validation_error_with_value(self):
        """Test validation error with value."""
        exc = ValidationError("Invalid value", value="invalid@")
        
        assert exc.value == "invalid@"
        assert exc.context["value"] == "invalid@"
    
    def test_validation_error_complete(self):
        """Test validation error with all parameters."""
        exc = ValidationError(
            "Invalid email format",
            field="email",
            value="invalid@",
            cause=ValueError("Format error")
        )
        
        assert exc.field == "email"
        assert exc.value == "invalid@"
        assert exc.context["field"] == "email"
        assert exc.context["value"] == "invalid@"
        assert isinstance(exc.cause, ValueError)


class TestNotFoundError:
    """Test NotFoundError class."""
    
    def test_basic_not_found_error(self):
        """Test basic not found error creation."""
        exc = NotFoundError("Record not found")
        
        assert isinstance(exc, AndamiosORMException)
        assert str(exc) == "Record not found"
        assert exc.model_class is None
        assert exc.identifier is None
    
    def test_not_found_error_with_model_class(self):
        """Test not found error with model class."""
        exc = NotFoundError("User not found", model_class="User")
        
        assert exc.model_class == "User"
        assert exc.context["model_class"] == "User"
    
    def test_not_found_error_with_identifier(self):
        """Test not found error with identifier."""
        exc = NotFoundError("Record not found", identifier=123)
        
        assert exc.identifier == 123
        assert exc.context["identifier"] == 123
    
    def test_not_found_error_complete(self):
        """Test not found error with all parameters."""
        exc = NotFoundError(
            "User not found",
            model_class="User",
            identifier=123,
            cause=Exception("DB error")
        )
        
        assert exc.model_class == "User"
        assert exc.identifier == 123
        assert exc.context["model_class"] == "User"
        assert exc.context["identifier"] == 123


class TestDatabaseConnectionError:
    """Test DatabaseConnectionError class."""
    
    def test_basic_connection_error(self):
        """Test basic connection error creation."""
        exc = DatabaseConnectionError("Connection failed")
        
        assert isinstance(exc, AndamiosORMException)
        assert str(exc) == "Connection failed"
        assert exc.connection_string is None
        assert exc.retry_count == 0
    
    def test_connection_error_with_connection_string(self):
        """Test connection error with connection string."""
        conn_str = "postgresql://user:password@localhost/db"
        exc = DatabaseConnectionError("Connection failed", connection_string=conn_str)
        
        assert exc.connection_string == conn_str
        # Should sanitize password in context
        assert "password=***" in exc.context["connection_string"]
        assert "password" not in exc.context["connection_string"]
    
    def test_connection_error_with_retry_count(self):
        """Test connection error with retry count."""
        exc = DatabaseConnectionError("Connection failed", retry_count=3)
        
        assert exc.retry_count == 3
        assert exc.context["retry_count"] == 3
    
    def test_connection_string_sanitization(self):
        """Test connection string sanitization."""
        test_cases = [
            ("postgresql://user:secret@host/db", "postgresql://user:password=***@host/db"),
            ("mysql://user:pwd=secret@host/db", "mysql://user:pwd=***@host/db"),
            ("sqlite:///path/to/db.sqlite", "sqlite:///path/to/db.sqlite"),  # No password
        ]
        
        for original, expected in test_cases:
            sanitized = DatabaseConnectionError._sanitize_connection_string(original)
            if "password" in expected or "pwd" in expected:
                assert "password=***" in sanitized or "pwd=***" in sanitized
            else:
                assert sanitized == original


class TestDatabaseOperationError:
    """Test DatabaseOperationError class."""
    
    def test_basic_operation_error(self):
        """Test basic operation error creation."""
        exc = DatabaseOperationError("Operation failed")
        
        assert isinstance(exc, AndamiosORMException)
        assert str(exc) == "Operation failed"
        assert exc.operation is None
        assert exc.table is None
        assert exc.sql_state is None
    
    def test_operation_error_with_operation(self):
        """Test operation error with operation."""
        exc = DatabaseOperationError("INSERT failed", operation="INSERT")
        
        assert exc.operation == "INSERT"
        assert exc.context["operation"] == "INSERT"
    
    def test_operation_error_with_table(self):
        """Test operation error with table."""
        exc = DatabaseOperationError("Operation failed", table="users")
        
        assert exc.table == "users"
        assert exc.context["table"] == "users"
    
    def test_operation_error_with_sql_state(self):
        """Test operation error with SQL state."""
        exc = DatabaseOperationError("Operation failed", sql_state="23505")
        
        assert exc.sql_state == "23505"
        assert exc.context["sql_state"] == "23505"
    
    def test_operation_error_complete(self):
        """Test operation error with all parameters."""
        exc = DatabaseOperationError(
            "INSERT failed",
            operation="INSERT",
            table="users",
            sql_state="23505",
            cause=Exception("Constraint violation")
        )
        
        assert exc.operation == "INSERT"
        assert exc.table == "users"
        assert exc.sql_state == "23505"
        assert all(key in exc.context for key in ["operation", "table", "sql_state"])


class TestConfigurationError:
    """Test ConfigurationError class."""
    
    def test_basic_config_error(self):
        """Test basic configuration error creation."""
        exc = ConfigurationError("Invalid configuration")
        
        assert isinstance(exc, AndamiosORMException)
        assert str(exc) == "Invalid configuration"
        assert exc.config_key is None
        assert exc.config_value is None
    
    def test_config_error_with_key(self):
        """Test configuration error with key."""
        exc = ConfigurationError("Invalid setting", config_key="database_url")
        
        assert exc.config_key == "database_url"
        assert exc.context["config_key"] == "database_url"
    
    def test_config_error_with_value(self):
        """Test configuration error with value."""
        exc = ConfigurationError("Invalid value", config_value="invalid_url")
        
        assert exc.config_value == "invalid_url"
        assert exc.context["config_value"] == "invalid_url"
    
    def test_config_error_complete(self):
        """Test configuration error with all parameters."""
        exc = ConfigurationError(
            "Invalid database URL",
            config_key="database_url",
            config_value="invalid://url",
            cause=ValueError("Invalid URL format")
        )
        
        assert exc.config_key == "database_url"
        assert exc.config_value == "invalid://url"
        assert exc.context["config_key"] == "database_url"
        assert exc.context["config_value"] == "invalid://url"


class TestTransactionError:
    """Test TransactionError class."""
    
    def test_basic_transaction_error(self):
        """Test basic transaction error creation."""
        exc = TransactionError("Transaction failed")
        
        assert isinstance(exc, AndamiosORMException)
        assert str(exc) == "Transaction failed"
        assert exc.transaction_state is None
    
    def test_transaction_error_with_state(self):
        """Test transaction error with state."""
        exc = TransactionError("Commit failed", transaction_state="COMMITTING")
        
        assert exc.transaction_state == "COMMITTING"
        assert exc.context["transaction_state"] == "COMMITTING"


class TestMigrationError:
    """Test MigrationError class."""
    
    def test_basic_migration_error(self):
        """Test basic migration error creation."""
        exc = MigrationError("Migration failed")
        
        assert isinstance(exc, AndamiosORMException)
        assert str(exc) == "Migration failed"
        assert exc.migration_name is None
        assert exc.migration_version is None
    
    def test_migration_error_with_name(self):
        """Test migration error with name."""
        exc = MigrationError("Migration failed", migration_name="001_initial")
        
        assert exc.migration_name == "001_initial"
        assert exc.context["migration_name"] == "001_initial"
    
    def test_migration_error_with_version(self):
        """Test migration error with version."""
        exc = MigrationError("Migration failed", migration_version="1.0.0")
        
        assert exc.migration_version == "1.0.0"
        assert exc.context["migration_version"] == "1.0.0"


class TestQueryError:
    """Test QueryError class."""
    
    def test_basic_query_error(self):
        """Test basic query error creation."""
        exc = QueryError("Query failed")
        
        assert isinstance(exc, AndamiosORMException)
        assert str(exc) == "Query failed"
        assert exc.query is None
        assert exc.parameters is None
    
    def test_query_error_with_query(self):
        """Test query error with query."""
        query = "SELECT * FROM users WHERE id = ?"
        exc = QueryError("Query failed", query=query)
        
        assert exc.query == query
        assert exc.context["query"] == query
    
    def test_query_error_with_parameters(self):
        """Test query error with parameters."""
        params = {"id": 123, "name": "test"}
        exc = QueryError("Query failed", parameters=params)
        
        assert exc.parameters == params
        assert exc.context["parameters"] == params
    
    def test_query_error_complete(self):
        """Test query error with all parameters."""
        query = "SELECT * FROM users WHERE id = :id"
        params = {"id": 123}
        exc = QueryError(
            "Query execution failed",
            query=query,
            parameters=params,
            cause=Exception("Database error")
        )
        
        assert exc.query == query
        assert exc.parameters == params
        assert exc.context["query"] == query
        assert exc.context["parameters"] == params


class TestConvenienceFunctions:
    """Test convenience functions for exception creation."""
    
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
    
    def test_handle_validation_error(self):
        """Test handle_validation_error function."""
        exc = handle_validation_error("email", "invalid@", "Invalid format")
        
        assert isinstance(exc, ValidationError)
        assert "Validation failed for field 'email': Invalid format" in str(exc)
        assert exc.field == "email"
        assert exc.value == "invalid@"
    
    def test_handle_not_found_error(self):
        """Test handle_not_found_error function."""
        exc = handle_not_found_error("User", 123)
        
        assert isinstance(exc, NotFoundError)
        assert "User with identifier '123' not found" in str(exc)
        assert exc.model_class == "User"
        assert exc.identifier == 123


class TestExceptionInheritance:
    """Test exception inheritance hierarchy."""
    
    def test_all_exceptions_inherit_from_base(self):
        """Test that all custom exceptions inherit from AndamiosORMException."""
        exceptions = [
            ValidationError,
            NotFoundError,
            DatabaseConnectionError,
            DatabaseOperationError,
            ConfigurationError,
            TransactionError,
            MigrationError,
            QueryError
        ]
        
        for exc_class in exceptions:
            assert issubclass(exc_class, AndamiosORMException)
            assert issubclass(exc_class, Exception)
    
    def test_base_exception_inherits_from_exception(self):
        """Test that base exception inherits from Exception."""
        assert issubclass(AndamiosORMException, Exception)
    
    def test_exception_instantiation(self):
        """Test that all exceptions can be instantiated."""
        exceptions = [
            (AndamiosORMException, "Test message"),
            (ValidationError, "Validation failed"),
            (NotFoundError, "Not found"),
            (DatabaseConnectionError, "Connection failed"),
            (DatabaseOperationError, "Operation failed"),
            (ConfigurationError, "Config error"),
            (TransactionError, "Transaction failed"),
            (MigrationError, "Migration failed"),
            (QueryError, "Query failed")
        ]
        
        for exc_class, message in exceptions:
            exc = exc_class(message)
            assert isinstance(exc, exc_class)
            assert isinstance(exc, AndamiosORMException)
            assert str(exc) == message


class TestExceptionChaining:
    """Test exception chaining and context propagation."""
    
    def test_exception_chaining(self):
        """Test exception chaining with cause."""
        original = ValueError("Original error")
        chained = DatabaseOperationError("Operation failed", cause=original)
        
        assert chained.cause == original
        detailed = chained.get_detailed_message()
        assert "Caused by: ValueError: Original error" in detailed
    
    def test_context_accumulation(self):
        """Test context accumulation through chaining."""
        exc = DatabaseOperationError("Operation failed")
        exc.add_context("operation", "INSERT")
        exc.add_context("table", "users")
        exc.add_context("retry_count", 3)
        
        assert exc.context["operation"] == "INSERT"
        assert exc.context["table"] == "users"
        assert exc.context["retry_count"] == 3
        
        detailed = exc.get_detailed_message()
        assert "operation" in detailed
        assert "table" in detailed
        assert "retry_count" in detailed
    
    def test_method_chaining(self):
        """Test method chaining with add_context."""
        exc = (AndamiosORMException("Test")
               .add_context("key1", "value1")
               .add_context("key2", "value2")
               .add_context("key3", "value3"))
        
        assert exc.context["key1"] == "value1"
        assert exc.context["key2"] == "value2"
        assert exc.context["key3"] == "value3"


class TestExceptionEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_empty_message(self):
        """Test exception with empty message."""
        exc = AndamiosORMException("")
        assert str(exc) == ""
        assert exc.message == ""
    
    def test_none_context_values(self):
        """Test exception with None context values."""
        exc = AndamiosORMException("Test")
        exc.add_context("key", None)
        
        assert exc.context["key"] is None
        detailed = exc.get_detailed_message()
        assert "key" in detailed
    
    def test_complex_context_values(self):
        """Test exception with complex context values."""
        complex_value = {"nested": {"dict": [1, 2, 3]}}
        exc = AndamiosORMException("Test")
        exc.add_context("complex", complex_value)
        
        assert exc.context["complex"] == complex_value
    
    def test_exception_with_args(self):
        """Test exception with additional args."""
        exc = AndamiosORMException("Test message", "arg1", "arg2")
        assert str(exc) == "Test message"
        assert exc.message == "Test message"
    
    def test_sanitize_connection_string_edge_cases(self):
        """Test connection string sanitization edge cases."""
        test_cases = [
            ("", ""),  # Empty string
            ("no_password_here", "no_password_here"),  # No password
            ("password=", "password=***"),  # Empty password
            ("PASSWORD=secret", "PASSWORD=***"),  # Uppercase
            ("pwd=test;password=secret", "pwd=***"),  # Multiple patterns
        ]
        
        for original, expected_pattern in test_cases:
            result = DatabaseConnectionError._sanitize_connection_string(original)
            if "***" in expected_pattern:
                assert "***" in result
            else:
                assert result == expected_pattern