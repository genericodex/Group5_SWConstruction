from abc import ABC, abstractmethod
from typing import List, Optional
from domain.transactions import Transaction


class ITransactionRepository(ABC):
    @abstractmethod
    def save(self, transaction: Transaction) -> None:
        """Save a transaction to the repository"""
        pass

    @abstractmethod
    def find_by_id(self, transaction_id: str) -> Optional[Transaction]:
        """Find a transaction by its ID"""
        pass

    @abstractmethod
    def find_by_account_id(self, account_id: str) -> List[Transaction]:
        """Find all transactions for a specific account"""
        pass

    @abstractmethod
    def find_all(self) -> List[Transaction]:
        """Find all transactions"""
        pass


# class InMemoryTransactionRepository(TransactionRepository):
#     def __init__(self):
#         self._transactions: Dict[str, Transaction] = {}
#
#     def save(self, transaction: Transaction) -> None:
#         self._transactions[transaction.transaction_id] = transaction
#
#     def get_by_id(self, transaction_id: str) -> Transaction:
#         transaction = self._transactions.get(transaction_id)
#         if not transaction:
#             raise ValueError(f"Transaction with ID '{transaction_id}' not found.")
#         return transaction
#
#     def get_by_account_id(self, account_id: str) -> List[Transaction]:
#         return [
#             txn for txn in self._transactions.values()
#             if txn.account_id == account_id
#         ]
#
#     def get_all(self) -> List[Transaction]:
#         return list(self._transactions.values())
