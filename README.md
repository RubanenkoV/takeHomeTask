# FastAPI Items API

A simple REST API for managing items, built with FastAPI, containerized with Docker, and featuring Kafka streaming integration and Kubernetes deployment.

*Last updated: 2025-09-20*

## Features

- ✅ Create, read items via REST endpoints
- ✅ In-memory data storage
- ✅ Full type hints and validation
- ✅ Comprehensive tests
- ✅ Docker containerization
- ✅ Kafka streaming integration
- ✅ Kubernetes deployment

## Project Structure

```
takeHomeTask/
├── main.py           # FastAPI application with Kafka integration
├── models.py         # Pydantic data models
├── consumer.py       # Simple Kafka consumer (bonus)
├── test_main.py      # Pytest test suite (includes Kafka tests)
├── requirements.txt  # Python dependencies
├── Dockerfile        # Container configuration
├── k8s.yaml         # Kubernetes deployment manifest
└── README.md         # This file
```

## API Endpoints

| Method | Endpoint      | Description          | Kafka Event           |
|--------|---------------|----------------------|-----------------------|
| GET    | `/`           | API information      | -                     |
| GET    | `/items`      | Get all items        | -                     |
| GET    | `/items/{id}` | Get item by ID       | `item_accessed`       |
| POST   | `/items`      | Create new item      | `item_created`        |

## Quick Start

### 1. Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py

# Access at http://127.0.0.1:8000
```

### 2. Using Docker

```bash
# Build the container
docker build -t items-api .

# Run the container
docker run -d -p 8000:8000 --name items-container items-api

# Test the API
curl http://localhost:8000/items
```

### 3. With Kafka

```bash
# Start Kafka with Docker
docker run -d --name kafka -p 9092:9092 apache/kafka:latest

# Run the app (will now send real Kafka events)
python main.py

# In another terminal, run the consumer to see events
python consumer.py

# Create an item and watch the consumer output
curl -X POST -H "Content-Type: application/json" -d '{"name": "kafka-test"}' http://localhost:8000/items
```

### 4. Kubernetes Deployment

```bash
# Build and tag the image
docker build -t items-api:latest .

# Deploy to Kubernetes
kubectl apply -f k8s.yaml

# Check deployment
kubectl get pods
kubectl get services

# Access the API
kubectl port-forward service/items-api-service 8000:8000
curl http://localhost:8000/items
```

### 5. Fly.io Deployment

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Login to Fly.io
flyctl auth login

# Deploy from GitHub
flyctl launch --from-github RubanenkoV/takeHomeTask
```

Alternatively, it can be deployed directly from the fly.io dashboard.

Live API: https://itemsapi.fly.dev/
API Docs: https://itemsapi.fly.dev/docs

Testing the deployed API:
```bash
curl -X POST -H "Content-Type: application/json" -d '{"name": "deployed-item"}' https://itempsapi.fly.dev/items
```
## Testing

```bash
# Run all tests (including Kafka integration tests)
python -m pytest test_main.py -v

# Expected output: 10 tests passed
```

## API Usage Examples

### Create an item (triggers Kafka event)
```bash
curl -X POST -H "Content-Type: application/json" \
     -d '{"name": "apple"}' \
     http://localhost:8000/items
```

### Get all items
```bash
curl http://localhost:8000/items
```

### Get item by ID (triggers Kafka event)
```bash
curl http://localhost:8000/items/1
```

### Check Kafka status
```bash
curl http://localhost:8000/
# Returns: {"kafka_enabled": true/false, ...}
```

## Streaming Integration

### Kafka Events
The application publishes events to the `item-events` topic:

- **item_created**: When a new item is created
- **item_accessed**: When an item is retrieved by ID

### Event Format
```json
{
  "type": "item_created",
  "data": {"id": 1, "name": "apple"},
  "timestamp": "2024-01-20T10:30:00"
}
```

### Consumer Usage
```bash
# Run the simple consumer
python consumer.py

# Output:
# 🔄 Listening for events...
# 📥 Received: item_created - {'id': 1, 'name': 'apple'}
# 📥 Received: item_accessed - {'id': 1}
```

## Kubernetes Deployment

### Resources Included
- **Deployment**: Single replica of the FastAPI app
- **Service**: LoadBalancer exposing port 8000
- **Minimal configuration**: Production-ready basics

### Scaling
```bash
# Scale the deployment
kubectl scale deployment items-api --replicas=3

# Check scaled pods
kubectl get pods
```

### Logs
```bash
# View application logs
kubectl logs -f deployment/items-api
```

## Requirements

- Python 3.11+
- Docker (for containerization)
- Kafka (optional, for streaming)
- Kubernetes (optional, for deployment)

## Dependencies

- **FastAPI**: Web framework
- **Uvicorn**: ASGI server
- **Pytest**: Testing framework
- **kafka-python**: Kafka integration (bonus)

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │───▶│   Kafka Topic   │───▶│    Consumer     │
│                 │    │  (item-events)  │    │   (Optional)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │
         ▼
┌─────────────────┐
│  In-Memory DB   │
│    (Items)      │
└─────────────────┘
```

