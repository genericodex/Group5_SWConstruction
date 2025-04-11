import unittest
from unittest.mock import Mock, patch

from application.repositories.account_repository import IAccountRepository
from application.services.account_creation_service import AccountCreationService
from domain.accounts import CheckingAccount, SavingsAccount


class TestAccountCreationService(unittest.TestCase):

    def setUp(self):
        # Create mock repository
        self.mock_account_repo = Mock(spec=IAccountRepository)

        # Create service with mock repository
        self.account_creation_service =  AccountCreationService(
            account_repository=self.mock_account_repo
        )

    def tearDown(self):
        # Clean up any resources
        pass

    def test_create_checking_account(self):
        # Arrange
        account_type = "checking"
        initial_deposit = 500.0

        # Act
        account_id = self.account_creation_service.create_account(account_type, initial_deposit)

        # Assert
        # Verify the account was saved to repository
        self.mock_account_repo.save.assert_called_once()

        # Get the saved account from the mock call
        saved_account = self.mock_account_repo.save.call_args[0][0]

        # Verify it's a checking account with correct properties
        self.assertIsInstance(saved_account, CheckingAccount)
        self.assertEqual(saved_account.account_id, account_id)
        self.assertEqual(saved_account.get_balance(), initial_deposit)

    def test_create_savings_account(self):
        # Arrange
        account_type = "savings"
        initial_deposit = 200.0  # Above minimum balance

        # Act
        account_id = self.account_creation_service.create_account(account_type, initial_deposit)

        # Assert
        # Verify the account was saved to repository
        self.mock_account_repo.save.assert_called_once()

        # Get the saved account from the mock call
        saved_account = self.mock_account_repo.save.call_args[0][0]

        # Verify it's a savings account with correct properties
        self.assertIsInstance(saved_account, SavingsAccount)
        self.assertEqual(saved_account.account_id, account_id)
        self.assertEqual(saved_account.get_balance(), initial_deposit)

    def test_create_savings_account_below_minimum_balance(self):
        # Arrange
        account_type = "savings"
        initial_deposit = 50.0  # Below minimum balance of 100.0

        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.account_creation_service.create_account(account_type, initial_deposit)

        self.assertIn(f"Savings account requires a minimum deposit of ${SavingsAccount.MINIMUM_BALANCE}",
                      str(context.exception))

        # Verify no account was saved
        self.mock_account_repo.save.assert_not_called()

    def test_create_unknown_account_type(self):
        # Arrange
        account_type = "premium"  # Invalid account type
        initial_deposit = 1000.0

        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.account_creation_service.create_account(account_type, initial_deposit)

        self.assertIn("Unknown account type", str(context.exception))

        # Verify no account was saved
        self.mock_account_repo.save.assert_not_called()

    @patch('uuid.uuid4')
    def test_create_account_with_uuid(self, mock_uuid):
        # This test verifies that the account ID is a UUID
        # Arrange
        account_type = "checking"
        mock_uuid.return_value = "mocked-uuid"

        # Act
        account_id = self.account_creation_service.create_account(account_type)

        # Assert
        self.assertEqual(account_id, "mocked-uuid")
        self.mock_account_repo.save.assert_called_once()


if __name__ == '__main__':
    unittest.main()