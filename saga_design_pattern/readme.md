# Saga Design Pattern Example

## Overview

This project demonstrates the implementation of the **Saga Design Pattern** in Python, using a SQLite in-memory database. The Saga pattern is commonly used in distributed systems to ensure consistency when handling complex transactions that span multiple services. In this example, a simulated order fulfillment workflow is modeled as a saga, including steps for inventory deduction, payment processing, and order confirmation.

---

## Features

- **Atomic Transactions**: Ensures consistency by defining both forward and compensating actions for each step.
- **Error Handling**: Implements rollback (compensation) for previously executed steps if any step fails.
- **In-Memory Database**: Uses SQLite for simplicity and ease of setup.
- **Extensible Design**: Provides `Saga` and `SagaStep` classes that can be reused in other workflows.

---

## Workflow Description

The saga handles an order fulfillment process:
1. Deduct inventory for the ordered product.
2. Process the payment for the order.
3. Confirm the order.

If any step fails, previously executed steps are compensated to maintain system consistency.

---

## Project Structure

### Database Setup
The database is initialized in memory with three tables:
- **`inventory`**: Tracks product stock.
- **`payments`**: Tracks payment statuses.
- **`orders`**: Tracks order statuses.

### Saga Steps
Each step in the workflow includes:
- A **forward action** (e.g., deducting inventory).
- A **compensation action** (e.g., restoring inventory if payment fails).

### Saga Execution
The `Saga` class:
- Executes steps in sequence.
- Rolls back previously executed steps if an error occurs.

---

## How It Works

### Key Classes

#### `SagaStep`
Represents a single step in the saga.

- **Attributes**:
  - `name`: The step name.
  - `action`: The forward action (a callable).
  - `compensation`: The compensating action (a callable).

#### `Saga`
Manages the sequence of `SagaStep` objects.

- **Methods**:
  - `add_step(step)`: Adds a step to the saga.
  - `execute()`: Executes all steps. If a step fails, compensates for previously executed steps.

### Saga Steps in Workflow
1. **Deduct Inventory**:
   - **Action**: Decrease stock in the `inventory` table.
   - **Compensation**: Restore stock if subsequent steps fail.
2. **Process Payment**:
   - **Action**: Insert a payment record into the `payments` table.
   - **Compensation**: Refund payment if subsequent steps fail.
3. **Confirm Order**:
   - **Action**: Insert a record into the `orders` table.
   - **Compensation**: Delete the order if subsequent steps fail.

---

## Code Walkthrough

## Example Output

Sample run of the program:
```
Executing: Deduct Inventory
Inventory deducted successfully.
Executing: Process Payment
Payment processed successfully.
Executing: Confirm Order
Order confirmed successfully.
```

If an error occurs (e.g., in the "Process Payment" step):
```
Executing: Deduct Inventory
Inventory deducted successfully.
Executing: Process Payment
Error during Process Payment: <error message>
Compensating: restore_inventory
Inventory restored.
```

---

## Dependencies

- Python 3.x
- SQLite3 (built-in with Python)

---

## How to Run

1. Clone the repository or copy the code.
2. Save the script as `saga_example.py`.
3. Run the script:
   ```bash
   python saga_example.py
   ```
4. To test the script:
    ```bash
    python test_saga.py
    ```
---

## Extending the Example

1. **Add New Steps**:
   - Define new forward and compensation actions.
   - Add them to the saga using `add_step`.

2. **Persist Data**:
   - Replace the in-memory SQLite database with a persistent database.

3. **Integrate with External Services**:
   - Replace dummy functions (e.g., `process_payment`) with real APIs.

---

## Benefits of the Saga Pattern

1. **Consistency**: Ensures data integrity across distributed systems.
2. **Resilience**: Handles failures gracefully by rolling back completed steps.
3. **Flexibility**: Steps can be executed asynchronously or in a distributed environment.
