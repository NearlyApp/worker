# RabbitMQ Producer-Consumer Go Application

This project demonstrates a simple RabbitMQ setup with a Go producer and consumer using Docker Compose.

## Components

- **RabbitMQ**: Message broker with management UI
- **Producer**: Go application that sends messages to RabbitMQ every 5 seconds
- **Consumer**: Go application that consumes and processes messages from RabbitMQ

## Prerequisites

- Docker
- Docker Compose

## Quick Start

1. **Build and start all services:**
   ```bash
   docker-compose up --build
   ```

2. **Access RabbitMQ Management UI:**
   - URL: http://localhost:15672
   - Username: `admin`
   - Password: `admin123`

3. **Monitor the logs:**
   ```bash
   # View all services logs
   docker-compose logs -f

   # View specific service logs
   docker-compose logs -f producer
   docker-compose logs -f consumer
   docker-compose logs -f rabbitmq
   ```

## Running Locally (without Docker)

1. **Start RabbitMQ:**
   ```bash
   docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 \
     -e RABBITMQ_DEFAULT_USER=admin \
     -e RABBITMQ_DEFAULT_PASS=admin123 \
     rabbitmq:3.13-management
   ```

2. **Run the producer:**
   ```bash
   go run cmd/producer/main.go
   ```

3. **Run the consumer:**
   ```bash
   go run cmd/consumer/main.go
   ```

## Project Structure

```
worker-go/
├── cmd/
│   ├── producer/
│   │   └── main.go          # Producer application
│   └── consumer/
│       └── main.go          # Consumer application
├── docker-compose.yml       # Docker Compose configuration
├── Dockerfile.producer      # Producer Docker image
├── Dockerfile.consumer      # Consumer Docker image
├── go.mod                   # Go module dependencies
├── go.sum                   # Go module checksums
└── README.md               # This file
```

## How It Works

1. **Producer**: Sends a message every 5 seconds to the `task_queue`
2. **Consumer**: Listens for messages on the `task_queue`, processes them (simulates 2 seconds of work), and acknowledges completion
3. **RabbitMQ**: Acts as the message broker, ensuring reliable message delivery

## Configuration

- **Queue Name**: `task_queue`
- **Queue Durability**: Enabled (messages survive broker restarts)
- **Message Persistence**: Enabled (messages are written to disk)
- **Consumer Acknowledgments**: Manual (ensures messages are processed before being removed from queue)

## Cleanup

To stop and remove all containers:
```bash
docker-compose down

# To also remove volumes (clears RabbitMQ data):
docker-compose down -v
```

## Environment Variables

- `RABBITMQ_URL`: RabbitMQ connection string (default: `amqp://admin:admin123@localhost:5672/`)
