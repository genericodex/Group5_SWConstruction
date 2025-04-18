from fastapi import Depends
from sqlalchemy.orm import Session
from infrastructure.database.db import get_db
from application.services.account_creation_service import AccountCreationService
from application.services.transaction_service import TransactionService
from infrastructure.repositories.account_repository import AccountRepository
from infrastructure.repositories.transaction_repository import TransactionRepository

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

# Dependency to get the AccountRepository (for queries like balance)
def get_account_repository(db: Session = Depends(get_db_session)) -> AccountRepository:
    return AccountRepository(db)

# Dependency to get the TransactionRepository (for transaction history)
def get_transaction_repository(db: Session = Depends(get_db_session)) -> TransactionRepository:
    return TransactionRepository(db)