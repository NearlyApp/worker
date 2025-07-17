# Worker Systems

This repository contains RabbitMQ worker implementations in multiple programming languages, demonstrating message queue patterns with producers and consumers.

## 📁 Projects

### 🐍 Python Implementation
**Location:** `python/`

A complete RabbitMQ setup with Python workers featuring:
- Docker Compose orchestration
- Enhanced logging with configurable levels
- Real-time monitoring tools
- Producer and Consumer workers

[**→ View Python Documentation**](python/README.md)

### 🐹 Go Implementation
**Location:** `golang/`

A Go-based RabbitMQ worker system with:
- High-performance message processing
- Concurrent worker patterns
- Docker containerization

[**→ View Go Documentation**](golang/README.md)

## 🚀 Quick Start

Choose your preferred implementation:

```bash
# Python workers
cd python/
make up

# Go workers  
cd golang/
make up
```

## 🔍 What's Inside

Both implementations provide:
- **Producer**: Sends messages to RabbitMQ queue
- **Consumer**: Processes messages from RabbitMQ queue  
- **RabbitMQ**: Message broker with management UI
- **Docker**: Containerized deployment
- **Monitoring**: Logs and management interface

## 📊 RabbitMQ Management

Access the web interface at: http://localhost:15672
- Username: `admin`
- Password: `admin`

## 🛠️ Development

Each implementation is self-contained with its own:
- Documentation
- Dependencies
- Docker configuration
- Build tools
