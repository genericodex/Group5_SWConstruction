from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from typing import List, Optional

class AccountStatus(Enum):
    ACTIVE = auto()
    CLOSED = auto()

class TransactionType(Enum):
    DEPOSIT = auto()
    WITHDRAW = auto()

@dataclass
class Account(ABC):
    account_id: str
    account_type: str
    balance: float
    status: AccountStatus
    creation_date: datetime
    
    @abstractmethod
    def can_withdraw(self, amount: float) -> bool:
        pass

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

@dataclass
class Transaction:
    transaction_id: str
    transaction_type: TransactionType
    amount: float
    timestamp: datetime
    account_id: str