"""FastAPI Items API with optional Kafka streaming."""
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from models import Item, ItemCreate
import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import and setup Kafka
KAFKA_ENABLED = False
producer = None

try:
    from kafka import KafkaProducer
    producer = KafkaProducer(
        bootstrap_servers=['localhost:9092'],
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        request_timeout_ms=3000,  # Fail if Kafka isn't available
        retries=0  # Don't retry if connection fails
    )
    KAFKA_ENABLED = True
    logger.info("✅ Kafka producer initialized successfully")
except ImportError:
    logger.info("📦 kafka-python not installed - Kafka features disabled")
except Exception as e:
    logger.info(f"📝 Kafka not available ({e}) - falling back to logging")

app = FastAPI(title="Items API", version="1.0.0")

# In-memory storage
items: List[dict] = []
next_id: int = 1

def send_event(event_type: str, data: dict):
    """Send event to Kafka (or log if not available)."""
    event = {
        "type": event_type,
        "data": data,
        "timestamp": datetime.now().isoformat()
    }

    if KAFKA_ENABLED and producer:
        try:
            producer.send('item-events', event)
            producer.flush()  # Ensure message is sent immediately
            logger.info(f"📤 Sent to Kafka: {event_type} - {data}")
        except Exception as e:
            logger.error(f"❌ Failed to send Kafka event: {e}")
            # Fall back to logging
            logger.info(f"📝 Event (Kafka failed): {event_type} - {data}")
    else:
        logger.info(f"📝 Event (Kafka disabled): {event_type} - {data}")

def create_item(item_data: ItemCreate) -> Item:
    """Create a new item."""
    global next_id
    item_dict = {
        "id": next_id,
        "name": item_data.name,
        "created_at": datetime.now()
    }
    items.append(item_dict)

    # Send Kafka event
    send_event("item_created", {"id": next_id, "name": item_data.name})

    next_id += 1
    return Item(**item_dict)

def get_item_by_id(item_id: int) -> Optional[Item]:
    """Get item by ID."""
    for item in items:
        if item["id"] == item_id:
            # Send Kafka event
            send_event("item_accessed", {"id": item_id})
            return Item(**item)
    return None

@app.get("/")
async def root() -> dict:
    return {
        "message": "Items API",
        "kafka_enabled": KAFKA_ENABLED,
        "total_items": len(items),
        "endpoints": {
            "GET /items": "View all items",
            "GET /items/{id}": "Get item by ID",
            "POST /items": "Create item" + (" (sends Kafka event)" if KAFKA_ENABLED else " (logs event)")
        }
    }

@app.post("/items", status_code=201)
async def create_item_endpoint(item: ItemCreate) -> dict:
    created_item = create_item(item)
    return {"item": created_item}

@app.get("/items")
async def get_items() -> dict:
    return {"total_items": len(items), "items": [Item(**item) for item in items]}

@app.get("/items/{item_id}")
async def get_item(item_id: int) -> dict:
    item = get_item_by_id(item_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Item with id {item_id} not found")
    return {"item": item}

@app.get("/events")
async def get_kafka_status() -> dict:
    """Get Kafka status and event info."""
    return {
        "kafka_enabled": KAFKA_ENABLED,
        "message": "Kafka is working!" if KAFKA_ENABLED else "Kafka not available - events are logged to console",
        "note": "Check console/logs to see events"
    }

if __name__ == "__main__":
    import uvicorn

    # Add some test data
    logger.info("🚀 Starting FastAPI Items API...")
    logger.info(f"📊 Kafka enabled: {KAFKA_ENABLED}")

    # Create initial items
    create_item(ItemCreate(name="apple"))
    create_item(ItemCreate(name="banana"))

    logger.info(f"📦 Starting server with {len(items)} items")
    uvicorn.run(app, host="127.0.0.1", port=8000)