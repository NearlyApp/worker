.PHONY: build up down logs clean producer consumer rabbitmq

# Build and start all services
up:
	docker-compose up --build

# Build and start services in background
up-d:
	docker-compose up --build -d

# Stop all services
down:
	docker-compose down

# Stop all services and remove volumes
clean:
	docker-compose down -v

# View logs for all services
logs:
	docker-compose logs -f

# View logs for specific services
logs-producer:
	docker-compose logs -f producer

logs-consumer:
	docker-compose logs -f consumer

logs-rabbitmq:
	docker-compose logs -f rabbitmq

# Build only
build:
	docker-compose build

# Run producer locally
producer:
	go run cmd/producer/main.go

# Run consumer locally
consumer:
	go run cmd/consumer/main.go

# Start only RabbitMQ for local development
rabbitmq:
	docker run -d --name rabbitmq-dev -p 5672:5672 -p 15672:15672 \
		-e RABBITMQ_DEFAULT_USER=admin \
		-e RABBITMQ_DEFAULT_PASS=admin123 \
		rabbitmq:3.13-management

# Stop local RabbitMQ
rabbitmq-stop:
	docker stop rabbitmq-dev && docker rm rabbitmq-dev

# Download Go dependencies
deps:
	go mod tidy
