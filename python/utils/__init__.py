"""
Shared library modules for RabbitMQ worker applications.
"""
from .logger import setup_logging, get_logger
from .rabbitmq import connect_rabbitmq, setup_queue, setup_consumer_qos, close_connection
from .types import (
    EmbeddingInputMessage, ProcessedEmbedding
)

__all__ = [
    'setup_logging', 'get_logger', 
    'connect_rabbitmq', 'setup_queue', 'setup_consumer_qos', 'close_connection',
    'EmbeddingInputMessage', 'ProcessedEmbedding'
]
