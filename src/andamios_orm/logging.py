"""
Comprehensive logging configuration for Andamios ORM

This module provides structured logging with configurable levels,
formatters, handlers, and performance monitoring capabilities.
"""

import logging
import logging.handlers
import sys
import json
import time
import threading
from pathlib import Path
from typing import Optional, Dict, Any, List, Union
from functools import wraps
from contextlib import contextmanager
import asyncio
from datetime import datetime


class StructuredFormatter(logging.Formatter):
    """Custom formatter that outputs structured JSON logs."""
    
    def format(self, record: logging.LogRecord) -> str:
        # Create structured log entry
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception information if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields from the log record
        for key, value in record.__dict__.items():
            if key not in {
                "name", "msg", "args", "levelname", "levelno", "pathname",
                "filename", "module", "lineno", "funcName", "created",
                "msecs", "relativeCreated", "thread", "threadName",
                "processName", "process", "message", "exc_info", "exc_text",
                "stack_info", "getMessage"
            }:
                log_entry[key] = value
        
        return json.dumps(log_entry, ensure_ascii=False)


class PerformanceLoggerAdapter(logging.LoggerAdapter):
    """Logger adapter that adds performance monitoring capabilities."""
    
    def __init__(self, logger: logging.Logger, extra: Optional[Dict[str, Any]] = None):
        super().__init__(logger, extra or {})
        self._timers: Dict[str, float] = {}
    
    def process(self, msg: str, kwargs: Dict[str, Any]) -> tuple:
        """Process the logging call to add extra information."""
        return msg, kwargs
    
    @contextmanager
    def timer(self, operation: str):
        """Context manager for timing operations."""
        start_time = time.perf_counter()
        self.debug(f"Starting operation: {operation}")
        
        try:
            yield
        finally:
            elapsed = time.perf_counter() - start_time
            self.info(f"Operation completed: {operation}", extra={
                "operation": operation,
                "elapsed_time": elapsed,
                "performance": True
            })
    
    def start_timer(self, operation: str) -> None:
        """Start a named timer."""
        self._timers[operation] = time.perf_counter()
        self.debug(f"Timer started: {operation}")
    
    def end_timer(self, operation: str) -> float:
        """End a named timer and return elapsed time."""
        if operation not in self._timers:
            self.warning(f"Timer '{operation}' was not started")
            return 0.0
        
        elapsed = time.perf_counter() - self._timers.pop(operation)
        self.info(f"Timer ended: {operation}", extra={
            "operation": operation,
            "elapsed_time": elapsed,
            "performance": True
        })
        return elapsed


