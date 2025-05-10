from abc import ABC, abstractmethod
import logging
import smtplib
from email.mime.text import MIMEText
import requests
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Decorator for logging method calls
def log_method(func):
    def wrapper(*args, **kwargs):
        logger.info(f"Calling {func.__name__} with args: {args[1:]}, kwargs: {kwargs}")
        result = func(*args, **kwargs)
        logger.info(f"Completed {func.__name__}, result: {result}")
        return result
    return wrapper

class NotificationAdapter(ABC):
    """Base abstract class for notification adapters"""

    @abstractmethod
    def send(self, *args, **kwargs) -> bool:
        """Send notification to recipient"""
        pass


class EmailNotificationAdapter(NotificationAdapter):
    """Adapter for sending email adapters"""

    def __init__(self, smtp_server: str, smtp_port: int, username: str, password: str,
                 from_email: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_email = from_email

    @log_method
    def send(self, recipient: str, subject: str, content: str) -> bool:
        """Send email notification"""
        try:
            msg = MIMEText(content)
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = recipient

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)

            logger.info(f"Email sent to {recipient}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {recipient}: {str(e)}")
            return False


class SMSNotificationAdapter(NotificationAdapter):
    """Adapter for sending SMS adapters"""

    def __init__(self, api_key: str, api_url: str, from_number: str):
        self.api_key = api_key
        self.api_url = api_url
        self.from_number = from_number

    @log_method
    def send(self, recipient: str, message: str) -> bool:
        """Send SMS notification"""
        try:
            payload = {
                "from": self.from_number,
                "to": recipient,
                "message": message
            }

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            response = requests.post(self.api_url, json=payload, headers=headers)
            response.raise_for_status()

            logger.info(f"SMS sent to {recipient}")
            return True
        except Exception as e:
            logger.error(f"Failed to send SMS to {recipient}: {str(e)}")
            return False


class NotificationFactory:
    """Factory for creating notification adapters"""

    @staticmethod
    def create_email_adapter(config: Dict[str, Any]) -> EmailNotificationAdapter:
        """Create email notification adapter from config"""
        return EmailNotificationAdapter(
            smtp_server=config.get("smtp_server"),
            smtp_port=config.get("smtp_port"),
            username=config.get("username"),
            password=config.get("password"),
            from_email=config.get("from_email")
        )

    @staticmethod
    def create_sms_adapter(config: Dict[str, Any]) -> SMSNotificationAdapter:
        """Create SMS notification adapter from config"""
        return SMSNotificationAdapter(
            api_key=config.get("api_key"),
            api_url=config.get("api_url"),
            from_number=config.get("from_number")
        )