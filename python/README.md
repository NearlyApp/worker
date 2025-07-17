# RabbitMQ Python Workers

This project demonstrates a simple RabbitMQ setup with Python producer and consumer workers using Docker.

## Architecture

- **RabbitMQ**: Message broker running in Docker
- **Producer**: Python script that sends messages to RabbitMQ queue
- **Consumer**: Python script that processes messages from RabbitMQ queue

## Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)

## Quick Start

### 1. Start the entire system

```bash
# Build and start all services
make build
make up-logs

# Or in one command
docker-compose up --build
```

### 2. Access RabbitMQ Management UI

- URL: http://localhost:15672
- Username: `admin`
- Password: `admin`

### 3. Monitor the logs

```bash
# View all logs
make logs

# View specific service logs
make logs-producer
make logs-consumer
make logs-rabbitmq
```

## Available Commands

Run `make help` to see all available commands:

```bash
make help
```

Key commands:
- `make up` - Start all services in background
- `make down` - Stop all services
- `make logs` - Show logs
- `make clean` - Remove all containers and volumes
- `make restart` - Restart all services

## Local Development

### Install dependencies locally

```bash
make install-local
```

### Run locally (requires local RabbitMQ)

```bash
# Terminal 1: Start local RabbitMQ
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management

# Terminal 2: Run producer
make run-producer

# Terminal 3: Run consumer
make run-consumer
```

## How it Works

1. **Producer** (`producer.py`):
   - Connects to RabbitMQ
   - Sends messages to a queue named `task_queue` every 5 seconds
   - Messages include ID, content, timestamp, and type

2. **Consumer** (`consumer.py`):
   - Connects to RabbitMQ
   - Listens for messages on the `task_queue`
   - Processes each message (simulates 2 seconds of work)
   - Acknowledges successful processing

3. **Queue Configuration**:
   - Durable queue (survives RabbitMQ restarts)
   - Persistent messages (survive RabbitMQ restarts)
   - QoS prefetch_count=1 (fair dispatch)

## Message Format

```json
{
  "id": 1,
  "content": "Hello from Producer! Message #1",
  "timestamp": "2025-07-17T10:30:00.123456",
  "type": "greeting"
}
```

## Environment Variables

- `RABBITMQ_URL`: RabbitMQ connection URL (default: `amqp://admin:admin@localhost:5672/`)
- `LOG_LEVEL`: Logging level - DEBUG, INFO, WARNING, ERROR, CRITICAL (default: `INFO`)

## Logging Configuration

The system supports configurable log levels through the `LOG_LEVEL` environment variable:

- **DEBUG**: Verbose logging including message content and detailed operations
- **INFO**: Standard operational logging (default)
- **WARNING**: Important issues that don't stop execution
- **ERROR**: Errors that may affect operation
- **CRITICAL**: Severe errors that may cause shutdown

### Setting Log Levels

```bash
# Start with DEBUG logging
make up-debug

# Start with DEBUG logging and rebuild
make up-debug-build

# Change log level for running containers
make set-log-level LEVEL=DEBUG

# Set in environment file
echo "LOG_LEVEL=DEBUG" >> .env
make restart
```

### Log Level Examples

**INFO (Default)**:
```
2025-07-17 13:11:34 |     INFO | producer | 📤 Message sent | ID: 14 | Size: 191 bytes
```

**DEBUG (Verbose)**:
```
2025-07-17 13:11:34 |    DEBUG | producer | 📤 Message content: {'id': 14, 'content': '...'}
```

## Troubleshooting

### Connection Issues

The producer and consumer include retry logic that will attempt to connect to RabbitMQ for up to 60 seconds. This allows RabbitMQ to fully start before the workers try to connect.

### View Container Logs

```bash
# All services
docker-compose logs

# Specific service
docker-compose logs producer
docker-compose logs consumer
docker-compose logs rabbitmq
```

### Restart Services

```bash
# Restart all
make restart

# Restart specific service
docker-compose restart producer
```

### Clean Reset

```bash
# Stop and remove everything
make clean

# Rebuild and start fresh
make build
make up
```

## Scaling

You can scale the consumers to handle more load:

```bash
# Scale to 3 consumer instances
docker-compose up --scale consumer=3 -d
```

## Monitoring

- RabbitMQ Management UI: http://localhost:15672
- Check queue status, message rates, and consumer connections
- Monitor container health with `docker-compose ps`
