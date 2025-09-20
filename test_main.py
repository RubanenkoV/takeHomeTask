"""Tests for the Items API with Kafka streaming."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import main
from main import app

client = TestClient(app)


def setup_function():
    """Reset data before each test."""
    import main
    main.items.clear()
    main.next_id = 1


def test_root():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Items API with Kafka"
    assert "kafka_enabled" in data
    assert "endpoints" in data


def test_create_item():
    """Test creating an item."""
    response = client.post("/items", json={"name": "test_item"})
    assert response.status_code == 201
    data = response.json()
    assert data["item"]["name"] == "test_item"
    assert data["item"]["id"] == 1


def test_create_item_sends_kafka_event():
    """Test that creating an item sends a Kafka event."""
    with patch('main.send_event') as mock_send_event:
        response = client.post("/items", json={"name": "kafka_test"})
        assert response.status_code == 201

        # Verify Kafka event was sent
        mock_send_event.assert_called_once_with(
            "item_created",
            {"id": 1, "name": "kafka_test"}
        )


def test_get_items():
    """Test getting all items."""
    client.post("/items", json={"name": "item1"})
    client.post("/items", json={"name": "item2"})

    response = client.get("/items")
    assert response.status_code == 200
    data = response.json()
    assert data["total_items"] == 2
    assert len(data["items"]) == 2


def test_get_item_by_id():
    """Test getting item by ID."""
    response = client.post("/items", json={"name": "findme"})
    item_id = response.json()["item"]["id"]

    response = client.get(f"/items/{item_id}")
    assert response.status_code == 200
    assert response.json()["item"]["name"] == "findme"


def test_get_item_sends_kafka_event():
    """Test that accessing an item sends a Kafka event."""
    # Create item first
    response = client.post("/items", json={"name": "access_test"})
    item_id = response.json()["item"]["id"]

    with patch('main.send_event') as mock_send_event:
        # Access the item
        client.get(f"/items/{item_id}")

        # Verify access event was sent
        mock_send_event.assert_called_once_with(
            "item_accessed",
            {"id": item_id}
        )


def test_get_nonexistent_item():
    """Test 404 for non-existent item."""
    response = client.get("/items/999")
    assert response.status_code == 404


def test_invalid_item():
    """Test validation error."""
    response = client.post("/items", json={})
    assert response.status_code == 422


def test_kafka_fallback_logging():
    """Test that events are logged when Kafka is disabled."""
    with patch('main.KAFKA_ENABLED', False), patch('builtins.print') as mock_print:
        from main import send_event

        send_event("test_event", {"test": "data"})

        # Verify console logging was called
        mock_print.assert_called_once()
        call_args = mock_print.call_args[0][0]
        assert "Event (Kafka disabled): test_event" in call_args


def test_kafka_status_in_root():
    """Test that root endpoint shows Kafka status."""
    response = client.get("/")
    data = response.json()
    assert isinstance(data["kafka_enabled"], bool)


# Run with: python -m pytest test_main.py -v