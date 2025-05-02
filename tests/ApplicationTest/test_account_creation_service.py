import unittest
from unittest.mock import Mock
from uuid import UUID

from application.services.account_service import AccountCreationService
from application.services.notification_service import NotificationService
from domain.savings_account import SavingsAccount
from domain.checking_account import CheckingAccount

class TestAccountCreationService(unittest.TestCase):
    def setUp(self):
        # Create mock repository, notification service, and logging service
        self.mock_repository = Mock()
        self.mock_notification_service = Mock(spec=NotificationService)
        self.mock_logging_service = Mock()  # Add mock for LoggingService
        self.service = AccountCreationService(self.mock_repository, self.mock_notification_service, self.mock_logging_service)
        self.username = "test_user"
        self.password = "secure_password"

    def test_create_savings_account_success(self):
        # Arrange
        account_type = "savings"
        initial_deposit = 150.00  # Above MINIMUM_BALANCE

        # Act
        account_id = self.service.create_account(account_type, self.username, self.password, initial_deposit)

        # Assert
        self.assertTrue(self.is_valid_uuid(account_id))
        self.mock_repository.save.assert_called_once()
        saved_account = self.mock_repository.save.call_args[0][0]
        self.assertIsInstance(saved_account, SavingsAccount)
        self.assertEqual(saved_account.account_id, account_id)
        self.assertEqual(saved_account.username, self.username)
        self.assertTrue(saved_account.verify_password(self.password))
        self.assertEqual(saved_account.balance(), initial_deposit)

        # Optional: Verify logging calls
        self.mock_logging_service.log_service_call.assert_any_call(
            service_name="AccountCreationService",
            method_name="create_account",
            status="started",
            duration_ms=0,
            params={
                "account_type": "savings",
                "username": "test_user",
                "initial_deposit": 150.0,
                "account_tier": "default"
            }
        )
        self.mock_logging_service.info.assert_called_once_with(
            message="Account created successfully",
            context={
                "account_id": account_id,
                "account_type": "savings",
                "username": "test_user",
                "initial_deposit": 150.0,
                "account_tier": "default"
            }
        )

    def test_create_savings_account_below_minimum_balance(self):
        # Arrange
        account_type = "savings"
        initial_deposit = 50.00  # Below MINIMUM_BALANCE

        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.service.create_account(account_type, self.username, self.password, initial_deposit)
        self.assertEqual(
            str(context.exception),
            f"Savings account requires a minimum deposit of ${SavingsAccount.MINIMUM_BALANCE}"
        )
        self.mock_repository.save.assert_not_called()

        # Optional: Verify logging calls
        self.mock_logging_service.log_service_call.assert_any_call(
            service_name="AccountCreationService",
            method_name="create_account",
            status="failed",
            duration_ms=self.mock_logging_service.log_service_call.call_args[1]["duration_ms"],
            params={
                "account_type": "savings",
                "username": "test_user",
                "initial_deposit": 50.0,
                "account_tier": "default"
            },
            error=f"Savings account requires a minimum deposit of ${SavingsAccount.MINIMUM_BALANCE}"
        )

    def test_create_checking_account_success(self):
        # Arrange
        account_type = "checking"
        initial_deposit = 0.00  # Valid for checking account

        # Act
        account_id = self.service.create_account(account_type, self.username, self.password, initial_deposit)

        # Assert
        self.assertTrue(self.is_valid_uuid(account_id))
        self.mock_repository.save.assert_called_once()
        saved_account = self.mock_repository.save.call_args[0][0]
        self.assertIsInstance(saved_account, CheckingAccount)
        self.assertEqual(saved_account.account_id, account_id)
        self.assertEqual(saved_account.username, self.username)
        self.assertTrue(saved_account.verify_password(self.password))
        self.assertEqual(saved_account.balance(), initial_deposit)

        # Optional: Verify logging calls
        self.mock_logging_service.log_service_call.assert_any_call(
            service_name="AccountCreationService",
            method_name="create_account",
            status="started",
            duration_ms=0,
            params={
                "account_type": "checking",
                "username": "test_user",
                "initial_deposit": 0.0,
                "account_tier": "default"
            }
        )
        self.mock_logging_service.info.assert_called_once_with(
            message="Account created successfully",
            context={
                "account_id": account_id,
                "account_type": "checking",
                "username": "test_user",
                "initial_deposit": 0.0,
                "account_tier": "standard"
            }
        )

    def test_create_account_invalid_type(self):
        # Arrange
        account_type = "invalid"
        initial_deposit = 100.00

        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.service.create_account(account_type, self.username, self.password, initial_deposit)
        self.assertEqual(
            str(context.exception),
            "Unknown account type. Choose 'checking' or 'savings'"
        )
        self.mock_repository.save.assert_not_called()

        # Optional: Verify logging calls
        self.mock_logging_service.log_service_call.assert_any_call(
            service_name="AccountCreationService",
            method_name="create_account",
            status="failed",
            duration_ms=self.mock_logging_service.log_service_call.call_args[1]["duration_ms"],
            params={
                "account_type": "invalid",
                "username": "test_user",
                "initial_deposit": 100.0,
                "account_tier": "default"
            },
            error="Unknown account type. Choose 'checking' or 'savings'"
        )

    def is_valid_uuid(self, uuid_str: str) -> bool:
        try:
            UUID(uuid_str)
            return True
        except ValueError:
            return False


if __name__ == '__main__':
    unittest.main()