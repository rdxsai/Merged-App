"""
Logging configuration for the Question App.

This module centralizes logging configuration and setup for the application.
"""

import logging
from typing import Optional

from .config import config


def setup_logging(
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    Set up logging configuration for the application.
    
    Args:
        level: Logging level (default: INFO)
        log_file: Path to log file (default: from config)
        format_string: Log format string (default: standard format)
        
    Returns:
        Configured logger instance
    """
    if log_file is None:
        log_file = config.LOG_FILE
        
    if format_string is None:
        format_string = "%(asctime)s - %(levelname)s - %(message)s"
    
    # Configure logging
    logging.basicConfig(
        level=level,
        format=format_string,
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ],
    )
    
    # Get and return the logger
    logger = logging.getLogger(__name__)
    logger.info("Logging configured successfully")
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)
