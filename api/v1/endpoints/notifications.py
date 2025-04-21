from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from infrastructure.Notifications.notifications import NotificationService
from presentation.api.dependencies import get_notification_service

router = APIRouter()

# Request models
class SubscribeRequest(BaseModel):
    accountId: str
    notifyType: str  # e.g., "email"
class UnsubscribeRequest(BaseModel):
    accountId: str

# Response models
class LogResponse(BaseModel):
    message: str
    timestamp: str

# 1. POST /notifications/subscribe
@router.post("/notifications/subscribe", status_code=200)
async def subscribe(
    request: SubscribeRequest,
    service: NotificationService = Depends(get_notification_service),
):
    try:
        service.subscribe(request.accountId, {"notifyType": request.notifyType})
        return {"message": f"Subscribed account {request.accountId} to notifications via {request.notifyType}"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# 2. POST /notifications/unsubscribe
@router.post("/notifications/unsubscribe", status_code=200)
async def unsubscribe(
    request: UnsubscribeRequest,
    service: NotificationService = Depends(get_notification_service),
):
    try:
        service.unsubscribe(request.accountId)
        return {"message": f"Unsubscribed account {request.accountId} from notifications"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
# 3. GET /logs/transactions
@router.get("/logs/transactions", status_code=200, response_model=List[LogResponse])
async def get_transaction_logs(
    service: NotificationService = Depends(get_notification_service),
):
    logs = service.get_transaction_logs()
    return [{"message": log.message, "timestamp": log.timestamp.isoformat()} for log in logs]

# 4. GET /accounts/{account_id}/logs
@router.get("/accounts/{account_id}/logs", status_code=200, response_model=List[LogResponse])
async def get_account_logs(
    account_id: str,
    service: NotificationService = Depends(get_notification_service),
):
    logs = service.get_account_logs(account_id)
    return [{"message": log.message, "timestamp": log.timestamp.isoformat()} for log in logs]
