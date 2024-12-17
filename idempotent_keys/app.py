from flask import Flask, request, jsonify
import uuid

app = Flask(__name__)

# Simulate a database to store idempotency keys and responses
idempotency_store = {}

# Simulated database to track transactions
payments = {}

@app.route('/payment', methods=['POST'])
def process_payment():
    data = request.get_json()
    idempotency_key = request.headers.get('Idempotency-Key')  # Key from client
    user_id = data.get("user_id")
    amount = data.get("amount")

    if not idempotency_key:
        return jsonify({"error": "Idempotency-Key header is required"}), 400

    # Check if the idempotency key already exists
    if idempotency_key in idempotency_store:
        print("Duplicate request detected. Returning cached response.")
        return jsonify(idempotency_store[idempotency_key]), 200

    # Simulate processing the payment
    transaction_id = str(uuid.uuid4())  # Unique transaction ID
    payments[transaction_id] = {"user_id": user_id, "amount": amount}

    # Response after successful payment
    response = {
        "status": "success",
        "transaction_id": transaction_id,
        "user_id": user_id,
        "amount": amount,
    }

    # Save the response in idempotency store
    idempotency_store[idempotency_key] = response

    print(f"Processed payment: {response}")
    return jsonify(response), 201


if __name__ == '__main__':
    app.run(debug=True)
