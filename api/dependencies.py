from fastapi import Depends
from sqlalchemy.orm import Session

from Group5_SWConstruction.application.repositories.accountConstraint_repository import IAccountConstraintsRepository
from Group5_SWConstruction.application.services.account_service import AccountCreationService
from Group5_SWConstruction.application.services.fund_transfer import FundTransferService
from Group5_SWConstruction.application.services.interest_service import InterestService
from Group5_SWConstruction.application.services.limit_enforcement_service import LimitEnforcementService
from Group5_SWConstruction.application.services.logging_service import LoggingService
from Group5_SWConstruction.application.services.notification_service import NotificationService
from Group5_SWConstruction.application.services.statement_service import StatementService
from Group5_SWConstruction.application.services.transaction_service import TransactionService
from Group5_SWConstruction.infrastructure.adapters.notification_adapters import NotificationFactory
from Group5_SWConstruction.infrastructure.adapters.statement_adapter import IStatementGenerator
from Group5_SWConstruction.infrastructure.database.db import get_db
from Group5_SWConstruction.infrastructure.repositories.account_repository import AccountRepository
from Group5_SWConstruction.infrastructure.repositories.interest_repository import InterestRepository
from Group5_SWConstruction.infrastructure.repositories.transaction_repository import TransactionRepository


# Dependency to get the database session
def get_db_session() -> Session:
    db = next(get_db())
    try:
        yield db
    finally:
        db.close()


# Dependency to get the LoggingService
def get_logging_service() -> LoggingService:
    return LoggingService(app_name="BankingSystemAPI")


# Dependency to get the NotificationService
def get_notification_service(logging_service: LoggingService = Depends(get_logging_service)) -> NotificationService:
    # Create notification adapters from configuration
    email_config = {
        "smtp_server": "smtp.example.com",
        "smtp_port": 587,
        "username": "banking@example.com",
        "password": "password",
        "from_email": "adapters@banking.example.com"
    }

    sms_config = {
        "api_key": "api_key_here",
        "api_url": "https://sms-provider.example.com/api/send",
        "from_number": "+15551234567"
    }

    email_adapter = NotificationFactory.create_email_adapter(email_config)
    sms_adapter = NotificationFactory.create_sms_adapter(sms_config)

    return NotificationService(
        email_adapter=email_adapter,
        sms_adapter=sms_adapter,
        logging_service=logging_service
    )


# Dependency to get the AccountCreationService
def get_account_creation_service(
        db: Session = Depends(get_db_session),
        notification_service: NotificationService = Depends(get_notification_service),
        logging_service: LoggingService = Depends(get_logging_service)
) -> AccountCreationService:
    account_repo = AccountRepository(db)
    return AccountCreationService(
        account_repository=account_repo,
        notification_service=notification_service,
        logging_service=logging_service
    )


# Dependency to get the TransactionService
def get_transaction_service(
        db: Session = Depends(get_db_session),
        notification_service: NotificationService = Depends(get_notification_service),
        logging_service: LoggingService = Depends(get_logging_service)
) -> TransactionService:
    account_repo = AccountRepository(db)
    transaction_repo = TransactionRepository(db, logging_service)
    return TransactionService(
        transaction_repository=transaction_repo,
        account_repository=account_repo,
        notification_service=notification_service,
        logging_service=logging_service
    )


# Dependency to get the FundTransferService
def get_fund_transfer_service(
        db: Session = Depends(get_db_session),
        notification_service: NotificationService = Depends(get_notification_service),
        logging_service: LoggingService = Depends(get_logging_service)
) -> FundTransferService:
    account_repo = AccountRepository(db)
    transaction_repo = TransactionRepository(db, logging_service)
    return FundTransferService(
        account_repository=account_repo,
        transaction_repository=transaction_repo,
        notification_service=notification_service,
        logging_service=logging_service
    )


# Dependency to get the AccountRepository (for queries like balance)
def get_account_repository(db: Session = Depends(get_db_session)) -> AccountRepository:
    return AccountRepository(db)


# Dependency to get the TransactionRepository (for transaction history)
def get_transaction_repository(
        db: Session = Depends(get_db_session),
        logging_service: LoggingService = Depends(get_logging_service)
) -> TransactionRepository:
    return TransactionRepository(db, logging_service)

# Dependency to get the InterestService
def get_interest_service(
    db: Session = Depends(get_db_session),
    logging_service: LoggingService = Depends(get_logging_service)
) -> InterestService:
    account_repo = AccountRepository(db)
    interest_repo = InterestRepository(None)
    return InterestService(account_repo, interest_repo, logging_service)

# Dependency to get the LimitEnforcementService
def get_limit_enforcement_service(
    db: Session = Depends(get_db_session),
    logging_service: LoggingService = Depends(get_logging_service)
) -> LimitEnforcementService:
    constraints_repo = IAccountConstraintsRepository()
    return LimitEnforcementService(constraints_repo, logging_service)

# Dependency to get the StatementService
def get_statement_service(
    db: Session = Depends(get_db_session),
    logging_service: LoggingService = Depends(get_logging_service)
) -> StatementService:
    account_repo = AccountRepository(db)
    transaction_repo = TransactionRepository(db, logging_service)
    generator = IStatementGenerator()
    return StatementService(transaction_repo, account_repo, generator)
