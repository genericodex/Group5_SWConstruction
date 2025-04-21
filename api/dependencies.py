from fastapi import Depends
from sqlalchemy.orm import Session
from infrastructure.database.db import get_db
from application.services.account_creation_service import AccountCreationService
from application.services.transaction_service import TransactionService
from application.services.fund_transfer_service import FundTransferService
from infrastructure.database.account_repository import AccountRepository
from infrastructure.database.transaction_repository import TransactionRepository
from infrastructure.Notifications.notifications import NotificationService

# Global instance of NotificationService (set in main.py)
notification_service: NotificationService = None

# Dependency to get the database session
def get_db_session() -> Session:
    db = next(get_db())
    try:
        yield db
    finally:
        db.close()

# Dependency to get the AccountCreationService
def get_account_creation_service(db: Session = Depends(get_db_session)) -> AccountCreationService:
    account_repo = AccountRepository(db)
    return AccountCreationService(account_repo)

# Dependency to get the TransactionService
def get_transaction_service(db: Session = Depends(get_db_session)) -> TransactionService:
    account_repo = AccountRepository(db)
    transaction_repo = TransactionRepository(db)
    return TransactionService(transaction_repo, account_repo)

# Dependency to get the FundTransferService
def get_fund_transfer_service(db: Session = Depends(get_db_session)) -> FundTransferService:
    account_repo = AccountRepository(db)
    transaction_repo = TransactionRepository(db)
    return FundTransferService(account_repo, transaction_repo)

# Dependency to get the NotificationService
def get_notification_service() -> NotificationService:
    if notification_service is None:
        raise HTTPException(status_code=500, detail="NotificationService not initialized")
    return notification_service

# Dependency to get the AccountRepository (for queries like balance)
def get_account_repository(db: Session = Depends(get_db_session)) -> AccountRepository:
    return AccountRepository(db)

# Dependency to get the TransactionRepository (for transaction history)
def get_transaction_repository(db: Session = Depends(get_db_session)) -> TransactionRepository:
    return TransactionRepository(db)
