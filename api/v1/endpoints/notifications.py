from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional

from application.services.notification_service import NotificationService
from infrastructure.database.db import get_db
from infrastructure.repositories.account_repository import AccountRepository
from api.dependencies import (
    get_notification_service,
    get_account_repository,
    get_logging_service,
)

router = APIRouter()


# Request Models
class NotificationSubscriptionRequest(BaseModel):
    accountId: str
    notifyType: str  # "email" or "sms"
    contactInfo: str  # email address or phone number


@router.post("/adapters/subscribe", status_code=200)
async def subscribe_to_notifications(
        request: NotificationSubscriptionRequest,
        notification_service: NotificationService = Depends(get_notification_service),
        account_repo: AccountRepository = Depends(get_account_repository),
        logging_service=Depends(get_logging_service)
):
    account = account_repo.get_account_by_id(request.accountId)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found.")

    # Determine account tier based on notification type
    if request.notifyType.lower() == "email":
        account_tier = "standard"
    elif request.notifyType.lower() == "sms":
        account_tier = "premium"
    else:
        raise HTTPException(status_code=400, detail="Invalid notification type. Must be 'email' or 'sms'.")

    try:
        # Update account with contact info
        if request.notifyType.lower() == "email":
            account.email = request.contactInfo
        else:  # SMS
            account.phone = request.contactInfo

        # Register for adapters based on tier
        notification_service.register_account_observers(account, account_tier)

        # Update account in repository
        account_repo.save(account)

        logging_service.info(
            f"Account {request.accountId} subscribed to {request.notifyType} adapters",
            {"account_id": request.accountId, "notify_type": request.notifyType}
        )

        return {"status": "success", "message": f"Successfully subscribed to {request.notifyType} adapters"}
    except Exception as e:
        logging_service.error(
            f"Failed to subscribe to adapters: {str(e)}",
            {"account_id": request.accountId, "notify_type": request.notifyType}
        )
        raise HTTPException(status_code=500, detail=f"Failed to subscribe to adapters: {str(e)}")


@router.post("/adapters/unsubscribe", status_code=200)
async def unsubscribe_from_notifications(
        request: NotificationSubscriptionRequest,
        notification_service: NotificationService = Depends(get_notification_service),
        account_repo: AccountRepository = Depends(get_account_repository),
        logging_service=Depends(get_logging_service)
):
    account = account_repo.get_account_by_id(request.accountId)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found.")

    # Validate notifyType before entering try block
    if request.notifyType.lower() not in ["email", "sms"]:
        raise HTTPException(status_code=400, detail="Invalid notification type. Must be 'email' or 'sms'.")

    try:
        # Reset the contact info
        if request.notifyType.lower() == "email":
            account.email = None
        else:  # SMS
            account.phone = None

        # Re-register with default tier (which has minimal adapters)
        notification_service.register_account_observers(account, "default")

        # Update account in repository
        account_repo.save(account)

        logging_service.info(
            f"Account {request.accountId} unsubscribed from {request.notifyType} adapters",
            {"account_id": request.accountId, "notify_type": request.notifyType}
        )

        return {"status": "success", "message": f"Successfully unsubscribed from {request.notifyType} adapters"}
    except Exception as e:
        logging_service.error(
            f"Failed to unsubscribe from adapters: {str(e)}",
            {"account_id": request.accountId, "notify_type": request.notifyType}
        )
        raise HTTPException(status_code=500, detail=f"Failed to unsubscribe from adapters: {str(e)}")