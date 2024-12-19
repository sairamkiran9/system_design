import sqlite3

# Define the database setup
def setup_database():
    connection = sqlite3.connect(":memory:")
    cursor = connection.cursor()

    # Create tables
    cursor.execute("CREATE TABLE inventory (product_id INTEGER PRIMARY KEY, stock INTEGER)")
    cursor.execute("CREATE TABLE payments (order_id INTEGER PRIMARY KEY, status TEXT)")
    cursor.execute("CREATE TABLE orders (order_id INTEGER PRIMARY KEY, status TEXT)")

    # Insert initial data
    cursor.execute("INSERT INTO inventory (product_id, stock) VALUES (1, 10)")
    connection.commit()

    return connection

# Saga step actions
def deduct_inventory(connection):
    cursor = connection.cursor()
    cursor.execute("UPDATE inventory SET stock = stock - 1 WHERE product_id = 1")
    connection.commit()
    print("Inventory deducted successfully.")

def restore_inventory(connection):
    cursor = connection.cursor()
    cursor.execute("UPDATE inventory SET stock = stock + 1 WHERE product_id = 1")
    connection.commit()
    print("Inventory restored.")

def process_payment(connection):
    cursor = connection.cursor()
    cursor.execute("INSERT INTO payments (order_id, status) VALUES (1, 'processed')")
    connection.commit()
    print("Payment processed successfully.")

def refund_payment(connection):
    cursor = connection.cursor()
    cursor.execute("DELETE FROM payments WHERE order_id = 1")
    connection.commit()
    print("Payment refunded.")

def confirm_order(connection):
    cursor = connection.cursor()
    cursor.execute("INSERT INTO orders (order_id, status) VALUES (1, 'confirmed')")
    connection.commit()
    print("Order confirmed successfully.")

def cancel_order(connection):
    cursor = connection.cursor()
    cursor.execute("DELETE FROM orders WHERE order_id = 1")
    connection.commit()
    print("Order cancelled.")

# Saga and SagaStep classes
class SagaStep:
    def __init__(self, name, action, compensation):
        self.name = name
        self.action = action
        self.compensation = compensation

class Saga:
    def __init__(self):
        self.steps = []
        self.compensation_stack = []

    def add_step(self, step):
        self.steps.append(step)

    def execute(self):
        try:
            for step in self.steps:
                print(f"Executing: {step.name}")
                step.action()
                self.compensation_stack.append(step.compensation)
        except Exception as e:
            print(f"Error during {step.name}: {e}")
            self._compensate()

    def _compensate(self):
        while self.compensation_stack:
            compensation = self.compensation_stack.pop()
            print(f"Compensating: {compensation.__name__}")
            compensation()

# Main execution
if __name__ == "__main__":
    connection = setup_database()

    saga = Saga()
    saga.add_step(SagaStep("Deduct Inventory", lambda: deduct_inventory(connection), lambda: restore_inventory(connection)))
    saga.add_step(SagaStep("Process Payment", lambda: process_payment(connection), lambda: refund_payment(connection)))
    saga.add_step(SagaStep("Confirm Order", lambda: confirm_order(connection), lambda: cancel_order(connection)))

    saga.execute()

    # Close the database connection
    connection.close()
