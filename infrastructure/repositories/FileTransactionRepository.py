from typing import List, Optional, Dict
import json
import os
from domain.transactions import Transaction, TransactionType
from application.repositories.transaction_repository import ITransactionRepository
from datetime import datetime


class FileTransactionRepository(ITransactionRepository):
    def __init__(self, storage_dir: str = "data/transactions"):
        self.storage_dir = storage_dir
        # Create directory if it doesn't exist
        os.makedirs(storage_dir, exist_ok=True)

        # Create index directory for account lookups
        self.index_dir = os.path.join(storage_dir, "index")
        os.makedirs(self.index_dir, exist_ok=True)

    def _get_file_path(self, transaction_id: str) -> str:
        """Get the file path for a transaction"""
        return os.path.join(self.storage_dir, f"{transaction_id}.json")

    def _get_account_index_path(self, account_id: str) -> str:
        """Get the file path for account transaction index"""
        return os.path.join(self.index_dir, f"{account_id}.json")

    def _serialize_transaction(self, transaction: Transaction) -> Dict:
        """Convert Transaction object to dictionary for JSON serialization"""
        return {
            "transaction_id": transaction.transaction_id,
            "transaction_type": transaction.transaction_type.name,
            "amount": transaction.amount,
            "account_id": transaction.account_id,
            "timestamp": transaction.timestamp.isoformat()
        }

    def _deserialize_transaction(self, data: Dict) -> Transaction:
        """Convert dictionary data back to Transaction object"""
        txn = Transaction(
            transaction_type=TransactionType[data["transaction_type"]],
            amount=data["amount"],
            account_id=data["account_id"],
            timestamp=datetime.fromisoformat(data["timestamp"])
        )
        # Override the transaction_id (which is generated in __post_init__)
        txn.transaction_id = data["transaction_id"]
        return txn

    def _add_to_account_index(self, transaction: Transaction) -> None:
        """Add transaction ID to account index"""
        index_path = self._get_account_index_path(transaction.account_id)

        # Load existing index if it exists
        transaction_ids = []
        if os.path.exists(index_path):
            try:
                with open(index_path, 'r') as f:
                    transaction_ids = json.load(f)
            except json.JSONDecodeError:
                # If file is corrupted, start with empty list
                pass

        # Add transaction ID if not already in index
        if transaction.transaction_id not in transaction_ids:
            transaction_ids.append(transaction.transaction_id)

            # Write updated index back to file
            with open(index_path, 'w') as f:
                json.dump(transaction_ids, f)

    def save(self, transaction: Transaction) -> None:
        """Save a transaction to the repository"""
        file_path = self._get_file_path(transaction.transaction_id)

        # Convert transaction to dictionary
        transaction_data = self._serialize_transaction(transaction)

        # Write to file
        with open(file_path, 'w') as f:
            json.dump(transaction_data, f, indent=2)

        # Update account index
        self._add_to_account_index(transaction)

    def find_by_id(self, transaction_id: str) -> Optional[Transaction]:
        """Find a transaction by its ID"""
        file_path = self._get_file_path(transaction_id)

        if not os.path.exists(file_path):
            return None

        try:
            with open(file_path, 'r') as f:
                transaction_data = json.load(f)
                return self._deserialize_transaction(transaction_data)
        except (json.JSONDecodeError, FileNotFoundError):
            return None

    def find_by_account_id(self, account_id: str) -> List[Transaction]:
        """Find all transactions for a specific account"""
        transactions = []
        index_path = self._get_account_index_path(account_id)

        if not os.path.exists(index_path):
            return transactions

        try:
            # Load transaction IDs from index
            with open(index_path, 'r') as f:
                transaction_ids = json.load(f)

            # Load each transaction
            for transaction_id in transaction_ids:
                transaction = self.find_by_id(transaction_id)
                if transaction:
                    transactions.append(transaction)
        except (json.JSONDecodeError, FileNotFoundError):
            # Return empty list if index file is invalid
            pass

        return transactions

    def find_all(self) -> List[Transaction]:
        """Find all transactions"""
        transactions = []

        # Check if directory exists
        if not os.path.exists(self.storage_dir):
            return transactions

        # Iterate through all JSON files in the directory (excluding index dir)
        for filename in os.listdir(self.storage_dir):
            if filename.endswith('.json') and os.path.isfile(os.path.join(self.storage_dir, filename)):
                try:
                    with open(os.path.join(self.storage_dir, filename), 'r') as f:
                        transaction_data = json.load(f)
                        transaction = self._deserialize_transaction(transaction_data)
                        transactions.append(transaction)
                except (json.JSONDecodeError, FileNotFoundError):
                    # Skip invalid files
                    continue

        return transactions
