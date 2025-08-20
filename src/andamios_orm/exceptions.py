"""
Custom exceptions for Andamios ORM
"""


class AndamiosORMException(Exception):
    """Base exception for Andamios ORM."""
    pass


class ValidationError(AndamiosORMException):
    """Raised when model validation fails."""
    pass


class NotFoundError(AndamiosORMException):
    """Raised when a record is not found."""
    pass


class DatabaseConnectionError(AndamiosORMException):
    """Raised when database connection fails."""
    pass


class DatabaseOperationError(AndamiosORMException):
    """Raised when a database operation fails."""
    pass


class ConfigurationError(AndamiosORMException):
    """Raised when configuration is invalid."""
    pass