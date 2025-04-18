# infrastructure/console_notification_service.py
from application.services.notification_service import INotificationService


class NotificationService(INotificationService):
    def notify(self, message: str) -> None:
        """Prints the notification message to the console."""
        print(f"NOTIFICATION: {message}")
