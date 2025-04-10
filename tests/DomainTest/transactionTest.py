import unittest
from datetime import datetime

from domain.transactions import Transaction, TransactionType


class TestTransaction(unittest.TestCase):

    def test_transaction_creation_deposit(self):
        # Test successful deposit transaction creation
        now = datetime(2025, 4, 10, 16, 0, 0)
        transaction = Transaction(
            transaction_type=TransactionType.DEPOSIT,
            amount=100.00,
            account_id="acc123",
            timestamp=now
        )
        self.assertEqual(transaction.transaction_type, TransactionType.DEPOSIT)
        self.assertEqual(transaction.amount, 100.00)
        self.assertEqual(transaction.account_id, "acc123")
        self.assertEqual(transaction.timestamp, now)
        self.assertTrue(transaction.transaction_id.startswith("txn_"))
        self.assertEqual(float(transaction.transaction_id[4:]), now.timestamp())

    def test_transaction_creation_withdraw(self):
        # Test successful withdraw transaction creation
        now = datetime(2025, 4, 10, 16, 0, 0)
        transaction = Transaction(
            transaction_type=TransactionType.WITHDRAW,
            amount=50.00,
            account_id="acc456",
            timestamp=now
        )
        self.assertEqual(transaction.transaction_type, TransactionType.WITHDRAW)
        self.assertEqual(transaction.amount, 50.00)
        self.assertEqual(transaction.account_id, "acc456")
        self.assertEqual(transaction.timestamp, now)
        self.assertTrue(transaction.transaction_id.startswith("txn_"))

    def test_transaction_creation_invalid_amount(self):
        # Test invalid amount cases
        test_cases = [
            (TransactionType.DEPOSIT, 0, "acc789"),
            (TransactionType.WITHDRAW, -25.00, "acc101"),
            (TransactionType.DEPOSIT, -1.00, "acc102")
        ]

        for trans_type, amount, acc_id in test_cases:
            with self.subTest(trans_type=trans_type, amount=amount, acc_id=acc_id):
                with self.assertRaisesRegex(ValueError, "Transaction amount must be positive"):
                    Transaction(
                        transaction_type=trans_type,
                        amount=amount,
                        account_id=acc_id
                    )

    def test_get_methods(self):
        # Test getter methods
        now = datetime(2025, 4, 10, 16, 0, 0)
        transaction = Transaction(
            transaction_type=TransactionType.DEPOSIT,
            amount=75.50,
            account_id="acc112",
            timestamp=now
        )
        self.assertEqual(transaction.get_transaction_id(), transaction.transaction_id)
        self.assertEqual(transaction.get_amount(), 75.50)
        self.assertEqual(transaction.get_transaction_type(), TransactionType.DEPOSIT)

    def test_transaction_repr(self):
        # Test string representation
        now = datetime(2025, 4, 10, 16, 0, 0)
        transaction = Transaction(
            transaction_type=TransactionType.DEPOSIT,
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
            transaction_type=TransactionType.WITHDRAW,
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
        }
        self.assertEqual(transaction.to_dict(), expected_dict)


if __name__ == '__main__':
    unittest.main()