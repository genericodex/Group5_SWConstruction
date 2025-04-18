# application/notification_service.py
from abc import ABC, abstractmethod


class INotificationService(ABC):
    @abstractmethod
    def notify(self, message: str) -> None:
        """Send a notification with the given message."""
        pass
