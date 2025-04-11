from abc import ABC, abstractmethod
from typing import List, Dict
from domain.transactions import Transaction


class TransactionRepository(ABC):
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


class InMemoryTransactionRepository(TransactionRepository):
    def __init__(self):
        self._transactions: Dict[str, Transaction] = {}

    def save(self, transaction: Transaction) -> None:
        self._transactions[transaction.transaction_id] = transaction

    def get_by_id(self, transaction_id: str) -> Transaction:
        transaction = self._transactions.get(transaction_id)
        if not transaction:
            raise ValueError(f"Transaction with ID '{transaction_id}' not found.")
        return transaction

    def get_by_account_id(self, account_id: str) -> List[Transaction]:
        return [
            txn for txn in self._transactions.values()
            if txn.account_id == account_id
        ]

    def get_all(self) -> List[Transaction]:
        return list(self._transactions.values())

