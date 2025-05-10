import unittest
from unittest.mock import MagicMock, Mock
from application.services.notification_service import NotificationService
from domain.accounts import Account
from domain.transactions import Transaction, DepositTransactionType, WithdrawTransactionType, TransferTransactionType
from infrastructure.adapters.notification_adapters import EmailNotificationAdapter, SMSNotificationAdapter


class TestNotificationService(unittest.TestCase):
    def setUp(self):
        """Set up the test environment before each test."""
        # Mock the email, SMS adapters, and logging service
        self.email_adapter = MagicMock(spec=EmailNotificationAdapter)
        self.sms_adapter = MagicMock(spec=SMSNotificationAdapter)
        self.logging_service = MagicMock()  # Add mock for LoggingService

        # Initialize the NotificationService with mocked adapters and logging service
        self.notification_service = NotificationService(
            email_adapter=self.email_adapter,
            sms_adapter=self.sms_adapter,
            logging_service=self.logging_service
        )

        # Create a mock account with email and phone attributes
        self.mock_account = Mock(spec=Account)
        self.mock_account.email = "test@example.com"
        self.mock_account.phone = "+12345678900"

        # Create test transactions with associated account
        self.deposit_txn = Transaction(
            transaction_type=DepositTransactionType(),
            amount=100.00,
            account_id="ACC123",
        )
        self.deposit_txn.transaction_id = "TXN001"
        self.deposit_txn.account = self.mock_account

        self.withdraw_txn = Transaction(
            transaction_type=WithdrawTransactionType(),
            amount=50.00,
            account_id="ACC123",
        )
        self.withdraw_txn.transaction_id = "TXN002"
        self.withdraw_txn.account = self.mock_account

        self.transfer_txn = Transaction(
            transaction_type=TransferTransactionType(),
            amount=75.00,
            account_id="ACC123",
            source_account_id="ACC123",
            destination_account_id="ACC456"
        )
        self.transfer_txn.transaction_id = "TXN003"
        self.transfer_txn.account = self.mock_account

        # Create mock strategies for observer pattern tests
        self.mock_logger = Mock()
        self.mock_email = Mock()
        self.mock_sms = Mock()

        # Override notification strategies with mocks for observer pattern tests
        self.notification_service._notification_strategies["default"] = [self.mock_logger]
        self.notification_service._notification_strategies["standard"] = [self.mock_logger, self.mock_email]
        self.notification_service._notification_strategies["premium"] = [self.mock_logger, self.mock_email, self.mock_sms]

    def test_notify_transaction_default_strategy(self):
        """Test that notify_transaction triggers default strategy (logging)."""
        self.notification_service.notify_transaction(self.deposit_txn)
        self.mock_logger.assert_called_once_with(self.deposit_txn)

    def test_register_account_observers_standard_tier(self):
        """Test registering observers for standard tier (logger + email)."""
        self.notification_service.register_account_observers(self.mock_account, "standard")
        self.mock_account.add_observer.assert_any_call(self.mock_logger)
        self.mock_account.add_observer.assert_any_call(self.mock_email)
        self.assertEqual(self.mock_account.add_observer.call_count, 2)

    def test_register_account_observers_premium_tier(self):
        """Test registering observers for premium tier (logger + email + sms)."""
        self.notification_service.register_account_observers(self.mock_account, "premium")
        self.mock_account.add_observer.assert_any_call(self.mock_logger)
        self.mock_account.add_observer.assert_any_call(self.mock_email)
        self.mock_account.add_observer.assert_any_call(self.mock_sms)
        self.assertEqual(self.mock_account.add_observer.call_count, 3)

    def test_register_account_observers_default_tier(self):
        """Test registering observers for default tier (logger only)."""
        self.notification_service.register_account_observers(self.mock_account, "default")
        self.mock_account.add_observer.assert_called_once_with(self.mock_logger)

    def test_register_account_observers_unknown_tier_falls_back_to_default(self):
        """Test that an unknown tier falls back to default (logger only)."""
        self.notification_service.register_account_observers(self.mock_account, "invalid_tier")
        self.mock_account.add_observer.assert_called_once_with(self.mock_logger)

    def test_add_custom_notification_strategy_new_tier(self):
        """Test adding a custom strategy to a new tier."""
        custom_strategy = Mock()
        self.notification_service.add_custom_notification_strategy("custom_tier", custom_strategy)
        self.assertIn("custom_tier", self.notification_service._notification_strategies)
        self.assertEqual(len(self.notification_service._notification_strategies["custom_tier"]), 2)
        self.assertEqual(self.notification_service._notification_strategies["custom_tier"][1], custom_strategy)

    def test_add_custom_notification_strategy_existing_tier(self):
        """Test adding a custom strategy to an existing tier."""
        custom_strategy = Mock()
        self.notification_service.add_custom_notification_strategy("standard", custom_strategy)
        self.assertEqual(len(self.notification_service._notification_strategies["standard"]), 3)
        self.assertEqual(self.notification_service._notification_strategies["standard"][2], custom_strategy)

    def test_init_with_adapters(self):
        """Test initialization with adapters."""
        service = NotificationService(
            email_adapter=self.email_adapter,
            sms_adapter=self.sms_adapter,
            logging_service=self.logging_service
        )
        self.assertEqual(service.email_adapter, self.email_adapter)
        self.assertEqual(service.sms_adapter, self.sms_adapter)

    def test_init_without_adapters(self):
        """Test initialization without adapters."""
        service = NotificationService(logging_service=self.logging_service)
        self.assertIsNone(service.email_adapter)
        self.assertIsNone(service.sms_adapter)

    def test_send_email_notification_deposit(self):
        """Test sending email notification for a deposit transaction."""
        self.notification_service._notification_strategies["standard"] = [
            self.mock_logger, self.notification_service._email_notifier
        ]

        self.notification_service._email_notifier(self.deposit_txn)

        self.email_adapter.send.assert_called_once()
        args = self.email_adapter.send.call_args[0]

        self.assertEqual(args[0], "test@example.com")
        self.assertEqual(args[1], "Deposit Notification")
        self.assertIn("deposit of $100.0", args[2].lower())
        self.assertIn("ACC123", args[2])

        # Verify logging calls
        self.logging_service.log_service_call.assert_any_call(
            service_name="NotificationService",
            method_name="_email_notifier",
            status="started",
            duration_ms=0,
            params={"transaction_id": "TXN001", "transaction_type": "DEPOSIT"}
        )
        self.logging_service.log_service_call.assert_any_call(
            service_name="NotificationService",
            method_name="_email_notifier",
            status="success",
            duration_ms=self.logging_service.log_service_call.call_args[1]["duration_ms"],
            params={"transaction_id": "TXN001", "transaction_type": "DEPOSIT"},
            result="Email sent to test@example.com"
        )

    def test_send_email_notification_withdraw(self):
        """Test sending email notification for a withdrawal transaction."""
        self.notification_service._notification_strategies["standard"] = [
            self.mock_logger, self.notification_service._email_notifier
        ]

        self.notification_service._email_notifier(self.withdraw_txn)

        self.email_adapter.send.assert_called_once()
        args = self.email_adapter.send.call_args[0]

        self.assertEqual(args[0], "test@example.com")
        self.assertEqual(args[1], "Withdrawal Notification")
        self.assertIn("withdrawal of $50.0", args[2].lower())
        self.assertIn("ACC123", args[2])

        # Verify logging calls
        self.logging_service.log_service_call.assert_any_call(
            service_name="NotificationService",
            method_name="_email_notifier",
            status="success",
            duration_ms=self.logging_service.log_service_call.call_args[1]["duration_ms"],
            params={"transaction_id": "TXN002", "transaction_type": "WITHDRAW"},
            result="Email sent to test@example.com"
        )

    def test_send_email_notification_transfer(self):
        """Test sending email notification for a transfer transaction."""
        self.notification_service._notification_strategies["standard"] = [
            self.mock_logger, self.notification_service._email_notifier
        ]

        self.notification_service._email_notifier(self.transfer_txn)

        self.email_adapter.send.assert_called_once()
        args = self.email_adapter.send.call_args[0]

        self.assertEqual(args[0], "test@example.com")
        self.assertEqual(args[1], "Transfer Notification")
        self.assertIn("transfer of $75.0", args[2].lower())
        self.assertIn("ACC123", args[2])
        self.assertIn("ACC456", args[2])

        # Verify logging calls
        self.logging_service.log_service_call.assert_any_call(
            service_name="NotificationService",
            method_name="_email_notifier",
            status="success",
            duration_ms=self.logging_service.log_service_call.call_args[1]["duration_ms"],
            params={"transaction_id": "TXN003", "transaction_type": "TRANSFER"},
            result="Email sent to test@example.com"
        )

    def test_send_email_notification_no_adapter(self):
        """Test sending email notification with no adapter."""
        service = NotificationService(logging_service=self.logging_service)  # No email adapter
        service._email_notifier(self.deposit_txn)  # Should not call send or log

    def test_send_sms_notification_deposit(self):
        """Test sending SMS notification for a deposit transaction."""
        self.notification_service._notification_strategies["premium"] = [
            self.mock_logger, self.mock_email, self.notification_service._sms_notifier
        ]

        self.notification_service._sms_notifier(self.deposit_txn)

        self.sms_adapter.send.assert_called_once()
        args = self.sms_adapter.send.call_args[0]

        self.assertEqual(args[0], "+12345678900")
        self.assertEqual(args[1], "Deposit Alert: Deposit of $100.0 to account ACC123 completed.")

        # Verify logging calls
        self.logging_service.log_service_call.assert_any_call(
            service_name="NotificationService",
            method_name="_sms_notifier",
            status="success",
            duration_ms=self.logging_service.log_service_call.call_args[1]["duration_ms"],
            params={"transaction_id": "TXN001", "transaction_type": "DEPOSIT"},
            result="SMS sent to +12345678900"
        )

    def test_send_sms_notification_withdraw(self):
        """Test sending SMS notification for a withdrawal transaction."""
        self.notification_service._notification_strategies["premium"] = [
            self.mock_logger, self.mock_email, self.notification_service._sms_notifier
        ]

        self.notification_service._sms_notifier(self.withdraw_txn)

        self.sms_adapter.send.assert_called_once()
        args = self.sms_adapter.send.call_args[0]

        self.assertEqual(args[0], "+12345678900")
        self.assertEqual(args[1], "Withdrawal Alert: Withdrawal of $50.0 from account ACC123 completed.")

        # Verify logging calls
        self.logging_service.log_service_call.assert_any_call(
            service_name="NotificationService",
            method_name="_sms_notifier",
            status="success",
            duration_ms=self.logging_service.log_service_call.call_args[1]["duration_ms"],
            params={"transaction_id": "TXN002", "transaction_type": "WITHDRAW"},
            result="SMS sent to +12345678900"
        )

    def test_send_sms_notification_transfer(self):
        """Test sending SMS notification for a transfer transaction."""
        self.notification_service._notification_strategies["premium"] = [
            self.mock_logger, self.mock_email, self.notification_service._sms_notifier
        ]

        self.notification_service._sms_notifier(self.transfer_txn)

        self.sms_adapter.send.assert_called_once()
        args = self.sms_adapter.send.call_args[0]

        self.assertEqual(args[0], "+12345678900")
        self.assertEqual(args[1], "Transfer Alert: Transfer of $75.0 from account ACC123 to ACC456 completed.")

        # Verify logging calls
        self.logging_service.log_service_call.assert_any_call(
            service_name="NotificationService",
            method_name="_sms_notifier",
            status="success",
            duration_ms=self.logging_service.log_service_call.call_args[1]["duration_ms"],
            params={"transaction_id": "TXN003", "transaction_type": "TRANSFER"},
            result="SMS sent to +12345678900"
        )

    def test_send_sms_notification_no_adapter(self):
        """Test sending SMS notification with no adapter."""
        service = NotificationService(logging_service=self.logging_service)  # No SMS adapter
        service._sms_notifier(self.deposit_txn)  # Should not call send or log

    def test_unknown_transaction_type(self):
        """Test handling of an unknown transaction type."""
        mock_txn_type = MagicMock()
        mock_txn_type.name = "UNKNOWN_TYPE"

        unknown_txn = Transaction(
            transaction_type=mock_txn_type,
            amount=100.00,
            account_id="ACC123",
        )
        unknown_txn.account = self.mock_account

        # Test email notification with unknown type
        self.notification_service._email_notifier(unknown_txn)
        self.email_adapter.send.assert_not_called()

        # Test SMS notification with unknown type
        self.notification_service._sms_notifier(unknown_txn)
        self.sms_adapter.send.assert_not_called()


if __name__ == '__main__':
    unittest.main()