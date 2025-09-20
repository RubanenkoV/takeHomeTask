from kafka import KafkaConsumer
import json

def main():
    consumer = KafkaConsumer(
        'item-events',
        bootstrap_servers=['localhost:9092'],
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )

    print("🔄 Listening for events...")
    for message in consumer:
        event = message.value
        print(f"📥 Received: {event['type']} - {event['data']}")


if __name__ == "__main__":
    main()