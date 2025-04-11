
from typing import Optional
from sqlalchemy.orm import Session
from application.repositories.account_repository import IAccountRepository
from domain.accounts import Account, CheckingAccount, SavingsAccount, AccountType
from infrastructure.database.models import AccountModel


class AccountRepository(IAccountRepository):
    def __init__(self, db: Session):
        self.db = db

    def create_account(self, account: Account) -> str:
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
        db_account = self.db.query(AccountModel).filter(AccountModel.account_id == account_id).first()
        if not db_account:
            return None

        # Map the database model back to the domain model
        if db_account.account_type == AccountType.CHECKING:
            account = CheckingAccount(account_id=db_account.account_id, initial_balance=db_account.balance)
        else:  # AccountType.SAVINGS
            account = SavingsAccount(account_id=db_account.account_id, initial_balance=db_account.balance)

        # Set additional fields
        account.status = db_account.status
        account.creation_date = db_account.creation_date
        return account

    def update_account(self, account: Account) -> None:
        db_account = self.db.query(AccountModel).filter(AccountModel.account_id == account.account_id).first()
        if not db_account:
            raise ValueError(f"Account with ID {account.account_id} not found")

        db_account.balance = account.balance
        db_account.status = account.status
        self.db.commit()