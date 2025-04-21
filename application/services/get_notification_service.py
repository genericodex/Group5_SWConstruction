from fastapi import Depends
from infrastructure.Notifications.notifications import NotificationService


def get_notification_service() -> NotificationService:
    """
    Dependency to provide an instance of NotificationService.
    """
    # Create and return the notification service instance
    return NotificationService()
