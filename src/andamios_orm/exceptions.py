"""
Custom exceptions for Andamios ORM

This module provides a comprehensive exception hierarchy for handling
different types of errors that can occur during ORM operations.
"""

from typing import Optional, Dict, Any
import traceback


class AndamiosORMException(Exception):
    """
    Base exception for all Andamios ORM errors.
    
    All exceptions in the Andamios ORM inherit from this base class,
    providing consistent error handling and additional metadata support.
    """
    
    def __init__(
        self, 
        message: str, 
        *args: Any,
        cause: Optional[Exception] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, *args)
        self.message = message
        self.cause = cause
        self.context = context or {}
        
        # Capture stack trace for debugging
        self.stack_trace = traceback.format_stack()
    
    def add_context(self, key: str, value: Any) -> "AndamiosORMException":
        """Add contextual information to the exception."""
        self.context[key] = value
        return self
    
    def get_detailed_message(self) -> str:
        """Get a detailed error message including context and cause."""
        parts = [f"AndamiosORMException: {self.message}"]
        
        if self.context:
            parts.append(f"Context: {self.context}")
        
        if self.cause:
            parts.append(f"Caused by: {type(self.cause).__name__}: {self.cause}")
        
        return "\n".join(parts)


class ValidationError(AndamiosORMException):
    """
    Raised when model validation fails.
    
    This exception is raised when data validation fails during
    model creation, updates, or custom validation checks.
    """
    
    def __init__(
        self, 
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        **kwargs: Any
    ):
        super().__init__(message, **kwargs)
        self.field = field
        self.value = value
        
        if field:
            self.add_context("field", field)
        if value is not None:
            self.add_context("value", value)


class NotFoundError(AndamiosORMException):
    """
    Raised when a requested record is not found.
    
    This exception is raised when attempting to retrieve, update,
    or delete records that don't exist in the database.
    """
    
    def __init__(
        self, 
        message: str,
        model_class: Optional[str] = None,
        identifier: Optional[Any] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[Any] = None,
        **kwargs: Any
    ):
        super().__init__(message, **kwargs)
        self.model_class = model_class or resource_type
        self.identifier = identifier or resource_id
        # Support both naming conventions
        self.resource_type = resource_type or model_class
        self.resource_id = resource_id or identifier
        
        if self.model_class:
            self.add_context("model_class", self.model_class)
        if self.identifier is not None:
            self.add_context("identifier", self.identifier)
    
    def __str__(self) -> str:
        """Return string representation including resource details."""
        result = super().__str__()
        if self.resource_type and self.resource_id is not None:
            result += f" (resource: {self.resource_type}#{self.resource_id})"
        elif self.resource_type:
            result += f" (resource: {self.resource_type})"
        elif self.resource_id is not None:
            result += f" (id: {self.resource_id})"
        return result


class DatabaseConnectionError(AndamiosORMException):
    """
    Raised when database connection fails.
    
    This exception is raised when the ORM cannot establish or maintain
    a connection to the database.
    """
    
    def __init__(
        self, 
        message: str,
        connection_string: Optional[str] = None,
        retry_count: int = 0,
        **kwargs: Any
    ):
        super().__init__(message, **kwargs)
        self.connection_string = connection_string
        self.retry_count = retry_count
        
        if connection_string:
            # Sanitize connection string (remove passwords)
            safe_conn = self._sanitize_connection_string(connection_string)
            self.add_context("connection_string", safe_conn)
        if retry_count > 0:
            self.add_context("retry_count", retry_count)
    
    def __str__(self) -> str:
        """Return string representation including connection string."""
        result = super().__str__()
        if self.connection_string:
            safe_conn = self._sanitize_connection_string(self.connection_string)
            result += f" (connection: {safe_conn})"
        return result
    
    @staticmethod
    def _sanitize_connection_string(conn_str: str) -> str:
        """Remove sensitive information from connection string."""
        import re
        # Handle URL format (e.g. postgresql://user:password@host)
        sanitized = re.sub(r'://([^:]+):([^@]+)@', r'://\1:***@', conn_str)
        # Handle key=value format (e.g. password=value)
        sanitized = re.sub(r'(password|pwd)=[^;]+', r'\1=***', sanitized, flags=re.IGNORECASE)
        return sanitized


class DatabaseOperationError(AndamiosORMException):
    """
    Raised when a database operation fails.
    
    This exception is raised when SQL operations fail, including
    CREATE, READ, UPDATE, DELETE, and schema operations.
    """
    
    def __init__(
        self, 
        message: str,
        operation: Optional[str] = None,
        table: Optional[str] = None,
        sql_state: Optional[str] = None,
        **kwargs: Any
    ):
        super().__init__(message, **kwargs)
        self.operation = operation
        self.table = table
        self.sql_state = sql_state
        
        if operation:
            self.add_context("operation", operation)
        if table:
            self.add_context("table", table)
        if sql_state:
            self.add_context("sql_state", sql_state)


