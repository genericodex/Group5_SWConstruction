import unittest
from unittest.mock import Mock

from application.services.limit_enforcement_service import LimitEnforcementService


class TestLimitEnforcementService(unittest.TestCase):
    def setUp(self):
        self.constraints_repository = Mock()
        self.logging_service = Mock()
        self.service = LimitEnforcementService(self.constraints_repository, self.logging_service)

    def test_check_limit_success(self):
        # Arrange
        account_id = "123"
        transaction_amount = 100.0
        self.constraints_repository.get_limits.return_value = {"daily": 1000, "monthly": 5000}
        self.constraints_repository.get_usage.return_value = {"daily": 500, "monthly": 2000}

        # Act
        result = self.service.check_limit(account_id, transaction_amount)

        # Assert
        self.assertTrue(result)
        self.constraints_repository.update_usage.assert_any_call(account_id, transaction_amount, "daily")
        self.constraints_repository.update_usage.assert_any_call(account_id, transaction_amount, "monthly")
        self.logging_service.log_service_call.assert_called()
        self.assertEqual(self.logging_service.log_service_call.call_count, 2)  # Started and success logs

    def test_check_limit_exceeds_daily_limit(self):
        # Arrange
        account_id = "123"
        transaction_amount = 600.0
        self.constraints_repository.get_limits.return_value = {"daily": 1000, "monthly": 5000}
        self.constraints_repository.get_usage.return_value = {"daily": 500, "monthly": 2000}

        # Act/Assert
        with self.assertRaises(ValueError) as context:
            self.service.check_limit(account_id, transaction_amount)
        self.assertEqual(str(context.exception), "Transaction exceeds daily or monthly limit")
        self.constraints_repository.update_usage.assert_not_called()
        self.logging_service.log_service_call.assert_called()
        self.assertEqual(self.logging_service.log_service_call.call_count, 2)  # Started and failed logs

    def test_check_limit_exceeds_monthly_limit(self):
        # Arrange
        account_id = "123"
        transaction_amount = 3100.0
        self.constraints_repository.get_limits.return_value = {"daily": 1000, "monthly": 5000}
        self.constraints_repository.get_usage.return_value = {"daily": 500, "monthly": 2000}

        # Act/Assert
        with self.assertRaises(ValueError) as context:
            self.service.check_limit(account_id, transaction_amount)
        self.assertEqual(str(context.exception), "Transaction exceeds daily or monthly limit")
        self.constraints_repository.update_usage.assert_not_called()
        self.logging_service.log_service_call.assert_called()
        self.assertEqual(self.logging_service.log_service_call.call_count, 2)  # Started and failed logs

    def test_reset_limits_daily_success(self):
        # Arrange
        account_id = "123"

        # Act
        self.service.reset_limits_daily(account_id)

        # Assert
        self.constraints_repository.reset_usage.assert_called_once_with(account_id, "daily")
        self.logging_service.log_service_call.assert_called()
        self.assertEqual(self.logging_service.log_service_call.call_count, 2)  # Started and success logs

    def test_reset_limits_daily_failure(self):
        # Arrange
        account_id = "123"
        self.constraints_repository.reset_usage.side_effect = Exception("Database error")

        # Act/Assert
        with self.assertRaises(Exception) as context:
            self.service.reset_limits_daily(account_id)
        self.assertEqual(str(context.exception), "Database error")
        self.logging_service.log_service_call.assert_called()
        self.assertEqual(self.logging_service.log_service_call.call_count, 2)  # Started and failed logs

    def test_reset_limits_monthly_success(self):
        # Arrange
        account_id = "123"

        # Act
        self.service.reset_limits_monthly(account_id)

        # Assert
        self.constraints_repository.reset_usage.assert_called_once_with(account_id, "monthly")
        self.logging_service.log_service_call.assert_called()
        self.assertEqual(self.logging_service.log_service_call.call_count, 2)  # Started and success logs

    def test_reset_limits_monthly_failure(self):
        # Arrange
        account_id = "123"
        self.constraints_repository.reset_usage.side_effect = Exception("Database error")

        # Act/Assert
        with self.assertRaises(Exception) as context:
            self.service.reset_limits_monthly(account_id)
        self.assertEqual(str(context.exception), "Database error")
        self.logging_service.log_service_call.assert_called()
        self.assertEqual(self.logging_service.log_service_call.call_count, 2)  # Started and failed logs


if __name__ == '__main__':
    unittest.main()