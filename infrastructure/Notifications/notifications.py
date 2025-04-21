from application.services.notification_service import INotificationService
from fastapi import APIRouter, HTTPException

router = APIRouter()


# Example NotificationService (to demonstrate functionality)
class NotificationService(INotificationService):
    def notify(self, message: str):
        print(f"Notification sent: {message}")


@router.get("/notifications/{notification_id}")
async def get_notification(notification_id: int):
    """
    Example API to fetch a specific notification by ID.
    """
    # Example handling (replace this with your actual implementation)
    if notification_id == 1:
        return {"notification_id": notification_id, "message": "Welcome to the system!"}
    raise HTTPException(status_code=404, detail="Notification not found")