class ConfigurationError(AndamiosORMException):
    """
    Raised when configuration is invalid.
    
    This exception is raised when the ORM encounters invalid
    configuration parameters or missing required settings.
    """
    
    def __init__(
        self, 
        message: str,
        config_key: Optional[str] = None,
        config_value: Optional[Any] = None,
        **kwargs: Any
    ):
        super().__init__(message, **kwargs)
        self.config_key = config_key
        self.config_value = config_value
        
        if config_key:
            self.add_context("config_key", config_key)
        if config_value is not None:
            self.add_context("config_value", config_value)


class TransactionError(AndamiosORMException):
    """
    Raised when transaction operations fail.
    
    This exception is raised when transaction commit, rollback,
    or savepoint operations fail.
    """
    
    def __init__(
        self, 
        message: str,
        transaction_state: Optional[str] = None,
        **kwargs: Any
    ):
        super().__init__(message, **kwargs)
        self.transaction_state = transaction_state
        
        if transaction_state:
            self.add_context("transaction_state", transaction_state)


class MigrationError(AndamiosORMException):
    """
    Raised when database migration operations fail.
    
    This exception is raised when schema migrations, table creation,
    or database initialization operations fail.
    """
    
    def __init__(
        self, 
        message: str,
        migration_name: Optional[str] = None,
        migration_version: Optional[str] = None,
        **kwargs: Any
    ):
        super().__init__(message, **kwargs)
        self.migration_name = migration_name
        self.migration_version = migration_version
        
        if migration_name:
            self.add_context("migration_name", migration_name)
        if migration_version:
            self.add_context("migration_version", migration_version)


class QueryError(AndamiosORMException):
    """
    Raised when query construction or execution fails.
    
    This exception is raised when there are issues with query
    building, parameter binding, or result processing.
    """
    
    def __init__(
        self, 
        message: str,
        query: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ):
        super().__init__(message, **kwargs)
        self.query = query
        self.parameters = parameters
        
        if query:
            self.add_context("query", query)
        if parameters:
            self.add_context("parameters", parameters)
    
    def __str__(self) -> str:
        """Return string representation including query details."""
        result = super().__str__()
        if self.query:
            result += f" (query: {self.query})"
        return result


# Convenience functions for exception handling
def handle_database_error(
    operation: str,
    table: str = None,
    cause: Exception = None
) -> DatabaseOperationError:
    """
    Create a standardized DatabaseOperationError.
    
    Args:
        operation: The operation that failed
        table: The table involved (if applicable)
        cause: The underlying exception that caused the error
    
    Returns:
        Configured DatabaseOperationError instance
    """
    message = f"Database operation '{operation}' failed"
    if table:
        message += f" on table '{table}'"
    
    return DatabaseOperationError(
        message=message,
        operation=operation,
        table=table,
        cause=cause
    )


def handle_validation_error(
    field: str,
    value: Any,
    reason: str
) -> ValidationError:
    """
    Create a standardized ValidationError.
    
    Args:
        field: The field that failed validation
        value: The invalid value
        reason: The reason for validation failure
    
    Returns:
        Configured ValidationError instance
    """
    message = f"Validation failed for field '{field}': {reason}"
    
    return ValidationError(
        message=message,
        field=field,
        value=value
    )


def handle_not_found_error(
    model_class: str,
    identifier: Any
) -> NotFoundError:
    """
    Create a standardized NotFoundError.
    
    Args:
        model_class: The model class name
        identifier: The identifier that was not found
    
    Returns:
        Configured NotFoundError instance
    """
    message = f"{model_class} with identifier '{identifier}' not found"
    
    return NotFoundError(
        message=message,
        model_class=model_class,
        identifier=identifier
    )


def sanitize_connection_string(conn_str: str) -> str:
    """
    Remove sensitive information from connection string.
    
    Args:
        conn_str: The connection string to sanitize
    
    Returns:
        Sanitized connection string with passwords masked
    """
    if not conn_str:
        return conn_str
    
    import re
    
    # Handle URL format (e.g. postgresql://user:password@host)
    sanitized = re.sub(r'://([^:]+):([^@]+)@', r'://\1:***@', conn_str)
    
    # Handle key=value format (e.g. password=value)
    sanitized = re.sub(r'(password|pwd)=[^;&]+', r'\1=***', sanitized, flags=re.IGNORECASE)
    
    return sanitized