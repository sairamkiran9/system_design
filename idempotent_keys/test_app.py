import pytest
import json
from app import app

# Pytest fixture to provide a test client
@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


def test_successful_payment_with_new_idempotency_key(client):
    """
    Test that a payment with a new idempotency key processes successfully.
    """
    idempotency_key = "unique-key-12345"
    payload = {"user_id": "user_1", "amount": 100}

    response = client.post(
        "/payment",
        headers={"Content-Type": "application/json", "Idempotency-Key": idempotency_key},
        data=json.dumps(payload),
    )

    assert response.status_code == 201
    data = response.get_json()
    assert data["status"] == "success"
    assert data["amount"] == 100
    assert "transaction_id" in data


def test_duplicate_payment_with_same_idempotency_key(client):
    """
    Test that a payment with the same idempotency key returns the cached response.
    """
    idempotency_key = "duplicate-key-12345"
    payload = {"user_id": "user_1", "amount": 100}

    # First request
    first_response = client.post(
        "/payment",
        headers={"Content-Type": "application/json", "Idempotency-Key": idempotency_key},
        data=json.dumps(payload),
    )

    assert first_response.status_code == 201
    first_data = first_response.get_json()
    assert first_data["status"] == "success"
    assert "transaction_id" in first_data

    # Second request with the same key
    second_response = client.post(
        "/payment",
        headers={"Content-Type": "application/json", "Idempotency-Key": idempotency_key},
        data=json.dumps(payload),
    )

    assert second_response.status_code == 200
    second_data = second_response.get_json()

    # Ensure the response is identical to the first response
    assert first_data == second_data


def test_payment_with_missing_idempotency_key(client):
    """
    Test that a request without an idempotency key returns a 400 error.
    """
    payload = {"user_id": "user_1", "amount": 100}

    response = client.post(
        "/payment",
        headers={"Content-Type": "application/json"},
        data=json.dumps(payload),
    )

    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
    assert data["error"] == "Idempotency-Key header is required"


def test_multiple_payments_with_different_idempotency_keys(client):
    """
    Test that multiple payments with different idempotency keys are processed independently.
    """
    payload_1 = {"user_id": "user_1", "amount": 50}
    payload_2 = {"user_id": "user_2", "amount": 75}

    # First payment
    response_1 = client.post(
        "/payment",
        headers={"Content-Type": "application/json", "Idempotency-Key": "key-1"},
        data=json.dumps(payload_1),
    )
    assert response_1.status_code == 201
    data_1 = response_1.get_json()
    assert data_1["status"] == "success"
    assert data_1["amount"] == 50

    # Second payment
    response_2 = client.post(
        "/payment",
        headers={"Content-Type": "application/json", "Idempotency-Key": "key-2"},
        data=json.dumps(payload_2),
    )
    assert response_2.status_code == 201
    data_2 = response_2.get_json()
    assert data_2["status"] == "success"
    assert data_2["amount"] == 75

    # Ensure transaction IDs are different
    assert data_1["transaction_id"] != data_2["transaction_id"]
