#!/usr/bin/env python3
import json
import time
import os
import logging
from datetime import datetime, timezone
from utils.logger import setup_logging, get_logger
from utils.rabbitmq import connect_rabbitmq, setup_queue, setup_consumer_qos, close_connection
from utils.types import WorkerMessage, MessageTypes

def process_message(body: bytes, logger: logging.Logger) -> bool:
    """Process the received message"""
    try:
        # Parse message data
        message_data = json.loads(body.decode('utf-8'))
        
        # Validate required fields for WorkerMessage
        required_fields = ['id', 'content', 'timestamp', 'type']
        for field in required_fields:
            if field not in message_data:
                logger.error(f"❌ Missing required field: {field}")
                return False
        
        # Create typed message
        message: WorkerMessage = {
            'id': message_data['id'],
            'content': message_data['content'],
            'timestamp': message_data['timestamp'],
            'type': message_data['type'],
            'producer_uptime': message_data.get('producer_uptime'),
            'hostname': message_data.get('hostname')
        }
        
        logger.info(f"📥 Processing message | ID: {message['id']} | Type: {message['type']}")
        logger.debug(f"📥 Message content: {message}")
        
        # Calculate message age if timestamp is available
        if message['timestamp']:
            try:
                msg_time = datetime.fromisoformat(message['timestamp'].replace('Z', '+00:00'))
                current_time = datetime.now(timezone.utc)
                age = current_time - msg_time
                logger.info(f"⏱️  Message age: {age.total_seconds():.2f} seconds")
            except Exception as e:
                logger.debug(f"Could not calculate message age: {e}")
        
        # Process based on message type
        if message['type'] == MessageTypes.GREETING:
            logger.info(f"👋 Processing greeting: {message['content']}")
        elif message['type'] == MessageTypes.TASK:
            logger.info(f"⚙️  Processing task: {message['content']}")
        else:
            logger.info(f"🔧 Processing {message['type']} message: {message['content']}")
        
        # Simulate some work
        processing_time = 2
        logger.info(f"⏳ Processing for {processing_time} seconds...")
        time.sleep(processing_time)
        
        logger.info(f"✅ Message {message['id']} processed successfully!")
        return True
        
    except json.JSONDecodeError as e:
        logger.error(f"❌ Failed to decode JSON: {e}")
        return False
    except KeyError as e:
        logger.error(f"❌ Missing required field in message: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Error processing message: {e}")
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
    logger.info("🎯 Starting Consumer...")
    logger.info(f"🌍 Environment: RABBITMQ_URL={os.getenv('RABBITMQ_URL', 'default')}")
    logger.info(f"🏠 Hostname: {os.getenv('HOSTNAME', 'unknown')}")
    
    # Connect to RabbitMQ
    connection, channel = connect_rabbitmq(logger)
    
    # Setup queue
    queue_name = setup_queue(channel, logger)
    
    # Set QoS to process one message at a time
    setup_consumer_qos(channel, logger, prefetch_count=1)
    
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
        close_connection(connection, logger, start_time)

if __name__ == '__main__':
    main()
