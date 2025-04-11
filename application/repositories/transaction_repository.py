from abc import ABC, abstractmethod
from typing import List, Dict
from domain.transactions import Transaction


class ITransactionRepository(ABC):
    @abstractmethod
    def save(self, transaction: Transaction) -> None:
        """Save a transaction."""
        pass

    @abstractmethod
    def get_by_id(self, transaction_id: str) -> Transaction:
        """Retrieve a transaction by its ID."""
        pass

    @abstractmethod
    def get_by_account_id(self, account_id: str) -> List[Transaction]:
        """Retrieve all transactions for a specific account."""
        pass

    @abstractmethod
    def get_all(self) -> List[Transaction]:
        """Retrieve all transactions."""
        pass



