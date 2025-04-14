# accounts.py (with fixes for status codes and consistent error messages)
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from application.services.account_creation_service import AccountCreationService
from application.services.transaction_service import TransactionService
from infrastructure.repositories.account_repository import AccountRepository
from infrastructure.repositories.transaction_repository import TransactionRepository
from api.dependencies import (
    get_account_creation_service,
    get_transaction_service,
    get_account_repository,
    get_transaction_repository,
)

router = APIRouter()

class CreateAccountRequest(BaseModel):
    accountType: str
    initialDeposit: float

class DepositRequest(BaseModel):
    amount: float

class WithdrawRequest(BaseModel):
    amount: float

class AccountResponse(BaseModel):
    account_id: str
    balance: float
    availableBalance: float

class TransactionResponse(BaseModel):
    transaction_id: str
    transaction_type: str
    amount: float
    account_id: str
    timestamp: str

@router.post("/accounts", status_code=201)
async def create_account(
    request: CreateAccountRequest,
    service: AccountCreationService = Depends(get_account_creation_service),
):
    if request.initialDeposit < 0:
        raise HTTPException(status_code=400, detail="Initial deposit must be non-negative.")

    account_type = request.accountType.lower()
    if account_type not in ["checking", "savings"]:
        raise HTTPException(status_code=400, detail="Invalid account type. Must be 'checking' or 'savings'.")

    try:
        account_id = service.create_account(account_type, request.initialDeposit)
        return {"account_id": account_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/accounts/{accountId}/deposit", status_code=200)
async def deposit(
    accountId: str,
    request: DepositRequest,
    service: TransactionService = Depends(get_transaction_service),
    account_repo: AccountRepository = Depends(get_account_repository),
):
    if request.amount <= 0:
        raise HTTPException(status_code=400, detail="Deposit amount must be positive.")

    try:
        transaction = service.deposit(accountId, request.amount)
        account = account_repo.get_account_by_id(accountId)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found after deposit.")
        return {"balance": account.balance}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/accounts/{accountId}/withdraw", status_code=200)
async def withdraw(
    accountId: str,
    request: WithdrawRequest,
    service: TransactionService = Depends(get_transaction_service),
    account_repo: AccountRepository = Depends(get_account_repository),
):
    if request.amount <= 0:
        raise HTTPException(status_code=400, detail="Withdrawal amount must be positive.")

    try:
        transaction = service.withdraw(accountId, request.amount)
        account = account_repo.get_account_by_id(accountId)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found after withdrawal.")
        return {"balance": account.balance}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/accounts/{accountId}/balance", status_code=200, response_model=AccountResponse)
async def get_balance(
    accountId: str,
    repo: AccountRepository = Depends(get_account_repository),
):
    account = repo.get_account_by_id(accountId)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found.")

    return {
        "account_id": account.account_id,
        "balance": account.balance,
        "availableBalance": account.balance,
    }

@router.get("/accounts/{accountId}/transactions", status_code=200, response_model=List[TransactionResponse])
async def get_transactions(
    accountId: str,
    repo: TransactionRepository = Depends(get_transaction_repository),
):
    transactions = repo.get_by_account_id(accountId)

    return [
        {
            "transaction_id": tx.transaction_id,
            "transaction_type": tx.transaction_type.name,
            "amount": tx.amount,
            "account_id": tx.account_id,
            "timestamp": tx.timestamp.isoformat(),
        }
        for tx in transactions
    ]