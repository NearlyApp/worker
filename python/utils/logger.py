#!/usr/bin/env python3
"""
Shared logging configuration for RabbitMQ worker applications.
"""
import os
import logging
from typing import Optional


def setup_logging(logger_name: Optional[str] = None) -> logging.Logger:
    """
    Setup structured logging with timestamps and environment-based log levels.
    
    Args:
        logger_name: Name for the logger. If None, uses the calling module's name.
    
    Returns:
        Configured logger instance
    """
    # Get log level from environment variable, default to INFO
    log_level_str = os.getenv('LOG_LEVEL', 'INFO').upper()
    
    # Map string to logging level
    log_levels = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    
    log_level = log_levels.get(log_level_str, logging.INFO)
    
    # Configure basic logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s | %(levelname)8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Create and configure logger
    if logger_name is None:
        # Get the calling module's name
        import inspect
        frame = inspect.currentframe().f_back
        logger_name = frame.f_globals.get('__name__', 'worker')
        if logger_name == '__main__':
            # Extract filename without extension
            filename = frame.f_globals.get('__file__', 'worker')
            logger_name = os.path.splitext(os.path.basename(filename))[0]
    
    logger = logging.getLogger(logger_name)
    logger.info(f"🔧 Log level set to: {log_level_str}")
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.
    
    Args:
        name: Logger name
    
    Returns:
        Logger instance
    """
    return logging.getLogger(name)
