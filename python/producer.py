#!/usr/bin/env python3
import pika
import json
import time
import os
import sys
from datetime import datetime, timezone
from typing import Dict, Any
from lib.logger import setup_logging

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

def send_message(channel, logger, queue_name: str, message: Dict[Any, Any]):
    """Send a message to the queue"""
    try:
        message_json = json.dumps(message)
        channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=message_json,
            properties=pika.BasicProperties(
                delivery_mode=2,  # Make message persistent
            )
        )
        logger.info(f"📤 Message sent | ID: {message.get('id', 'N/A')} | Size: {len(message_json)} bytes")
        logger.debug(f"📤 Message content: {message}")
    except Exception as e:
        logger.error(f"❌ Failed to send message: {e}")
        raise

def main():
    logger = setup_logging('producer')
    logger.info("🚀 Starting Producer...")
    logger.info(f"🌍 Environment: RABBITMQ_URL={os.getenv('RABBITMQ_URL', 'default')}")
    
    # Connect to RabbitMQ
    connection, channel = connect_rabbitmq(logger)
    
    # Setup queue
    queue_name = setup_queue(channel, logger)
    
    try:
        # Send messages periodically
        message_count = 1
        start_time = datetime.now(timezone.utc)
        logger.info(f"🔄 Starting message production at {start_time.isoformat()}")
        
        while True:
            current_time = datetime.now(timezone.utc)
            message = {
                'id': message_count,
                'content': f'Hello from Producer! Message #{message_count}',
                'timestamp': current_time.isoformat(),
                'type': 'greeting',
                'producer_uptime': str(current_time - start_time),
                'hostname': os.getenv('HOSTNAME', 'unknown')
            }
            
            send_message(channel, logger, queue_name, message)
            message_count += 1
            
            if message_count % 10 == 0:
                logger.info(f"📊 Milestone: {message_count} messages sent")
            
            # Wait before sending next message
            time.sleep(5)
            
    except KeyboardInterrupt:
        logger.info("\n🛑 Producer stopped by user")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        raise
    finally:
        if connection and not connection.is_closed:
            connection.close()
            logger.info("🔌 Connection closed gracefully")

if __name__ == '__main__':
    main()
