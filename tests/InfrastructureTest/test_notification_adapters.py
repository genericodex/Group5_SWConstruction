import unittest
from unittest.mock import patch, MagicMock
from infrastructure.adapters.notification_adapters import (
    EmailNotificationAdapter,
    SMSNotificationAdapter,
    NotificationFactory,
)

class TestNotificationAdapters(unittest.TestCase):
    def setUp(self):
        # Configuration for email adapter
        self.email_config = {
            "smtp_server": "smtp.example.com",
            "smtp_port": 587,
            "username": "user@example.com",
            "password": "password",
            "from_email": "sender@example.com",
        }
        # Configuration for SMS adapter
        self.sms_config = {
            "api_key": "test_api_key",
            "api_url": "https://api.smsprovider.com/send",
            "from_number": "+1234567890",
        }

    @patch('smtplib.SMTP')
    def test_email_notification_adapter_success(self, mock_smtp):
        # Arrange
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        mock_smtp.return_value.__exit__.return_value = None
        adapter = EmailNotificationAdapter(
            smtp_server=self.email_config["smtp_server"],
            smtp_port=self.email_config["smtp_port"],
            username=self.email_config["username"],
            password=self.email_config["password"],
            from_email=self.email_config["from_email"],
        )
        recipient = "recipient@example.com"
        subject = "Test Subject"
        content = "Test Content"

        # Act
        result = adapter.send(recipient, subject, content)

        # Assert
        self.assertTrue(result)
        mock_smtp.assert_called_once_with(self.email_config["smtp_server"], self.email_config["smtp_port"])
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with(self.email_config["username"], self.email_config["password"])
        mock_server.send_message.assert_called_once()
        message = mock_server.send_message.call_args[0][0]
        self.assertEqual(message["Subject"], subject)
        self.assertEqual(message["From"], self.email_config["from_email"])
        self.assertEqual(message["To"], recipient)
        self.assertEqual(message.get_payload(), content)

    @patch('smtplib.SMTP')
    def test_email_notification_adapter_failure(self, mock_smtp):
        # Arrange
        mock_server = MagicMock()
        mock_server.login.side_effect = Exception("Login failed")
        mock_smtp.return_value.__enter__.return_value = mock_server
        mock_smtp.return_value.__exit__.return_value = None
        adapter = EmailNotificationAdapter(
            smtp_server=self.email_config["smtp_server"],
            smtp_port=self.email_config["smtp_port"],
            username=self.email_config["username"],
            password=self.email_config["password"],
            from_email=self.email_config["from_email"],
        )

        # Act
        result = adapter.send("recipient@example.com", "Subject", "Content")

        # Assert
        self.assertFalse(result)
        mock_server.login.assert_called_once()

    @patch('requests.post')
    def test_sms_notification_adapter_success(self, mock_post):
        # Arrange
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        adapter = SMSNotificationAdapter(
            api_key=self.sms_config["api_key"],
            api_url=self.sms_config["api_url"],
            from_number=self.sms_config["from_number"],
        )
        recipient = "+0987654321"
        message = "Test Alert: Test SMS"

        # Act
        result = adapter.send(recipient, message)

        # Assert
        self.assertTrue(result)
        expected_payload = {
            "from": self.sms_config["from_number"],
            "to": recipient,
            "message": message,
        }
        expected_headers = {
            "Authorization": f"Bearer {self.sms_config['api_key']}",
            "Content-Type": "application/json",
        }
        mock_post.assert_called_once_with(self.sms_config["api_url"], json=expected_payload, headers=expected_headers)

    @patch('requests.post')
    def test_sms_notification_adapter_success_no_subject(self, mock_post):
        # Arrange
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        adapter = SMSNotificationAdapter(
            api_key=self.sms_config["api_key"],
            api_url=self.sms_config["api_url"],
            from_number=self.sms_config["from_number"],
        )
        recipient = "+0987654321"
        message = "Test SMS"

        # Act
        result = adapter.send(recipient, message)

        # Assert
        self.assertTrue(result)
        expected_payload = {
            "from": self.sms_config["from_number"],
            "to": recipient,
            "message": message,
        }
        expected_headers = {
            "Authorization": f"Bearer {self.sms_config['api_key']}",
            "Content-Type": "application/json",
        }
        mock_post.assert_called_once_with(self.sms_config["api_url"], json=expected_payload, headers=expected_headers)

    @patch('requests.post')
    def test_sms_notification_adapter_failure(self, mock_post):
        # Arrange
        mock_post.side_effect = Exception("API request failed")
        adapter = SMSNotificationAdapter(
            api_key=self.sms_config["api_key"],
            api_url=self.sms_config["api_url"],
            from_number=self.sms_config["from_number"],
        )
        recipient = "+0987654321"
        message = "Test Alert: Test SMS"

        # Act
        result = adapter.send(recipient, message)

        # Assert
        self.assertFalse(result)
        mock_post.assert_called_once()

    def test_notification_factory_create_email_adapter(self):
        # Act
        adapter = NotificationFactory.create_email_adapter(self.email_config)

        # Assert
        self.assertIsInstance(adapter, EmailNotificationAdapter)
        self.assertEqual(adapter.smtp_server, self.email_config["smtp_server"])
        self.assertEqual(adapter.smtp_port, self.email_config["smtp_port"])
        self.assertEqual(adapter.username, self.email_config["username"])
        self.assertEqual(adapter.password, self.email_config["password"])
        self.assertEqual(adapter.from_email, self.email_config["from_email"])

    def test_notification_factory_create_sms_adapter(self):
        # Act
        adapter = NotificationFactory.create_sms_adapter(self.sms_config)

        # Assert
        self.assertIsInstance(adapter, SMSNotificationAdapter)
        self.assertEqual(adapter.api_key, self.sms_config["api_key"])
        self.assertEqual(adapter.api_url, self.sms_config["api_url"])
        self.assertEqual(adapter.from_number, self.sms_config["from_number"])

if __name__ == '__main__':
    unittest.main()