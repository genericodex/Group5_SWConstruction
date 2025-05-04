from unittest import TestCase
from unittest.mock import Mock, ANY

from application.repositories.transaction_repository import ITransactionRepository
from application.services.limit_enforcement_service import LimitEnforcementService


class TestLimitEnforcementService(TestCase):
    def setUp(self):
        """Set up mock dependencies and instantiate the service before each test."""
        self.transaction_repo = Mock(spec=ITransactionRepository)
        self.logging_service = Mock()
        self.service = LimitEnforcementService(self.transaction_repo, self.logging_service)

    def test_check_limit_success(self):
        """Test check_limit when transaction is within both daily and monthly limits."""
        account_id = "123"
        transaction_amount = 3000.0
        self.transaction_repo.get_usage.return_value = {"daily": 5000.0, "monthly": 20000.0}

        result = self.service.check_limit(account_id, transaction_amount)

        self.assertTrue(result)
        self.logging_service.log_service_call.assert_any_call(
            service_name="LimitEnforcementService",
            method_name="check_limit",
            status="started",
            duration_ms=0,
            params={"account_id": account_id, "transaction_amount": transaction_amount}
        )
        self.logging_service.log_service_call.assert_any_call(
            service_name="LimitEnforcementService",
            method_name="check_limit",
            status="success",
            duration_ms=ANY,
            params={"account_id": account_id, "transaction_amount": transaction_amount}
        )

    def test_check_limit_exceeds_daily_limit(self):
        """Test check_limit when transaction exceeds the daily limit."""
        account_id = "123"
        transaction_amount = 3000.0
        self.transaction_repo.get_usage.return_value = {"daily": 8000.0, "monthly": 20000.0}

        with self.assertRaises(ValueError):
            self.service.check_limit(account_id, transaction_amount)

        self.logging_service.log_service_call.assert_any_call(
            service_name="LimitEnforcementService",
            method_name="check_limit",
            status="started",
            duration_ms=0,
            params={"account_id": account_id, "transaction_amount": transaction_amount}
        )
        self.logging_service.log_service_call.assert_any_call(
            service_name="LimitEnforcementService",
            method_name="check_limit",
            status="failed",
            duration_ms=ANY,
            params={"account_id": account_id, "transaction_amount": transaction_amount},
            error="Transaction exceeds daily or monthly limit"
        )

    def test_check_limit_exceeds_monthly_limit(self):
        """Test check_limit when transaction exceeds the monthly limit."""
        account_id = "123"
        transaction_amount = 3000.0
        self.transaction_repo.get_usage.return_value = {"daily": 5000.0, "monthly": 48000.0}

        with self.assertRaises(ValueError):
            self.service.check_limit(account_id, transaction_amount)

        self.logging_service.log_service_call.assert_any_call(
            service_name="LimitEnforcementService",
            method_name="check_limit",
            status="started",
            duration_ms=0,
            params={"account_id": account_id, "transaction_amount": transaction_amount}
        )
        self.logging_service.log_service_call.assert_any_call(
            service_name="LimitEnforcementService",
            method_name="check_limit",
            status="failed",
            duration_ms=ANY,
            params={"account_id": account_id, "transaction_amount": transaction_amount},
            error="Transaction exceeds daily or monthly limit"
        )

    def test_check_limit_repository_error(self):
        """Test check_limit when the repository raises an exception."""
        account_id = "123"
        transaction_amount = 1000.0
        self.transaction_repo.get_usage.side_effect = Exception("Database error")

        with self.assertRaises(Exception) as cm:
            self.service.check_limit(account_id, transaction_amount)

        self.assertEqual(str(cm.exception), "Database error")
        self.logging_service.log_service_call.assert_any_call(
            service_name="LimitEnforcementService",
            method_name="check_limit",
            status="started",
            duration_ms=0,
            params={"account_id": account_id, "transaction_amount": transaction_amount}
        )
        self.logging_service.log_service_call.assert_any_call(
            service_name="LimitEnforcementService",
            method_name="check_limit",
            status="failed",
            duration_ms=ANY,
            params={"account_id": account_id, "transaction_amount": transaction_amount},
            error="Database error"
        )

    def test_reset_limits_daily_success(self):
        """Test reset_limits_daily when the reset succeeds."""
        account_id = "123"
        self.transaction_repo.reset_usage.return_value = None

        self.service.reset_limits_daily(account_id)

        self.transaction_repo.reset_usage.assert_called_once_with(account_id, "daily")
        self.logging_service.log_service_call.assert_any_call(
            service_name="LimitEnforcementService",
            method_name="reset_limits_daily",
            status="started",
            duration_ms=0,
            params={"account_id": account_id}
        )
        self.logging_service.log_service_call.assert_any_call(
            service_name="LimitEnforcementService",
            method_name="reset_limits_daily",
            status="success",
            duration_ms=ANY,
            params={"account_id": account_id}
        )

    def test_reset_limits_daily_error(self):
        """Test reset_limits_daily when the repository raises an exception."""
        account_id = "123"
        self.transaction_repo.reset_usage.side_effect = Exception("Database error")

        with self.assertRaises(Exception) as cm:
            self.service.reset_limits_daily(account_id)

        self.assertEqual(str(cm.exception), "Database error")
        self.transaction_repo.reset_usage.assert_called_once_with(account_id, "daily")
        self.logging_service.log_service_call.assert_any_call(
            service_name="LimitEnforcementService",
            method_name="reset_limits_daily",
            status="started",
            duration_ms=0,
            params={"account_id": account_id}
        )
        self.logging_service.log_service_call.assert_any_call(
            service_name="LimitEnforcementService",
            method_name="reset_limits_daily",
            status="failed",
            duration_ms=ANY,
            params={"account_id": account_id},
            error="Database error"
        )

    def test_reset_limits_monthly_success(self):
        """Test reset_limits_monthly when the reset succeeds."""
        account_id = "123"
        self.transaction_repo.reset_usage.return_value = None

        self.service.reset_limits_monthly(account_id)

        self.transaction_repo.reset_usage.assert_called_once_with(account_id, "monthly")
        self.logging_service.log_service_call.assert_any_call(
            service_name="LimitEnforcementService",
            method_name="reset_limits_monthly",
            status="started",
            duration_ms=0,
            params={"account_id": account_id}
        )
        self.logging_service.log_service_call.assert_any_call(
            service_name="LimitEnforcementService",
            method_name="reset_limits_monthly",
            status="success",
            duration_ms=ANY,
            params={"account_id": account_id}
        )

    def test_reset_limits_monthly_error(self):
        """Test reset_limits_monthly when the repository raises an exception."""
        account_id = "123"
        self.transaction_repo.reset_usage.side_effect = Exception("Database error")

        with self.assertRaises(Exception) as cm:
            self.service.reset_limits_monthly(account_id)

        self.assertEqual(str(cm.exception), "Database error")
        self.transaction_repo.reset_usage.assert_called_once_with(account_id, "monthly")
        self.logging_service.log_service_call.assert_any_call(
            service_name="LimitEnforcementService",
            method_name="reset_limits_monthly",
            status="started",
            duration_ms=0,
            params={"account_id": account_id}
        )
        self.logging_service.log_service_call.assert_any_call(
            service_name="LimitEnforcementService",
            method_name="reset_limits_monthly",
            status="failed",
            duration_ms=ANY,
            params={"account_id": account_id},
            error="Database error"
        )