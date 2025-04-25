import logging
from typing import Optional, List
from sqlalchemy.orm import Session
from application.repositories.account_repository import IAccountRepository
from domain.accounts import Account, ActiveStatus, ClosedStatus
from domain.checking_account import CheckingAccount, CheckingAccountType
from domain.savings_account import SavingsAccount, SavingsAccountType
from infrastructure.database.models import AccountModel
from infrastructure.database.transaction_manager import TransactionManager

logger = logging.getLogger(__name__)

# Decorator for logging method calls
def log_method(func):
    def wrapper(*args, **kwargs):
        logger.info(f"Calling {func.__name__} with args: {args[1:]}, kwargs: {kwargs}")
        result = func(*args, **kwargs)
        logger.info(f"Completed {func.__name__}, result: {result}")
        return result
    return wrapper

class AccountRepository(IAccountRepository):
    def __init__(self, db: Session):
        self.db = db
        self.transaction_manager = TransactionManager(db)

    @log_method
    def create_account(self, account: Account) -> str:
        # Create new account with proper string values from objects
        db_account = AccountModel(
            account_id=account.account_id,
            account_type=account.account_type.name,  # Use the name property
            username=account.username,
            password_hash=account._password_hash,
            balance=account._balance,
            status=account.status.name,  # Use the name property
            creation_date=account.creation_date
        )
        self.db.add(db_account)
        self.db.commit()
        self.db.refresh(db_account)
        return db_account.account_id

    @log_method
    def get_account_by_id(self, account_id: str) -> Optional[Account]:
        db_account = self.db.query(AccountModel).filter(AccountModel.account_id == account_id).first()
        if not db_account:
            return None

        # Create appropriate account type based on string value
        if db_account.account_type == "CHECKING":
            account = CheckingAccount(
                account_id=db_account.account_id,
                username=db_account.username,
                password=None,  # We'll set the hashed password directly
                initial_balance=db_account.balance
            )
            # Override the hashed password that was created in constructor
            account._password_hash = db_account.password_hash
        else:  # "SAVINGS"
            account = SavingsAccount(
                account_id=db_account.account_id,
                username=db_account.username,
                password=None,  # We'll set the hashed password directly
                initial_balance=db_account.balance
            )
            # Override the hashed password that was created in constructor
            account._password_hash = db_account.password_hash

        # Set status based on string value
        if db_account.status == "ACTIVE":
            account.status = ActiveStatus()
        else:  # "CLOSED"
            account.status = ClosedStatus()

        account.creation_date = db_account.creation_date
        return account

    @log_method
    def update_account(self, account: Account) -> None:
        db_account = self.db.query(AccountModel).filter(AccountModel.account_id == account.account_id).first()
        if not db_account:
            raise ValueError(f"Account with ID {account.account_id} not found")

        db_account.balance = account._balance
        db_account.status = account.status.name  # Use the name property
        self.db.commit()

    @log_method
    def save(self, account: Account) -> str:
        """Save an account (create if new, update if existing)."""
        db_account = self.db.query(AccountModel).filter(AccountModel.account_id == account.account_id).first()
        if db_account:
            # Update existing account
            db_account.balance = account._balance
            db_account.status = account.status.name  # Use the name property
            self.db.commit()
            return db_account.account_id
        else:
            # Create new account
            return self.create_account(account)

    @log_method
    def get_by_id(self, account_id: str) -> Optional[Account]:
        """Retrieve an account by ID (matches abstract method name)."""
        return self.get_account_by_id(account_id)

    @log_method
    def delete(self, account_id: str) -> None:
        """Delete an account by ID."""
        db_account = self.db.query(AccountModel).filter(AccountModel.account_id == account_id).first()
        if db_account:
            self.db.delete(db_account)
            self.db.commit()

    @log_method
    def get_all(self) -> List[Account]:
        """Retrieve all accounts."""
        db_accounts = self.db.query(AccountModel).all()
        accounts = []

        for db_account in db_accounts:
            # Create appropriate account type based on string value
            if db_account.account_type == "CHECKING":
                account = CheckingAccount(
                    account_id=db_account.account_id,
                    username=db_account.username,
                    password=None,
                    initial_balance=db_account.balance
                )
                # Override the hashed password
                account._password_hash = db_account.password_hash
            else:  # "SAVINGS"
                account = SavingsAccount(
                    account_id=db_account.account_id,
                    username=db_account.username,
                    password=None,
                    initial_balance=db_account.balance
                )
                # Override the hashed password
                account._password_hash = db_account.password_hash

            # Set status based on string value
            if db_account.status == "ACTIVE":
                account.status = ActiveStatus()
            else:  # "CLOSED"
                account.status = ClosedStatus()

            account.creation_date = db_account.creation_date
            accounts.append(account)

        return accounts

    @log_method
    def prepare_transfer(self, source_account_id: str, destination_account_id: str, amount: float) -> bool:
        """Check balances and handle concurrency for a transfer."""
        source_account = self.get_by_id(source_account_id)
        destination_account = self.get_by_id(destination_account_id)

        if not source_account or not destination_account:
            logger.error(f"Source or destination account not found: {source_account_id}, {destination_account_id}")
            raise ValueError("Source or destination account not found")

        if source_account.status.name != "ACTIVE" or destination_account.status.name != "ACTIVE":
            logger.error(f"One or both accounts are not active: {source_account_id}, {destination_account_id}")
            raise ValueError("One or both accounts are not active")

        if source_account._balance < amount:
            logger.error(f"Insufficient funds in source account {source_account_id}: balance={source_account._balance}, amount={amount}")
            raise ValueError("Insufficient funds in source account")

        return True

    @log_method
    def update_accounts_for_transfer(self, source_account: Account, destination_account: Account, amount: float) -> None:
        """Atomically update source and destination accounts for a transfer."""
        with self.transaction_manager.transaction():
            source_account._balance -= amount
            destination_account._balance += amount
            self.update_account(source_account)
            self.update_account(destination_account)