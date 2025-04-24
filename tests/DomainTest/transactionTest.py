from unittest import TestCase
from domain.transactions import Transaction, DepositTransactionType, WithdrawTransactionType, TransferTransactionType
from datetime import datetime

<<<<<<< HEAD
from domain.transactions import (
    Transaction, DepositTransactionType, WithdrawTransactionType, TransferTransactionType
)


class TestTransaction(unittest.TestCase):

    def test_transaction_creation_deposit(self):
        # Test successful deposit transaction creation
        now = datetime(2025, 4, 10, 16, 0, 0)
        transaction = Transaction(
            transaction_type=DepositTransactionType(),
            amount=100.00,
=======
class TestTransaction(TestCase):
    def test_deposit_transaction_initialization(self):
        fixed_timestamp = datetime(2023, 1, 1)
        transaction = Transaction(
            transaction_type=DepositTransactionType(),
            amount=100.0,
>>>>>>> c761c5edffc07abf770bfbaa78990093ce673367
            account_id="acc123",
            timestamp=fixed_timestamp
        )
        self.assertEqual(transaction.transaction_type.name, "DEPOSIT")
<<<<<<< HEAD
        self.assertEqual(transaction.amount, 100.00)
=======
        self.assertEqual(transaction.amount, 100.0)
>>>>>>> c761c5edffc07abf770bfbaa78990093ce673367
        self.assertEqual(transaction.account_id, "acc123")
        self.assertEqual(transaction.timestamp, fixed_timestamp)
        self.assertEqual(transaction.transaction_id, f"txn_{fixed_timestamp.timestamp()}")
        self.assertIsNone(transaction.source_account_id)
        self.assertIsNone(transaction.destination_account_id)

    def test_withdraw_transaction_initialization(self):
        fixed_timestamp = datetime(2023, 1, 1)
        transaction = Transaction(
            transaction_type=WithdrawTransactionType(),
<<<<<<< HEAD
            amount=50.00,
=======
            amount=200.0,
>>>>>>> c761c5edffc07abf770bfbaa78990093ce673367
            account_id="acc456",
            timestamp=fixed_timestamp
        )
        self.assertEqual(transaction.transaction_type.name, "WITHDRAW")
<<<<<<< HEAD
        self.assertEqual(transaction.amount, 50.00)
=======
        self.assertEqual(transaction.amount, 200.0)
>>>>>>> c761c5edffc07abf770bfbaa78990093ce673367
        self.assertEqual(transaction.account_id, "acc456")
        self.assertEqual(transaction.timestamp, fixed_timestamp)

<<<<<<< HEAD
    def test_transaction_creation_transfer(self):
        now = datetime(2025, 4, 10, 16, 0, 0)
        transaction = Transaction(
            transaction_type=TransferTransactionType(),
            amount=75.00,
            account_id="acc789",
            source_account_id="acc789",
            destination_account_id="acc101",
            timestamp=now
        )
        self.assertEqual(transaction.transaction_type.name, "TRANSFER")
        self.assertEqual(transaction.source_account_id, "acc789")
        self.assertEqual(transaction.destination_account_id, "acc101")

    def test_transfer_without_accounts(self):
        with self.assertRaises(ValueError):
            Transaction(
                transaction_type=TransferTransactionType(),
                amount=75.00,
                account_id="acc789",
                timestamp=datetime.now()
            )

    def test_transaction_creation_invalid_amount(self):
        # Test invalid amount cases
        test_cases = [
            (DepositTransactionType(), 0, "acc789"),
            (WithdrawTransactionType(), -25.00, "acc101"),
            (DepositTransactionType(), -1.00, "acc102")
        ]

        for trans_type, amount, acc_id in test_cases:
            with self.subTest(trans_type=trans_type, amount=amount, acc_id=acc_id):
                with self.assertRaisesRegex(ValueError, "Transaction amount must be positive"):
                    Transaction(
                        transaction_type=trans_type,
                        amount=amount,
                        account_id=acc_id
                    )
=======
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
>>>>>>> c761c5edffc07abf770bfbaa78990093ce673367

    def test_get_methods(self):
        fixed_timestamp = datetime(2023, 1, 1)
        transaction = Transaction(
<<<<<<< HEAD
            transaction_type=DepositTransactionType(),
            amount=75.50,
            account_id="acc112",
            timestamp=now
        )
        self.assertEqual(transaction.get_transaction_id(), transaction.transaction_id)
        self.assertEqual(transaction.get_amount(), 75.50)
        self.assertEqual(transaction.get_transaction_type().name, "DEPOSIT")
=======
            transaction_type=WithdrawTransactionType(),
            amount=150.0,
            account_id="acc789",
            timestamp=fixed_timestamp
        )
        self.assertEqual(transaction.get_transaction_id(), f"txn_{fixed_timestamp.timestamp()}")
        self.assertEqual(transaction.get_amount(), 150.0)
        self.assertEqual(transaction.get_transaction_type().name, "WITHDRAW")
>>>>>>> c761c5edffc07abf770bfbaa78990093ce673367

    def test_to_dict_deposit(self):
        fixed_timestamp = datetime(2023, 1, 1)
        transaction = Transaction(
            transaction_type=DepositTransactionType(),
<<<<<<< HEAD
            amount=75.50,
            account_id="acc112",
            timestamp=now
        )
        expected_repr = (f"Transaction(transaction_id=txn_{now.timestamp()}, "
                         f"type=DEPOSIT, amount=75.5, account_id=acc112, "
                         f"timestamp={now})")
        self.assertEqual(repr(transaction), expected_repr)

    def test_transaction_to_dict(self):
        # Test dictionary conversion
        now = datetime(2025, 4, 10, 16, 0, 0)
        transaction = Transaction(
            transaction_type=WithdrawTransactionType(),
            amount=30.00,
            account_id="acc131",
            timestamp=now
        )
        expected_dict = {
            "transaction_id": f"txn_{now.timestamp()}",
            "type": "WITHDRAW",
            "amount": 30.00,
            "account_id": "acc131",
            "timestamp": now.isoformat()
=======
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
>>>>>>> c761c5edffc07abf770bfbaa78990093ce673367
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