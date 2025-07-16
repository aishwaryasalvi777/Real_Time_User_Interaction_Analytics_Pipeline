# producer.py
import json
import random
import time
from datetime import datetime
from kafka import KafkaProducer

# Sample configuration (adjust if needed)
KAFKA_BROKER = 'localhost:9092'
TOPIC_NAME = 'user_events'

# Create Kafka producer
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Sample event types
event_types = ['click', 'add_to_cart', 'purchase']

# Main loop: generate and send events
def generate_event():
    event = {
        "user_id": random.randint(1, 100),
        "product_id": random.randint(1, 500),
        "event_type": random.choice(event_types),
        "timestamp": datetime.utcnow().isoformat()
    }
    return event

if __name__ == "__main__":
    print(f"Sending events to Kafka topic '{TOPIC_NAME}'...")
    try:
        while True:
            event = generate_event()
            producer.send(TOPIC_NAME, value=event)
            print("Event sent:", event)
            time.sleep(1)  # Send 1 event per second
    except KeyboardInterrupt:
        print("Stopped by user.")
    finally:
        producer.close()
