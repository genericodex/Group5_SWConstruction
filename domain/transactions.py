from dataclasses import dataclass, field
from datetime import datetime
from abc import ABC, abstractmethod

class TransactionType(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

class DepositTransactionType(TransactionType):
    @property
    def name(self) -> str:
        return "DEPOSIT"

class WithdrawTransactionType(TransactionType):
    @property
    def name(self) -> str:
        return "WITHDRAW"

class TransferTransactionType(TransactionType):
    @property
    def name(self) -> str:
        return "TRANSFER"

@dataclass
class Transaction:
    transaction_type: TransactionType
    amount: float
    account_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    transaction_id: str = field(init=False)
    source_account_id: str = None
    destination_account_id: str = None

    def __post_init__(self):
        if self.amount <= 0:
            raise ValueError("Transaction amount must be positive")
        self.transaction_id = f"txn_{self.timestamp.timestamp()}"
        if isinstance(self.transaction_type, TransferTransactionType):
            if not (self.source_account_id and self.destination_account_id):
                raise ValueError("Transfer requires source and destination accounts")

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
        data = {
            "transaction_id": self.transaction_id,
            "type": self.transaction_type.name,
            "amount": self.amount,
            "account_id": self.account_id,
            "timestamp": self.timestamp.isoformat()
        }
        if isinstance(self.transaction_type, TransferTransactionType):
            data.update({
                "source_account_id": self.source_account_id,
                "destination_account_id": self.destination_account_id
            })
        return data
