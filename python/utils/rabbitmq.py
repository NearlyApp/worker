#!/usr/bin/env python3
"""
Shared RabbitMQ connection and setup utilities for worker applications.
"""
import pika
import time
import os
import sys
from typing import Tuple, Optional
import logging


def connect_rabbitmq(logger: logging.Logger, 
                    max_retries: int = 30, 
                    retry_delay: int = 2,
                    rabbitmq_url: Optional[str] = None) -> Tuple[pika.BlockingConnection, pika.channel.Channel]:
    """
    Connect to RabbitMQ with retry logic.
    
    Args:
        logger: Logger instance for logging connection attempts
        max_retries: Maximum number of connection attempts (default: 30)
        retry_delay: Delay between retry attempts in seconds (default: 2)
        rabbitmq_url: RabbitMQ connection URL (default: from RABBITMQ_URL env var)
    
    Returns:
        Tuple of (connection, channel)
    
    Raises:
        SystemExit: If max retries are reached without successful connection
    """
    if rabbitmq_url is None:
        rabbitmq_url = os.getenv('RABBITMQ_URL', 'amqp://admin:admin@localhost:5672/')
    
    logger.info(f"🔗 Connecting to RabbitMQ at {rabbitmq_url}")
    
    for attempt in range(max_retries):
        try:
            logger.info(f"🔄 Connection attempt {attempt + 1}/{max_retries}")
            connection = pika.BlockingConnection(pika.URLParameters(rabbitmq_url))
            channel = connection.channel()
            logger.info("✅ Successfully connected to RabbitMQ")
            return connection, channel
        except Exception as e:
            logger.error(f"❌ Connection failed: {e}")
            if attempt < max_retries - 1:
                logger.info(f"⏳ Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.critical("❌ Max retries reached. Exiting.")
                sys.exit(1)


def setup_queue(channel: pika.channel.Channel, 
               logger: logging.Logger, 
               queue_name: str = 'embedding_input',
               durable: bool = True) -> str:
    """
    Declare a queue with specified options.
    
    Args:
        channel: RabbitMQ channel
        logger: Logger instance for logging setup
        queue_name: Name of the queue to declare (default: 'task_queue')
        durable: Whether the queue should be durable (default: True)
    
    Returns:
        The queue name that was declared
    """
    logger.info(f"📋 Setting up queue: {queue_name}")
    channel.queue_declare(queue=queue_name, durable=durable)
    logger.info(f"✅ Queue '{queue_name}' is ready (durable={durable})")
    return queue_name


def setup_consumer_qos(channel: pika.channel.Channel, 
                      logger: logging.Logger,
                      prefetch_count: int = 1) -> None:
    """
    Set Quality of Service (QoS) for fair message dispatch.
    
    Args:
        channel: RabbitMQ channel
        logger: Logger instance for logging QoS setup
        prefetch_count: Number of messages to prefetch (default: 1 for fair dispatch)
    """
    channel.basic_qos(prefetch_count=prefetch_count)
    logger.info(f"⚙️  QoS set to prefetch_count={prefetch_count} (fair dispatch)")


def close_connection(connection: pika.BlockingConnection, 
                    logger: logging.Logger,
                    start_time: Optional[object] = None) -> None:
    """
    Gracefully close RabbitMQ connection.
    
    Args:
        connection: RabbitMQ connection to close
        logger: Logger instance for logging closure
        start_time: Optional start time to calculate uptime
    """
    if connection and not connection.is_closed:
        connection.close()
        
        if start_time:
            from datetime import datetime, timezone
            uptime = datetime.now(timezone.utc) - start_time
            logger.info(f"🔌 Connection closed gracefully | Uptime: {uptime}")
        else:
            logger.info("🔌 Connection closed gracefully")
