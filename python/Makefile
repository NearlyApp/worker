.PHONY: help build up down logs clean install-local run-producer run-consumer

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

build: ## Build all Docker images
	docker-compose build

up: ## Start all services
	docker-compose up -d

up-build: ## Build and start all services
	docker-compose up --build -d

up-logs: ## Start all services and show logs
	docker-compose up

down: ## Stop all services
	docker-compose down

logs: ## Show logs for all services
	docker-compose logs -f

logs-rabbitmq: ## Show RabbitMQ logs
	docker-compose logs -f rabbitmq

logs-producer: ## Show producer logs
	docker-compose logs -f producer

logs-consumer: ## Show consumer logs
	docker-compose logs -f consumer

restart: ## Restart all services
	docker-compose restart

clean: ## Remove all containers and volumes
	docker-compose down -v
	docker-compose rm -f

install-local: ## Install Python dependencies locally
	pip install -r requirements.txt

run-producer: ## Run producer locally (requires local RabbitMQ)
	python producer.py

run-consumer: ## Run consumer locally (requires local RabbitMQ)
	python consumer.py

status: ## Show status of all containers
	docker-compose ps

shell-producer: ## Open shell in producer container
	docker-compose exec producer /bin/bash

shell-consumer: ## Open shell in consumer container
	docker-compose exec consumer /bin/bash

rabbitmq-management: ## Open RabbitMQ management UI
	@echo "RabbitMQ Management UI: http://localhost:15672"
	@echo "Username: admin"
	@echo "Password: admin"

monitor: ## Run the monitoring script locally
	python monitor.py

monitor-docker: ## Run the monitoring script in a container
	docker run --rm --network python_rabbitmq_net -e RABBITMQ_URL=amqp://admin:admin@rabbitmq:5672/ -v $(PWD):/app -w /app python:3.11-slim bash -c "pip install pika && python monitor.py"

logs-follow: ## Follow logs from all services in real-time
	docker compose logs -f

logs-producer-follow: ## Follow producer logs in real-time
	docker compose logs -f producer

logs-consumer-follow: ## Follow consumer logs in real-time  
	docker compose logs -f consumer

up-debug: ## Start all services with DEBUG log level
	LOG_LEVEL=DEBUG docker compose up

up-debug-build: ## Build and start all services with DEBUG log level
	LOG_LEVEL=DEBUG docker compose up --build

up-verbose: ## Start all services with DEBUG log level in background
	LOG_LEVEL=DEBUG docker compose up -d

restart-debug: ## Restart services with DEBUG logging
	LOG_LEVEL=DEBUG docker compose restart

set-log-level: ## Set log level for running containers (usage: make set-log-level LEVEL=DEBUG)
	@echo "Restarting containers with LOG_LEVEL=$(LEVEL)"
	LOG_LEVEL=$(LEVEL) docker compose restart
