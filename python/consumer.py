#!/usr/bin/env python3
import pika
import json
import time
import os
import sys
import logging
from datetime import datetime, timezone
from typing import Dict, Any

def setup_logging():
    """Setup structured logging with timestamps"""
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
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s | %(levelname)8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    logger = logging.getLogger('consumer')
    logger.info(f"🔧 Log level set to: {log_level_str}")
    return logger

def connect_rabbitmq(logger):
    """Connect to RabbitMQ with retry logic"""
    rabbitmq_url = os.getenv('RABBITMQ_URL', 'amqp://admin:admin@localhost:5672/')
    
    max_retries = 30
    retry_delay = 2
    
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

def setup_queue(channel, logger, queue_name='task_queue'):
    """Declare a durable queue"""
    logger.info(f"📋 Setting up queue: {queue_name}")
    channel.queue_declare(queue=queue_name, durable=True)
    logger.info(f"✅ Queue '{queue_name}' is ready")
    return queue_name

def process_message(body: bytes, logger) -> bool:
    """Process the received message"""
    try:
        message = json.loads(body.decode('utf-8'))
        logger.info(f"📥 Processing message | ID: {message.get('id', 'N/A')} | Type: {message.get('type', 'unknown')}")
        logger.debug(f"📥 Message content: {message}")
        
        # Calculate message age if timestamp is available
        if 'timestamp' in message:
            try:
                msg_time = datetime.fromisoformat(message['timestamp'].replace('Z', '+00:00'))
                current_time = datetime.now(timezone.utc)
                age = current_time - msg_time
                logger.info(f"⏱️  Message age: {age.total_seconds():.2f} seconds")
            except Exception as e:
                logger.debug(f"Could not calculate message age: {e}")
        
        # Simulate some work
        processing_time = 2
        logger.info(f"⏳ Processing for {processing_time} seconds...")
        time.sleep(processing_time)
        
        logger.info(f"✅ Message {message.get('id', 'unknown')} processed successfully!")
        return True
        
    except json.JSONDecodeError as e:
        logger.error(f"❌ Failed to decode JSON: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Error processing message: {e}")
        return False

def callback(ch, method, properties, body):
    """Callback function for processing messages"""
    logger = logging.getLogger('consumer')
    receive_time = datetime.now(timezone.utc)
    logger.info(f"📨 Received message at {receive_time.isoformat()}")
    
    # Process the message
    start_processing = time.time()
    success = process_message(body, logger)
    processing_duration = time.time() - start_processing
    
    if success:
        # Acknowledge the message
        ch.basic_ack(delivery_tag=method.delivery_tag)
        logger.info(f"✅ Message acknowledged | Processing time: {processing_duration:.2f}s")
    else:
        # Reject the message and requeue it
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        logger.warning(f"❌ Message rejected and requeued | Processing time: {processing_duration:.2f}s")

def main():
    logger = setup_logging()
    logger.info("🎯 Starting Consumer...")
    logger.info(f"🌍 Environment: RABBITMQ_URL={os.getenv('RABBITMQ_URL', 'default')}")
    logger.info(f"🏠 Hostname: {os.getenv('HOSTNAME', 'unknown')}")
    
    # Connect to RabbitMQ
    connection, channel = connect_rabbitmq(logger)
    
    # Setup queue
    queue_name = setup_queue(channel, logger)
    
    # Set QoS to process one message at a time
    channel.basic_qos(prefetch_count=1)
    logger.info("⚙️  QoS set to prefetch_count=1 (fair dispatch)")
    
    # Setup consumer
    channel.basic_consume(queue=queue_name, on_message_callback=callback)
    
    logger.info("🔄 Waiting for messages. To exit press CTRL+C")
    start_time = datetime.now(timezone.utc)
    logger.info(f"🕐 Consumer started at {start_time.isoformat()}")
    
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        logger.info("\n🛑 Consumer stopped by user")
        channel.stop_consuming()
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        raise
    finally:
        if connection and not connection.is_closed:
            connection.close()
            uptime = datetime.now(timezone.utc) - start_time
            logger.info(f"🔌 Connection closed gracefully | Uptime: {uptime}")

if __name__ == '__main__':
    main()
