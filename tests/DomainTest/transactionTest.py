from unittest import TestCase
from domain.transactions import Transaction, DepositTransactionType, WithdrawTransactionType, TransferTransactionType
from datetime import datetime

class TestTransaction(TestCase):
    def test_deposit_transaction_initialization(self):
        fixed_timestamp = datetime(2023, 1, 1)
        transaction = Transaction(
            transaction_type=DepositTransactionType(),
            amount=100.0,
            account_id="acc123",
            timestamp=fixed_timestamp
        )
        self.assertEqual(transaction.transaction_type.name, "DEPOSIT")
        self.assertEqual(transaction.amount, 100.0)
        self.assertEqual(transaction.account_id, "acc123")
        self.assertEqual(transaction.timestamp, fixed_timestamp)
        self.assertEqual(transaction.transaction_id, f"txn_{fixed_timestamp.timestamp()}")
        self.assertIsNone(transaction.source_account_id)
        self.assertIsNone(transaction.destination_account_id)

    def test_withdraw_transaction_initialization(self):
        fixed_timestamp = datetime(2023, 1, 1)
        transaction = Transaction(
            transaction_type=WithdrawTransactionType(),
            amount=200.0,
            account_id="acc456",
            timestamp=fixed_timestamp
        )
        self.assertEqual(transaction.transaction_type.name, "WITHDRAW")
        self.assertEqual(transaction.amount, 200.0)
        self.assertEqual(transaction.account_id, "acc456")
        self.assertEqual(transaction.timestamp, fixed_timestamp)

    def test_transfer_transaction_initialization(self):
        fixed_timestamp = datetime(2023, 1, 1)
        transaction = Transaction(
            transaction_type=TransferTransactionType(),
            amount=50.0,
            account_id="acc123",
            source_account_id="acc123",
            destination_account_id="acc456",
            timestamp=fixed_timestamp
        )
        self.assertEqual(transaction.transaction_type.name, "TRANSFER")
        self.assertEqual(transaction.amount, 50.0)
        self.assertEqual(transaction.account_id, "acc123")
        self.assertEqual(transaction.source_account_id, "acc123")
        self.assertEqual(transaction.destination_account_id, "acc456")

    def test_get_methods(self):
        fixed_timestamp = datetime(2023, 1, 1)
        transaction = Transaction(
            transaction_type=WithdrawTransactionType(),
            amount=150.0,
            account_id="acc789",
            timestamp=fixed_timestamp
        )
        self.assertEqual(transaction.get_transaction_id(), f"txn_{fixed_timestamp.timestamp()}")
        self.assertEqual(transaction.get_amount(), 150.0)
        self.assertEqual(transaction.get_transaction_type().name, "WITHDRAW")

    def test_to_dict_deposit(self):
        fixed_timestamp = datetime(2023, 1, 1)
        transaction = Transaction(
            transaction_type=DepositTransactionType(),
            amount=100.0,
            account_id="acc123",
            timestamp=fixed_timestamp
        )
        expected = {
            "transaction_id": f"txn_{fixed_timestamp.timestamp()}",
            "type": "DEPOSIT",
            "amount": 100.0,
            "account_id": "acc123",
            "timestamp": fixed_timestamp.isoformat()
        }
        self.assertEqual(transaction.to_dict(), expected)

    def test_to_dict_transfer(self):
        fixed_timestamp = datetime(2023, 1, 1)
        transaction = Transaction(
            transaction_type=TransferTransactionType(),
            amount=50.0,
            account_id="acc123",
            source_account_id="acc123",
            destination_account_id="acc456",
            timestamp=fixed_timestamp
        )
        expected = {
            "transaction_id": f"txn_{fixed_timestamp.timestamp()}",
            "type": "TRANSFER",
            "amount": 50.0,
            "account_id": "acc123",
            "source_account_id": "acc123",
            "destination_account_id": "acc456",
            "timestamp": fixed_timestamp.isoformat()
        }
        self.assertEqual(transaction.to_dict(), expected)

    def test_transaction_amount_positive(self):
        with self.assertRaises(ValueError):
            Transaction(
                transaction_type=DepositTransactionType(),
                amount=-10.0,
                account_id="acc123",
                timestamp=datetime(2023, 1, 1)
            )

    def test_transfer_requires_source_and_destination(self):
        with self.assertRaises(ValueError):
            Transaction(
                transaction_type=TransferTransactionType(),
                amount=50.0,
                account_id="acc123",
                timestamp=datetime(2023, 1, 1)
            )
if __name__ == '__main__':
    import unittest
    unittest.main()