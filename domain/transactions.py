from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto


class TransactionType(Enum):
    DEPOSIT = auto()
    WITHDRAW = auto()


@dataclass
class Transaction:
    transaction_type: TransactionType
    amount: float
    account_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    transaction_id: str = field(init=False)

    def __post_init__(self):
        if self.amount <= 0:
            raise ValueError("Transaction amount must be positive")
        self.transaction_id = f"txn_{self.timestamp.timestamp()}"

    def get_transaction_id(self) -> str:
        return self.transaction_id

    def get_amount(self) -> float:
        return self.amount

    def get_transaction_type(self) -> TransactionType:
        return self.transaction_type

    def __repr__(self):
        return (f"Transaction(transaction_id={self.transaction_id}, "
                f"type={self.transaction_type.name}, "
                f"amount={self.amount}, "
                f"account_id={self.account_id}, "
                f"timestamp={self.timestamp})")

    def to_dict(self):
        return {
            "transaction_id": self.transaction_id,
            "type": self.transaction_type.name,
            "amount": self.amount,
            "account_id": self.account_id,
            "timestamp": self.timestamp.isoformat()
        }
