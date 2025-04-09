from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto


class TransactionType(Enum):
    DEPOSIT = auto()
    WITHDRAW = auto()




@dataclass
class Transaction:
    transaction_id: str
    transaction_type: TransactionType
    amount: float
    timestamp: datetime
    account_id: str