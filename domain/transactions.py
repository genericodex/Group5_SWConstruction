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
    timestamp: datetime = None  # Default to None instead of datetime.now()
    transaction_id: str = field(init=False)  # Generated after initialization
    source_account_id: str = None
    destination_account_id: str = None

    def __post_init__(self):
        # Set timestamp to current time only if not provided
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.amount <= 0:
            raise ValueError("Transaction amount must be positive")
        # Generate transaction_id based on timestamp
        self.transaction_id = f"txn_{self.timestamp.timestamp()}"
        if isinstance(self.transaction_type, TransferTransactionType):
            if not (self.source_account_id and self.destination_account_id):
                raise ValueError("Transfer requires source and destination accounts")

    def to_dict(self):
        data = {
            "transaction_id": self.transaction_id,
            "type": self.transaction_type.name,
            "amount": self.amount,
            "account_id": self.account_id,
            "timestamp": self.timestamp.isoformat()
        }
        if isinstance(self.transaction_type, TransferTransactionType):
            data["source_account_id"] = self.source_account_id
            data["destination_account_id"] = self.destination_account_id
        return data

    def get_transaction_id(self):
        return self.transaction_id

    def get_amount(self):
        return self.amount

    def get_transaction_type(self):
        return self.transaction_type