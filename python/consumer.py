#!/usr/bin/env python3
import json
import time
import os
import logging
from datetime import datetime, timezone
from utils.logger import setup_logging, get_logger
from utils.rabbitmq import connect_rabbitmq, setup_queue, setup_consumer_qos, close_connection
from utils.types import EmbeddingInputMessage

def process_message(body: bytes, logger: logging.Logger) -> bool:
    """Process an embedding input message from the queue."""
    try:
        data = json.loads(body.decode('utf-8'))
        for field in ['id', 'text', 'timestamp']:
            if field not in data:
                logger.error(f"❌ Missing required field: {field}")
                return False

        message: EmbeddingInputMessage = data  # type: ignore

        logger.info(f"📥 Received embedding request | id={message['id']} text_len={len(message['text'])}")
        logger.debug(f"📥 Full message: {message}")

        # Age calculation (timestamp expected as epoch seconds)
        try:
            age = time.time() - float(message['timestamp'])
            if age >= 0:
                logger.info(f"⏱️  Age {age:.3f}s")
        except Exception:
            logger.debug("Could not parse timestamp for age computation")

        # Simulate embedding generation latency based on length
        latency = min(0.25 + len(message['text']) / 400.0, 1.5)
        logger.info(f"🧮 Generating embedding (simulated {latency:.2f}s)...")
        time.sleep(latency)
        logger.info("✅ Embedding generated (mock)")
        return True
    except json.JSONDecodeError as e:
        logger.error(f"❌ JSON decode error: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return False

def callback(ch, method, properties, body: bytes) -> None:
    """Callback function for processing messages"""
    logger = get_logger('consumer')
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
    logger = setup_logging('consumer')
    logger.info("🎯 Starting Embedding Consumer...")
    logger.info(f"🌍 Environment: RABBITMQ_URL={os.getenv('RABBITMQ_URL', 'default')}")
    logger.info(f"🏠 Hostname: {os.getenv('HOSTNAME', 'unknown')}")
    
    # Connect to RabbitMQ
    connection, channel = connect_rabbitmq(logger)
    
    # Setup queue
    queue_name = setup_queue(channel, logger, queue_name='embedding_input')
    
    # Set QoS to process one message at a time
    setup_consumer_qos(channel, logger, prefetch_count=1)
    
    # Setup consumer
    channel.basic_consume(queue=queue_name, on_message_callback=callback)
    
    logger.info("🔄 Waiting for embedding input messages. To exit press CTRL+C")
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
        close_connection(connection, logger, start_time)

if __name__ == '__main__':
    main()
