from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from Group5_SWConstruction.application.services.account_creation_service import AccountCreationService
from Group5_SWConstruction.application.services.transaction_service import TransactionService

router = APIRouter()

# ======= Request Models =======
class CreateAccountRequest(BaseModel):
    accountType: str
    initialDeposit: float = 0.0

class AmountRequest(BaseModel):
    amount: float

# ======= Endpoints =======
@router.post("/accounts", status_code=201)
def create_account(req: CreateAccountRequest):
    try:
        account_id = AccountCreationService().create_account(req.accountType, req.initialDeposit)
        return {"accountId": account_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
