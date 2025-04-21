from typing import Optional, List
from sqlalchemy.orm import Session
from application.repositories.account_repository import IAccountRepository
from domain.accounts import Account, AccountType
from domain.checking_account import CheckingAccount
from domain.savings_account import SavingsAccount
from infrastructure.database.models import AccountModel

class AccountRepository(IAccountRepository):
    def __init__(self, db: Session):
        self.db = db

    def create_account(self, account: Account) -> str:
        # Existing implementation
        db_account = AccountModel(
            account_id=account.account_id,
            account_type=account.account_type,
            balance=account.balance,
            status=account.status,
            creation_date=account.creation_date
        )
        self.db.add(db_account)
        self.db.commit()
        self.db.refresh(db_account)
        return db_account.account_id

    def get_account_by_id(self, account_id: str) -> Optional[Account]:
        # Existing implementation
        db_account = self.db.query(AccountModel).filter(AccountModel.account_id == account_id).first()
        if not db_account:
            return None
        if db_account.account_type == AccountType.CHECKING:
            account = CheckingAccount(account_id=db_account.account_id, initial_balance=db_account.balance)
        else:  # AccountType.SAVINGS
            account = SavingsAccount(account_id=db_account.account_id, initial_balance=db_account.balance)
        account.status = db_account.status
        account.creation_date = db_account.creation_date
        return account

    def update_account(self, account: Account) -> None:
        # Existing implementation
        db_account = self.db.query(AccountModel).filter(AccountModel.account_id == account.account_id).first()
        if not db_account:
            raise ValueError(f"Account with ID {account.account_id} not found")
        db_account.balance = account.balance
        db_account.status = account.status
        self.db.commit()

    # New implementations for abstract methods
    def save(self, account: Account) -> str:
        """Save an account (create if new, update if existing)."""
        db_account = self.db.query(AccountModel).filter(AccountModel.account_id == account.account_id).first()
        if db_account:
            # Update existing account
            db_account.balance = account.balance
            db_account.status = account.status
            self.db.commit()
            return db_account.account_id
        else:
            # Create new account
            return self.create_account(account)

    def get_by_id(self, account_id: str) -> Optional[Account]:
        """Retrieve an account by ID (matches abstract method name)."""
        return self.get_account_by_id(account_id)

    def delete(self, account_id: str) -> None:
        """Delete an account by ID."""
        db_account = self.db.query(AccountModel).filter(AccountModel.account_id == account_id).first()
        if db_account:
            self.db.delete(db_account)
            self.db.commit()

    def get_all(self) -> List[Account]:
        """Retrieve all accounts."""
        db_accounts = self.db.query(AccountModel).all()
        accounts = []
        for db_account in db_accounts:
            if db_account.account_type == AccountType.CHECKING:
                account = CheckingAccount(account_id=db_account.account_id, initial_balance=db_account.balance)
            else:  # AccountType.SAVINGS
                account = SavingsAccount(account_id=db_account.account_id, initial_balance=db_account.balance)
            account.status = db_account.status
            account.creation_date = db_account.creation_date
            accounts.append(account)
        return accounts