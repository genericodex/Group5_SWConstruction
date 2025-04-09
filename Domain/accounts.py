from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import List
from Group5_SWConstruction.Domain.transactions import Transaction, TransactionType


class AccountStatus(Enum):
    ACTIVE = auto()
    CLOSED = auto()

@dataclass
class Account(ABC):
    account_id: str
    _balance: float = 0.0
    status: AccountStatus = AccountStatus.ACTIVE
    creation_date: datetime = field(default_factory=datetime.now)
    _transactions: List[Transaction] = field(default_factory=list, init=False)

    @property
    def balance(self) -> float:
        return self._balance

    @abstractmethod
    def can_withdraw(self, amount: float) -> bool:
        pass

    def deposit(self, amount: float) -> Transaction:
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        
        self._balance += amount
        transaction = Transaction(
            transaction_type=TransactionType.DEPOSIT,
            amount=amount,
            account_id=self.account_id
        )
        self._transactions.append(transaction)
        return transaction

    def withdraw(self, amount: float) -> Transaction:
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        
        if not self.can_withdraw(amount):
            raise ValueError("Withdrawal amount exceeds available balance")
        
        self._balance -= amount
        transaction = Transaction(
            transaction_type=TransactionType.WITHDRAW,
            amount=amount,
            account_id=self.account_id
        )
        self._transactions.append(transaction)
        return transaction

    def get_transactions(self) -> List[Transaction]:
        return self._transactions.copy()


@dataclass
class CheckingAccount(Account):
    def __init__(self, account_id: str, initial_balance: float = 0.0):
        super().__init__(
            account_id=account_id,
            account_type="CHECKING",
            balance=initial_balance,
            status=AccountStatus.ACTIVE,
            creation_date=datetime.now()
        )
    
    def can_withdraw(self, amount: float) -> bool:
        return self.balance >= amount
    
    def __repr__(self):
        return (f"CheckingAccount(account_id={self.account_id}, "
                f"balance={self.balance}, status={self.status}, "
                f"creation_date={self.creation_date})")

@dataclass
class SavingsAccount(Account):
    MINIMUM_BALANCE = 100.00
    
    def __init__(self, account_id: str, initial_balance: float = 0.0):
        super().__init__(
            account_id=account_id,
            account_type="SAVINGS",
            balance=initial_balance,
            status=AccountStatus.ACTIVE,
            creation_date=datetime.now()
        )
    
    def can_withdraw(self, amount: float) -> bool:
        return (self.balance - amount) >= self.MINIMUM_BALANCE
    
    def __repr__(self):
        return (f"SavingsAccount(account_id={self.account_id}, "
                f"balance={self.balance}, status={self.status}, "
                f"creation_date={self.creation_date})")