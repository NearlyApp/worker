package main

import (
	"fmt"
	"log"
	"os"
	"time"

	"github.com/streadway/amqp"
)

func main() {
	// Get RabbitMQ URL from environment variable
	rabbitmqURL := os.Getenv("RABBITMQ_URL")
	if rabbitmqURL == "" {
		rabbitmqURL = "amqp://admin:admin123@localhost:5672/"
	}

	// Wait for RabbitMQ to be ready
	time.Sleep(10 * time.Second)

	// Connect to RabbitMQ
	conn, err := amqp.Dial(rabbitmqURL)
	if err != nil {
		log.Fatalf("Failed to connect to RabbitMQ: %v", err)
	}
	defer conn.Close()

	ch, err := conn.Channel()
	if err != nil {
		log.Fatalf("Failed to open a channel: %v", err)
	}
	defer ch.Close()

	// Declare a queue
	queueName := "task_queue"
	q, err := ch.QueueDeclare(
		queueName, // name
		true,      // durable
		false,     // delete when unused
		false,     // exclusive
		false,     // no-wait
		nil,       // arguments
	)
	if err != nil {
		log.Fatalf("Failed to declare a queue: %v", err)
	}

	// Produce messages
	for i := 1; ; i++ {
		message := fmt.Sprintf("Hello from producer! Message #%d", i)

		err = ch.Publish(
			"",     // exchange
			q.Name, // routing key
			false,  // mandatory
			false,  // immediate
			amqp.Publishing{
				ContentType:  "text/plain",
				Body:         []byte(message),
				DeliveryMode: amqp.Persistent, // make message persistent
			},
		)

		if err != nil {
			log.Printf("Failed to publish a message: %v", err)
		} else {
			log.Printf("Sent: %s", message)
		}

		// Wait 5 seconds before sending next message
		time.Sleep(5 * time.Second)
	}
}
