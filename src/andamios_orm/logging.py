"""
Logging configuration for Andamios ORM
"""

import logging
import sys
from typing import Optional


def setup_logging(level: str = "INFO", format_string: Optional[str] = None) -> None:
    """
    Set up logging for Andamios ORM.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_string: Custom format string for log messages
    """
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=format_string,
        handlers=[logging.StreamHandler(sys.stdout)]
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for the given name.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return logging.getLogger(f"andamios_orm.{name}")


# Default logger for the package
logger = get_logger("core")