#!/usr/bin/env python3
"""
Type definitions for RabbitMQ worker applications.
"""
from typing import TypedDict, Optional, Any
from datetime import datetime


class WorkerMessage(TypedDict):
    """
    Standard message format for worker communication.
    
    All messages sent between producers and consumers should follow this structure.
    """
    id: int
    content: str
    timestamp: str  # ISO format string
    type: str
    producer_uptime: Optional[str]
    hostname: Optional[str]


class GreetingMessage(WorkerMessage):
    """
    Specific message type for greeting messages.
    Extends the base WorkerMessage with greeting-specific fields.
    """
    type: str  # Should always be 'greeting'


class TaskMessage(WorkerMessage):
    """
    Specific message type for task messages.
    Extends the base WorkerMessage with task-specific fields.
    """
    type: str  # Should always be 'task'
    priority: Optional[int]
    retry_count: Optional[int]
    max_retries: Optional[int]


class MessageEnvelope(TypedDict):
    """
    Envelope containing message metadata and payload.
    Used for internal processing and logging.
    """
    message: WorkerMessage
    received_at: datetime
    processing_started_at: Optional[datetime]
    processing_completed_at: Optional[datetime]
    processing_duration: Optional[float]
    success: Optional[bool]
    error: Optional[str]


# Message type constants
class MessageTypes:
    """Constants for message types."""
    GREETING = "greeting"
    TASK = "task"
    HEARTBEAT = "heartbeat"
    STATUS = "status"
    ERROR = "error"


# Queue configuration types
class QueueConfig(TypedDict):
    """Configuration for queue setup."""
    name: str
    durable: bool
    exclusive: bool
    auto_delete: bool


class ConnectionConfig(TypedDict):
    """Configuration for RabbitMQ connection."""
    url: str
    max_retries: int
    retry_delay: int
    heartbeat: int
    connection_timeout: int
