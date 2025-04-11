import unittest
from unittest.mock import Mock, patch
from application.services.transaction_service import TransactionService
from domain.accounts import CheckingAccount
from domain.transactions import Transaction, TransactionType  # Import the enum
from decimal import Decimal
import uuid

class TestTransactionService(unittest.TestCase):
    def setUp(self):
        # Initialize mocks for repositories
        self.account_repository = Mock()
        self.transaction_repository = Mock()
        self.transaction_service = TransactionService(
            self.transaction_repository,
            self.account_repository
        )
        self.account_id = str(uuid.uuid4())
        self.amount = 100.0

    def test_deposit_successful(self):
        # Arrange
        account = CheckingAccount(self.account_id, 0.0)
        self.account_repository.find_by_id.return_value = account
        expected_balance = Decimal(str(self.amount))

        # Act
        transaction = self.transaction_service.deposit(self.account_id, self.amount)

        # Assert
        self.account_repository.find_by_id.assert_called_once_with(self.account_id)
        self.transaction_repository.save.assert_called_once()
        self.account_repository.save.assert_called_once_with(account)
        self.assertEqual(account.balance, expected_balance)
        self.assertIsInstance(transaction, Transaction)
        self.assertEqual(transaction.amount, Decimal(str(self.amount)))
        # Fix: Compare with enum value instead of string
        self.assertEqual(transaction.transaction_type, TransactionType.DEPOSIT)

    def test_deposit_account_not_found(self):
        # Arrange
        self.account_repository.find_by_id.return_value = None

        # Act / Assert
        with self.assertRaises(ValueError) as context:
            self.transaction_service.deposit(self.account_id, self.amount)
        self.assertEqual(
            str(context.exception),
            f"Account with ID {self.account_id} not found"
        )
        self.account_repository.find_by_id.assert_called_once_with(self.account_id)
        self.transaction_repository.save.assert_not_called()
        self.account_repository.save.assert_not_called()

    def test_withdraw_successful(self):
        # Arrange
        initial_balance = 200.0
        account = CheckingAccount(self.account_id, initial_balance)
        self.account_repository.find_by_id.return_value = account
        expected_balance = Decimal(str(initial_balance - self.amount))

        # Act
        transaction = self.transaction_service.withdraw(self.account_id, self.amount)

        # Assert
        self.account_repository.find_by_id.assert_called_once_with(self.account_id)
        self.transaction_repository.save.assert_called_once()
        self.account_repository.save.assert_called_once_with(account)
        self.assertEqual(account.balance, expected_balance)
        self.assertIsInstance(transaction, Transaction)
        self.assertEqual(transaction.amount, Decimal(str(self.amount)))
        # Fix: Compare with enum value instead of string
        self.assertEqual(transaction.transaction_type, TransactionType.WITHDRAW)

    def test_withdraw_insufficient_funds(self):
        # Arrange
        initial_balance = 50.0
        account = CheckingAccount(self.account_id, initial_balance)
        self.account_repository.find_by_id.return_value = account

        # Act / Assert
        with self.assertRaises(ValueError) as context:
            self.transaction_service.withdraw(self.account_id, self.amount)
        self.assertEqual(
            str(context.exception),
            "Withdrawal amount exceeds available balance"
        )
        self.account_repository.find_by_id.assert_called_once_with(self.account_id)
        self.transaction_repository.save.assert_not_called()
        self.account_repository.save.assert_not_called()

    def test_withdraw_account_not_found(self):
        # Arrange
        self.account_repository.find_by_id.return_value = None

        # Act / Assert
        with self.assertRaises(ValueError) as context:
            self.transaction_service.withdraw(self.account_id, self.amount)
        self.assertEqual(
            str(context.exception),
            f"Account with ID {self.account_id} not found"
        )
        self.account_repository.find_by_id.assert_called_once_with(self.account_id)
        self.transaction_repository.save.assert_not_called()
        self.account_repository.save.assert_not_called()

if __name__ == '__main__':
    unittest.main()