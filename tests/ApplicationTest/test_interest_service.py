import unittest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from application.services.interest_service import InterestService
from domain.savings_account import SavingsAccount
from domain.accounts import InterestStrategy
from domain.interest import SavingsInterestStrategy

class TestInterestService(unittest.TestCase):
    def setUp(self):
        # Mock repositories and logging service
        self.account_repository = Mock()
        self.interest_repository = Mock()
        self.logging_service = Mock()

        # Initialize InterestService with mocked dependencies
        self.interest_service = InterestService(
            account_repository=self.account_repository,
            interest_repository=self.interest_repository,
            logging_service=self.logging_service
        )

        # Create a mock SavingsAccount
        self.account_id = "123"
        self.initial_balance = 1000.0
        self.savings_account = SavingsAccount(
            account_id=self.account_id,
            username="testuser",
            password="password",
            initial_balance=self.initial_balance
        )

        # Set up dates for the test (April 1 to April 30, 2025)
        self.start_date = datetime(2025, 4, 1)
        self.end_date = datetime(2025, 4, 30)

    def test_apply_interest_to_account_success(self):
        # Arrange
        self.account_repository.get_by_id.return_value = self.savings_account
        self.account_repository.save.return_value = None

        # Act
        interest = self.interest_service.apply_interest_to_account(
            account_id=self.account_id,
            start_date=self.start_date,
            end_date=self.end_date
        )

        # Assert
        # SavingsInterestStrategy has annual_rate = 0.025 (2.5%)
        # Daily rate = 0.025 / 365
        # Days = 29 (April 1 to April 30)
        # Interest = balance * daily_rate * days
        expected_daily_rate = 0.025 / 365
        expected_days = (self.end_date - self.start_date).days
        expected_interest = self.initial_balance * expected_daily_rate * expected_days

        self.assertAlmostEqual(interest, expected_interest, places=5)
        self.assertEqual(self.savings_account.balance(), self.initial_balance + interest)
        self.account_repository.save.assert_called_once_with(self.savings_account)
        self.logging_service.info.assert_called_with(
            message="Interest applied successfully",
            context={"account_id": self.account_id, "interest": interest}
        )
        self.logging_service.log_service_call.assert_any_call(
            service_name="InterestService",
            method_name="apply_interest_to_account",
            status="started",
            duration_ms=0,
            params={"account_id": self.account_id, "start_date": self.start_date.isoformat(), "end_date": self.end_date.isoformat()}
        )
        self.assertTrue(
            any(
                call[1]["status"] == "success"
                for call in self.logging_service.log_service_call.call_args_list
            )
        )

    def test_apply_interest_to_account_account_not_found(self):
        # Arrange
        self.account_repository.get_by_id.return_value = None

        # Act
        interest = self.interest_service.apply_interest_to_account(
            account_id=self.account_id,
            start_date=self.start_date,
            end_date=self.end_date
        )

        # Assert
        self.assertEqual(interest, 0.0)
        self.logging_service.warning.assert_called_once_with(
            message="Account not found",
            context={"account_id": self.account_id}
        )
        self.logging_service.log_service_call.assert_any_call(
            service_name="InterestService",
            method_name="apply_interest_to_account",
            status="started",
            duration_ms=0,
            params={"account_id": self.account_id, "start_date": self.start_date.isoformat(), "end_date": self.end_date.isoformat()}
        )
        self.assertTrue(
            any(
                call[1]["status"] == "success"
                for call in self.logging_service.log_service_call.call_args_list
            )
        )

    def test_apply_interest_to_account_no_interest_strategy(self):
        # Arrange
        self.savings_account.interest_strategy = None  # Remove the interest strategy
        self.account_repository.get_by_id.return_value = self.savings_account
        self.account_repository.save.return_value = None

        # Act
        interest = self.interest_service.apply_interest_to_account(
            account_id=self.account_id,
            start_date=self.start_date,
            end_date=self.end_date
        )

        # Assert
        self.assertEqual(interest, 0.0)
        self.logging_service.info.assert_called_once_with(
            message="Account is not eligible for interest",
            context={"account_id": self.account_id, "account_type": "SavingsAccount"}
        )
        self.assertEqual(self.savings_account.balance(), self.initial_balance)  # Balance unchanged
        self.account_repository.save.assert_not_called()

    def test_apply_interest_batch_mixed_success_and_failure(self):
        # Arrange
        account_id_1 = "123"
        account_id_2 = "456"
        account_id_3 = "789"

        # Account 1: Success
        savings_account_1 = SavingsAccount(
            account_id=account_id_1,
            username="user1",
            password="password",
            initial_balance=1000.0
        )
        # Account 2: No interest strategy
        savings_account_2 = SavingsAccount(
            account_id=account_id_2,
            username="user2",
            password="password",
            initial_balance=500.0
        )
        savings_account_2.interest_strategy = None
        # Account 3: Not found

        self.account_repository.get_by_id.side_effect = [
            savings_account_1,  # First call
            savings_account_2,  # Second call
            None               # Third call
        ]
        self.account_repository.save.return_value = None

        # Act
        results = self.interest_service.apply_interest_batch(
            account_ids=[account_id_1, account_id_2, account_id_3],
            start_date=self.start_date,
            end_date=self.end_date
        )

        # Assert
        # Account 1: Should have interest applied
        expected_daily_rate = 0.025 / 365
        expected_days = (self.end_date - self.start_date).days
        expected_interest = 1000.0 * expected_daily_rate * expected_days
        self.assertAlmostEqual(results[account_id_1], expected_interest, places=5)
        self.assertEqual(savings_account_1.balance(), 1000.0 + expected_interest)

        # Account 2: No interest applied
        self.assertEqual(results[account_id_2], 0.0)
        self.assertEqual(savings_account_2.balance(), 500.0)

        # Account 3: Not found, should be in results as 0.0
        self.assertEqual(results[account_id_3], 0.0)

        # Logging checks
        self.logging_service.log_service_call.assert_any_call(
            service_name="InterestService",
            method_name="apply_interest_batch",
            status="started",
            duration_ms=0,
            params={"account_ids": [account_id_1, account_id_2, account_id_3], "start_date": self.start_date.isoformat(), "end_date": self.end_date.isoformat()}
        )
        self.assertTrue(
            any(
                call[1]["status"] == "success"
                for call in self.logging_service.log_service_call.call_args_list
            )
        )
        self.logging_service.info.assert_any_call(
            message="Interest applied successfully",
            context={"account_id": account_id_1, "interest": expected_interest}
        )
        self.logging_service.info.assert_any_call(
            message="Account is not eligible for interest",
            context={"account_id": account_id_2, "account_type": "SavingsAccount"}
        )
        self.logging_service.warning.assert_called_once_with(
            message="Account not found",
            context={"account_id": account_id_3}
        )

if __name__ == '__main__':
    unittest.main()