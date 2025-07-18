#!/usr/bin/env python3
import pika
import json
import time
import os
from datetime import datetime, timezone
from typing import Dict, Any
from utils.logger import setup_logging
from utils.rabbitmq import connect_rabbitmq, setup_queue, close_connection

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
        close_connection(connection, logger)

if __name__ == '__main__':
    main()
