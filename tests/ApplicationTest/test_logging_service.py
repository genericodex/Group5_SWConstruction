import unittest
import json
import logging
from unittest.mock import patch, MagicMock
from application.services.logging_service import LoggingService


class TestLoggingService(unittest.TestCase):
    def setUp(self):
        # Create a test logger that doesn't output to console during tests
        self.log_service = LoggingService(app_name="TestApp", log_level=logging.CRITICAL)

        # Replace the internal logger with a mock
        self.log_service.logger = MagicMock()

    def test_init_and_setup(self):
        # Test that initialization and setup work correctly
        with patch('os.makedirs') as mock_makedirs, \
                patch('logging.FileHandler') as mock_file_handler, \
                patch('logging.StreamHandler') as mock_stream_handler, \
                patch('os.path.exists', return_value=False) as mock_exists:
            log_service = LoggingService(app_name="TestSetup")

            # Directory creation
            mock_makedirs.assert_called_once()

            # Handlers created
            mock_file_handler.assert_called_once()
            mock_stream_handler.assert_called_once()

    def test_format_log_message(self):
        # Test with no context
        message = "Test message"
        formatted = self.log_service._format_log_message(message)
        self.assertEqual(formatted, message)

        # Test with context
        context = {"key": "value", "number": 42}
        formatted = self.log_service._format_log_message(message, context)
        expected = f"{message} | Context: {json.dumps(context)}"
        self.assertEqual(formatted, expected)

        # Test with context that can't be JSON serialized
        bad_context = {"key": object()}
        formatted = self.log_service._format_log_message(message, bad_context)
        self.assertEqual(formatted, message)

    def test_log_methods(self):
        # Test info method
        test_message = "Info message"
        test_context = {"test": "data"}
        self.log_service.info(test_message, test_context)
        self.log_service.logger.info.assert_called_once()

        # Test warning method
        self.log_service.logger.reset_mock()
        test_message = "Warning message"
        self.log_service.warning(test_message)
        self.log_service.logger.warning.assert_called_once()

        # Test error method
        self.log_service.logger.reset_mock()
        test_message = "Error message"
        self.log_service.error(test_message, test_context)
        self.log_service.logger.error.assert_called_once()

        # Test critical method
        self.log_service.logger.reset_mock()
        test_message = "Critical message"
        self.log_service.critical(test_message)
        self.log_service.logger.critical.assert_called_once()

    def test_log_transaction(self):
        # Test transaction logging
        transaction_id = "tx123"
        transaction_type = "DEPOSIT"
        amount = 100.0
        account_id = "acc456"
        status = "completed"
        details = {"extra": "info"}

        self.log_service.log_transaction(
            transaction_id, transaction_type, amount, account_id, status, details
        )

        self.log_service.logger.info.assert_called_once()
        # Check that the message contains the transaction details
        call_args = self.log_service.logger.info.call_args[0][0]
        self.assertIn(transaction_id, call_args)
        self.assertIn(transaction_type, call_args)
        self.assertIn(status, call_args)

    def test_log_service_call_success(self):
        # Test service call logging for success
        service_name = "TestService"
        method_name = "test_method"
        status = "success"
        duration_ms = 123.45
        params = {"param1": "value1", "password": "secret"}
        result = "Operation succeeded"

        self.log_service.log_service_call(
            service_name, method_name, status, duration_ms, params, result
        )

        self.log_service.logger.info.assert_called_once()
        # Verify sensitive params are masked
        call_args = self.log_service.logger.info.call_args[0][0]
        self.assertIn(service_name, call_args)
        self.assertIn(method_name, call_args)
        self.assertIn(status, call_args)

        # Extract context from the formatted message
        context_str = call_args.split(" | Context: ")[1]
        context = json.loads(context_str)
        self.assertEqual(context['params']['password'], '***')

    def test_log_service_call_error(self):
        # Test service call logging for error
        service_name = "TestService"
        method_name = "test_method"
        status = "error"
        duration_ms = 123.45
        error = "Operation failed"

        self.log_service.log_service_call(
            service_name, method_name, status, duration_ms, error=error
        )

        self.log_service.logger.error.assert_called_once()
        call_args = self.log_service.logger.error.call_args[0][0]
        self.assertIn(service_name, call_args)
        self.assertIn(method_name, call_args)
        self.assertIn(status, call_args)


if __name__ == '__main__':
    unittest.main()