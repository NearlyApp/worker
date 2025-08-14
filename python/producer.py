#!/usr/bin/env python3
import pika
import json
import time
import os
import logging
from datetime import datetime, timezone
from utils.logger import setup_logging
from utils.rabbitmq import connect_rabbitmq, setup_queue, close_connection
from utils.types import EmbeddingInputMessage

def send_message(channel: pika.channel.Channel, logger: logging.Logger, queue_name: str, message: EmbeddingInputMessage) -> None:
    """Send an embedding input message to the queue."""
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
    logger.info("🚀 Starting Embedding Input Producer...")
    logger.info(f"🌍 Environment: RABBITMQ_URL={os.getenv('RABBITMQ_URL', 'default')}")
    
    # Connect to RabbitMQ
    connection, channel = connect_rabbitmq(logger)
    
    # Setup queue
    queue_name = setup_queue(channel, logger, queue_name='embedding_input')
    
    try:
        # Send messages periodically
        message_count = 1
        start_time = datetime.now(timezone.utc)
        logger.info(f"🔄 Starting embedding message production at {start_time.isoformat()}")
        
        while True:
            current_time = datetime.now(timezone.utc)
            message: EmbeddingInputMessage = {
                'id': message_count,
                'text': f'Sample text to embed #{message_count}',
                'timestamp': int(current_time.timestamp()),
                'source': 'demo-producer',
                'trace_id': f'trace-{message_count}',
                'metadata': {
                    'lang': 'en',
                    'producer_uptime_seconds': int((current_time - start_time).total_seconds()),
                }
            }

            send_message(channel, logger, queue_name, message)
            message_count += 1

            if message_count % 10 == 0:
                logger.info(f"📊 Milestone: {message_count} embedding messages sent")

            # Wait before sending next message (shorter for embedding throughput demo)
            time.sleep(2)
            
    except KeyboardInterrupt:
        logger.info("\n🛑 Embedding Producer stopped by user")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        raise
    finally:
        close_connection(connection, logger)

if __name__ == '__main__':
    main()
