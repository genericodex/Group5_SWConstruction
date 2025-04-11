import unittest
from unittest.mock import Mock, patch

from application.repositories.account_repository import IAccountRepository
from application.repositories.transaction_repository import ITransactionRepository
from application.services.transaction_service import TransactionService
from domain.accounts import CheckingAccount
from domain.transactions import Transaction, TransactionType


class TestTransactionService(unittest.TestCase):

    def setUp(self):
        # Create mock repositories
        self.mock_transaction_repo = Mock(spec=ITransactionRepository)
        self.mock_account_repo = Mock(spec=IAccountRepository)

        # Create service with mock repositories
        self.transaction_service = TransactionService(
            transaction_repository=self.mock_transaction_repo,
            account_repository=self.mock_account_repo
        )

        # Create a test account
        self.test_account = CheckingAccount("test-account-123", initial_balance=1000.0)

        # Configure mock account repository to return our test account
        self.mock_account_repo.find_by_id.return_value = self.test_account

    def tearDown(self):
        # Clean up any resources
        pass

    def test_deposit(self):
        # Arrange
        account_id = "test-account-123"
        deposit_amount = 500.0
        initial_balance = self.test_account.get_balance()

        # Act
        transaction = self.transaction_service.deposit(account_id, deposit_amount)

        # Assert
        # Verify the account repository was called to get the account
        self.mock_account_repo.find_by_id.assert_called_once_with(account_id)

        # Verify the transaction was saved
        self.mock_transaction_repo.save.assert_called_once()
        saved_transaction = self.mock_transaction_repo.save.call_args[0][0]
        self.assertIsInstance(saved_transaction, Transaction)
        self.assertEqual(saved_transaction.get_transaction_type(), TransactionType.DEPOSIT)
        self.assertEqual(saved_transaction.get_amount(), deposit_amount)

        # Verify the updated account was saved
        self.mock_account_repo.save.assert_called_once_with(self.test_account)

        # Verify the account balance was updated
        self.assertEqual(self.test_account.get_balance(), initial_balance + deposit_amount)

    def test_withdraw(self):
        # Arrange
        account_id = "test-account-123"
        withdrawal_amount = 300.0
        initial_balance = self.test_account.get_balance()

        # Act
        transaction = self.transaction_service.withdraw(account_id, withdrawal_amount)

        # Assert
        # Verify the account repository was called to get the account
        self.mock_account_repo.find_by_id.assert_called_once_with(account_id)

        # Verify the transaction was saved
        self.mock_transaction_repo.save.assert_called_once()
        saved_transaction = self.mock_transaction_repo.save.call_args[0][0]
        self.assertIsInstance(saved_transaction, Transaction)
        self.assertEqual(saved_transaction.get_transaction_type(), TransactionType.WITHDRAW)
        self.assertEqual(saved_transaction.get_amount(), withdrawal_amount)

        # Verify the updated account was saved
        self.mock_account_repo.save.assert_called_once_with(self.test_account)

        # Verify the account balance was updated
        self.assertEqual(self.test_account.get_balance(), initial_balance - withdrawal_amount)

    def test_withdraw_insufficient_funds(self):
        # Arrange
        account_id = "test-account-123"
        excessive_amount = 2000.0  # More than the balance of 1000.0

        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.transaction_service.withdraw(account_id, excessive_amount)

        self.assertIn("Withdrawal amount exceeds available balance", str(context.exception))

        # Verify the repositories were not called to save anything
        self.mock_transaction_repo.save.assert_not_called()
        self.mock_account_repo.save.assert_not_called()

    def test_account_not_found(self):
        # Arrange
        # Configure mock to return None (account not found)
        self.mock_account_repo.find_by_id.return_value = None
        non_existent_id = "non-existent-account"

        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.transaction_service.deposit(non_existent_id, 100.0)

        self.assertIn(f"Account with ID {non_existent_id} not found", str(context.exception))

        # Verify repositories were not called to save anything
        self.mock_transaction_repo.save.assert_not_called()
        self.mock_account_repo.save.assert_not_called()


if __name__ == '__main__':
    unittest.main()