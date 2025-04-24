from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Callable
from domain.transactions import (
    Transaction, 
    DepositTransactionType, WithdrawTransactionType, TransferTransactionType
)
from hashlib import sha256
from fastapi import APIRouter

router = APIRouter()


class AccountStatus(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

class ActiveStatus(AccountStatus):
    @property
    def name(self) -> str:
        return "ACTIVE"

class ClosedStatus(AccountStatus):
    @property
    def name(self) -> str:
        return "CLOSED"

class AccountType(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

@dataclass
class Account(ABC):
    account_id: str
    account_type: AccountType
    username: str
    _password_hash: str  # Stores the hashed version of the password
    _balance: float = 0.0
    status: AccountStatus = field(default_factory=ActiveStatus)
    creation_date: datetime = field(default_factory=datetime.now)
    _transactions: List[Transaction] = field(default_factory=list, init=False)
    _observers: List[Callable] = field(default_factory=list, init=False)



    def hash_password(self, password: str) -> None:
        """Hashes and sets the password for the account."""
        if password is not None:
            self._password_hash = sha256(password.encode()).hexdigest()

    def verify_password(self, password: str) -> bool:
        """Verifies whether a given password matches the stored hashed password."""
        return self._password_hash == sha256(password.encode()).hexdigest()

    def balance(self) -> float:
        return self._balance

    def update_balance(self, amount: float) -> None:
        self._balance += amount

    def get_balance(self) -> float:
        return self._balance

    @abstractmethod
    def can_withdraw(self, amount: float) -> bool:
        pass

    def deposit(self, amount: float) -> Transaction:
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")

        self.update_balance(amount)
        transaction = Transaction(
            transaction_type=DepositTransactionType(),
            amount=amount,
            account_id=self.account_id
        )
        self._transactions.append(transaction)
        self.notify_observers(transaction)
        return transaction

    def withdraw(self, amount: float) -> Transaction:
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")

        if not self.can_withdraw(amount):
            raise ValueError("Withdrawal amount exceeds available balance")

        self.update_balance(-amount)
        transaction = Transaction(
            transaction_type=WithdrawTransactionType(),
            amount=amount,
            account_id=self.account_id
        )
        self._transactions.append(transaction)
        self.notify_observers(transaction)
        return transaction

    def transfer(self, amount: float, destination_account: 'Account') -> Transaction:
        if amount <= 0:
            raise ValueError("Transfer amount must be positive")
        
        if not self.can_withdraw(amount):
            raise ValueError("Insufficient funds for transfer")
            
        self.update_balance(-amount)
        destination_account.update_balance(amount)
        
        transaction = Transaction(
            transaction_type=TransferTransactionType(),
            amount=amount,
            account_id=self.account_id,
            source_account_id=self.account_id,
            destination_account_id=destination_account.account_id
        )
        
        self._transactions.append(transaction)
        destination_account._transactions.append(transaction)
        self.notify_observers(transaction)
        return transaction

    def add_observer(self, observer: Callable) -> None:
        self._observers.append(observer)

    def notify_observers(self, transaction: Transaction) -> None:
        for observer in self._observers:
            observer(transaction)

    def get_transactions(self) -> List[Transaction]:
        return self._transactions.copy()

@router.get("/accounts")
def get_accounts():
    """
    Endpoint to get a list of accounts (mock data for now).
    """
    return {"message": "List of accounts"}