class AsyncLogHandler(logging.Handler):
    """Async-aware log handler that doesn't block the event loop."""
    
    def __init__(self, base_handler: logging.Handler):
        super().__init__()
        self.base_handler = base_handler
        self.setLevel(base_handler.level)
        self.setFormatter(base_handler.formatter)
    
    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record asynchronously if in async context."""
        try:
            # Check if we're in an async context
            loop = asyncio.get_running_loop()
            # Schedule the actual logging in a thread pool
            loop.run_in_executor(None, self._emit_sync, record)
        except RuntimeError:
            # Not in async context, emit synchronously
            self._emit_sync(record)
    
    def _emit_sync(self, record: logging.LogRecord) -> None:
        """Emit record synchronously."""
        try:
            self.base_handler.emit(record)
        except Exception:
            self.handleError(record)


def setup_logging(
    level: str = "INFO",
    format_type: str = "standard",  # "standard", "structured", "json"
    log_file: Optional[Union[str, Path]] = None,
    max_file_size: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    async_mode: bool = True,
    extra_loggers: Optional[List[str]] = None,
    **kwargs: Any
) -> None:
    """
    Set up comprehensive logging for Andamios ORM.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_type: Type of format ("standard", "structured", "json")
        log_file: Optional file path for file logging
        max_file_size: Maximum log file size before rotation
        backup_count: Number of backup files to keep
        async_mode: Whether to use async-compatible handlers
        extra_loggers: Additional logger names to configure
        **kwargs: Additional configuration options
    """
    # Clear any existing handlers
    root_logger = logging.getLogger("andamios_orm")
    root_logger.handlers.clear()
    
    # Set level
    log_level = getattr(logging, level.upper())
    root_logger.setLevel(log_level)
    
    # Choose formatter based on format_type
    if format_type == "json" or format_type == "structured":
        formatter = StructuredFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    
    if async_mode:
        console_handler = AsyncLogHandler(console_handler)
    
    root_logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_path,
            maxBytes=max_file_size,
            backupCount=backup_count
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        
        if async_mode:
            file_handler = AsyncLogHandler(file_handler)
        
        root_logger.addHandler(file_handler)
    
    # Configure additional loggers
    additional_loggers = extra_loggers or []
    for logger_name in additional_loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(log_level)
        # They will inherit handlers from root logger
    
    # Suppress noisy third-party loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    
    # Log the configuration
    logger = get_logger("logging")
    logger.info(f"Logging configured: level={level}, format={format_type}, async={async_mode}")


def get_logger(name: str, performance: bool = False) -> Union[logging.Logger, PerformanceLoggerAdapter]:
    """
    Get a logger instance for the given name.
    
    Args:
        name: Logger name (will be prefixed with 'andamios_orm.')
        performance: Whether to return a performance-aware logger adapter
        
    Returns:
        Logger instance or PerformanceLoggerAdapter
    """
    logger = logging.getLogger(f"andamios_orm.{name}")
    
    if performance:
        return PerformanceLoggerAdapter(logger)
    
    return logger


def log_async_performance(operation_name: str):
    """
    Decorator for logging async function performance.
    
    Args:
        operation_name: Name of the operation being logged
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            logger = get_logger("performance", performance=True)
            
            async with logger.timer(f"{operation_name}"):
                result = await func(*args, **kwargs)
            
            return result
        return wrapper
    return decorator


def log_sync_performance(operation_name: str):
    """
    Decorator for logging sync function performance.
    
    Args:
        operation_name: Name of the operation being logged
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger("performance", performance=True)
            
            with logger.timer(f"{operation_name}"):
                result = func(*args, **kwargs)
            
            return result
        return wrapper
    return decorator


@contextmanager
def log_context(logger: logging.Logger, operation: str, **context_data):
    """
    Context manager for adding contextual information to logs.
    
    Args:
        logger: Logger instance to use
        operation: Operation name for context
        **context_data: Additional context data to include
    """
    start_time = time.perf_counter()
    logger.info(f"Starting {operation}", extra=context_data)
    
    try:
        yield
        elapsed = time.perf_counter() - start_time
        logger.info(f"Completed {operation}", extra={
            **context_data,
            "elapsed_time": elapsed,
            "success": True
        })
    except Exception as e:
        elapsed = time.perf_counter() - start_time
        logger.error(f"Failed {operation}: {e}", extra={
            **context_data,
            "elapsed_time": elapsed,
            "success": False,
            "error": str(e)
        }, exc_info=True)
        raise


class LoggingConfig:
    """Configuration class for logging setup."""
    
    def __init__(
        self,
        level: str = "INFO",
        format_type: str = "standard",
        log_file: Optional[str] = None,
        async_mode: bool = True,
        performance_logging: bool = False
    ):
        self.level = level
        self.format_type = format_type
        self.log_file = log_file
        self.async_mode = async_mode
        self.performance_logging = performance_logging
    
    def apply(self) -> None:
        """Apply this logging configuration."""
        extra_loggers = []
        if self.performance_logging:
            extra_loggers.append("andamios_orm.performance")
        
        setup_logging(
            level=self.level,
            format_type=self.format_type,
            log_file=self.log_file,
            async_mode=self.async_mode,
            extra_loggers=extra_loggers
        )


# Default logger for the package
logger = get_logger("core")
performance_logger = get_logger("performance", performance=True)

# Pre-configured logging setups for common scenarios
DEVELOPMENT_CONFIG = LoggingConfig(
    level="DEBUG",
    format_type="standard",
    async_mode=True,
    performance_logging=True
)

PRODUCTION_CONFIG = LoggingConfig(
    level="INFO",
    format_type="json",
    log_file="/var/log/andamios-orm/app.log",
    async_mode=True,
    performance_logging=False
)

TESTING_CONFIG = LoggingConfig(
    level="WARNING",
    format_type="standard",
    async_mode=False,
    performance_logging=False
)