from abc import ABC, abstractmethod
from typing import List
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

    @abstractmethod
    def get_usage(self, account_id: str) -> dict[str, float]:
        """Retrieve daily and monthly transaction usage for the given account."""
        pass

    @abstractmethod
    def reset_usage(self, account_id: str, period: str) -> None:
        """Reset transaction usage for the specified period ('daily' or 'monthly')."""
        pass



