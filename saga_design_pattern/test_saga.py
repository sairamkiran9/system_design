import unittest
import sqlite3
from io import StringIO
from contextlib import redirect_stdout
from saga import (
    Saga,
    SagaStep,
    deduct_inventory,
    restore_inventory,
    process_payment,
    refund_payment,
    confirm_order,
    cancel_order,
    setup_database,
)


class TestSagaPattern(unittest.TestCase):
    def setUp(self):
        """
        Sets up a fresh SQLite database for each test.
        """
        self.connection = setup_database()

    def tearDown(self):
        """
        Closes the database connection after each test.
        """
        self.connection.close()

    def capture_logs(self, func):
        """
        Captures the output logs from a function for validation.
        """
        output = StringIO()
        with redirect_stdout(output):
            func()
        return output.getvalue()

    def test_successful_saga_execution(self):
        """
        Tests that the Saga executes successfully without any compensation.
        """
        saga = Saga()
        saga.add_step(SagaStep("Deduct Inventory", lambda: deduct_inventory(self.connection), lambda: restore_inventory(self.connection)))
        saga.add_step(SagaStep("Process Payment", lambda: process_payment(self.connection), lambda: refund_payment(self.connection)))
        saga.add_step(SagaStep("Confirm Order", lambda: confirm_order(self.connection), lambda: cancel_order(self.connection)))

        logs = self.capture_logs(saga.execute)

        # Check log outputs for successful execution
        self.assertIn("Executing: Deduct Inventory", logs)
        self.assertIn("Inventory deducted successfully.", logs)
        self.assertIn("Executing: Process Payment", logs)
        self.assertIn("Payment processed successfully.", logs)
        self.assertIn("Executing: Confirm Order", logs)
        self.assertIn("Order confirmed successfully.", logs)

        # Verify database state
        cursor = self.connection.cursor()
        inventory = cursor.execute("SELECT stock FROM inventory WHERE product_id = 1").fetchone()[0]
        payments = cursor.execute("SELECT status FROM payments WHERE order_id = 1").fetchall()
        orders = cursor.execute("SELECT status FROM orders WHERE order_id = 1").fetchall()

        self.assertEqual(inventory, 9)  # Stock reduced by 1
        self.assertEqual(payments[0][0], "processed")
        self.assertEqual(orders[0][0], "confirmed")

    def test_saga_with_compensation(self):
        """
        Tests that the Saga compensates correctly when a failure occurs.
        """
        def failing_payment():
            raise Exception("Simulated payment failure")

        saga = Saga()
        saga.add_step(SagaStep("Deduct Inventory", lambda: deduct_inventory(self.connection), lambda: restore_inventory(self.connection)))
        saga.add_step(SagaStep("Process Payment", failing_payment, lambda: refund_payment(self.connection)))
        saga.add_step(SagaStep("Confirm Order", lambda: confirm_order(self.connection), lambda: cancel_order(self.connection)))

        logs = self.capture_logs(saga.execute)

        # Check log outputs for compensation
        self.assertIn("Executing: Deduct Inventory", logs)
        self.assertIn("Inventory deducted successfully.", logs)
        self.assertIn("Executing: Process Payment", logs)
        self.assertIn("Error during Process Payment", logs)
        self.assertIn("Inventory restored.", logs)

        # Verify database state
        cursor = self.connection.cursor()
        inventory = cursor.execute("SELECT stock FROM inventory WHERE product_id = 1").fetchone()[0]
        payments = cursor.execute("SELECT * FROM payments").fetchall()
        orders = cursor.execute("SELECT * FROM orders").fetchall()

        self.assertEqual(inventory, 10)  # Inventory restored
        self.assertEqual(len(payments), 0)  # No successful payments
        self.assertEqual(len(orders), 0)  # No confirmed orders

    def test_partial_compensation(self):
        """
        Tests compensation for partial success in the Saga execution.
        """
        def failing_order():
            raise Exception("Simulated order confirmation failure")

        saga = Saga()
        saga.add_step(SagaStep("Deduct Inventory", lambda: deduct_inventory(self.connection), lambda: restore_inventory(self.connection)))
        saga.add_step(SagaStep("Process Payment", lambda: process_payment(self.connection), lambda: refund_payment(self.connection)))
        saga.add_step(SagaStep("Confirm Order", failing_order, lambda: cancel_order(self.connection)))

        logs = self.capture_logs(saga.execute)

        # Check log outputs for partial compensation
        self.assertIn("Executing: Deduct Inventory", logs)
        self.assertIn("Inventory deducted successfully.", logs)
        self.assertIn("Executing: Process Payment", logs)
        self.assertIn("Payment processed successfully.", logs)
        self.assertIn("Executing: Confirm Order", logs)
        self.assertIn("Error during Confirm Order", logs)
        self.assertIn("Payment refunded", logs)
        self.assertIn("Inventory restored", logs)

        # Verify database state
        cursor = self.connection.cursor()
        inventory = cursor.execute("SELECT stock FROM inventory WHERE product_id = 1").fetchone()[0]
        payments = cursor.execute("SELECT * FROM payments").fetchall()
        orders = cursor.execute("SELECT * FROM orders").fetchall()

        self.assertEqual(inventory, 10)  # Inventory restored
        self.assertEqual(len(payments), 0)  # No successful payments
        self.assertEqual(len(orders), 0)  # No confirmed orders


if __name__ == "__main__":
    unittest.main()
