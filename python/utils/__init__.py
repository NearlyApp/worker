"""
Shared library modules for RabbitMQ worker applications.
"""
from .logger import setup_logging, get_logger

__all__ = ['setup_logging', 'get_logger']
