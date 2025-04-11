from uuid import uuid4
from typing import Protocol
from Domain.BankingDomainLayer import Account, CheckingAccount, SavingsAccount, Transaction, TransactionType
from datetime import datetime
from typing import List, Optional

class AccountRepository(Protocol):
    def create_account(self, account: Account) -> str:
        ...
    
    def get_account_by_id(self, account_id: str) -> Optional[Account]:
        ...
    
    def update_account(self, account: Account) -> None:
        ...

class TransactionRepository(Protocol):
    def save_transaction(self, transaction: Transaction) -> str:
        ...
    
    def get_transactions_for_account(self, account_id: str) -> List[Transaction]:
        ...

class AccountCreationService:
    def __init__(self, account_repository: AccountRepository):
        self.account_repository = account_repository
    
    def create_account(self, account_type: str, initial_deposit: float = 0.0) -> str:
        account_id = str(uuid4())
        
        if account_type == "CHECKING":
            account = CheckingAccount(account_id, initial_deposit)
        elif account_type == "SAVINGS":
            if initial_deposit < SavingsAccount.MINIMUM_BALANCE:
                raise ValueError(f"Savings account requires minimum deposit of {SavingsAccount.MINIMUM_BALANCE}")
            account = SavingsAccount(account_id, initial_deposit)
        else:
            raise ValueError(f"Unknown account type: {account_type}")
        
        return self.account_repository.create_account(account)

class TransactionService:
    def __init__(self, account_repository: AccountRepository, transaction_repository: TransactionRepository):
        self.account_repository = account_repository
        self.transaction_repository = transaction_repository
    
    def deposit(self, account_id: str, amount: float) -> Transaction:
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        
        account = self.account_repository.get_account_by_id(account_id)
        if not account:
            raise ValueError("Account not found")
        
        account.balance += amount
        self.account_repository.update_account(account)
        
        transaction = Transaction(
            transaction_id=str(uuid4()),
            transaction_type=TransactionType.DEPOSIT,
            amount=amount,
            timestamp=datetime.now(),
            account_id=account_id
        )
        
        self.transaction_repository.save_transaction(transaction)
        return transaction
    
    def withdraw(self, account_id: str, amount: float) -> Transaction:
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        
        account = self.account_repository.get_account_by_id(account_id)
        if not account:
            raise ValueError("Account not found")
        
        if not account.can_withdraw(amount):
            raise ValueError("Withdrawal not allowed based on account rules")
        
        account.balance -= amount
        self.account_repository.update_account(account)
        
        transaction = Transaction(
            transaction_id=str(uuid4()),
            transaction_type=TransactionType.WITHDRAW,
            amount=amount,
            timestamp=datetime.now(),
            account_id=account_id
        )
        
        self.transaction_repository.save_transaction(transaction)
        return transaction