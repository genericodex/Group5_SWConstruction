from typing import List, Optional, Dict
import json
import os
from domain.accounts import Account, CheckingAccount, SavingsAccount, AccountType, AccountStatus
from application.repositories.account_repository import IAccountRepository
from datetime import datetime


class FileAccountRepository(IAccountRepository):
    def __init__(self, storage_dir: str = "data/accounts"):
        self.storage_dir = storage_dir
        # Create directory if it doesn't exist
        os.makedirs(storage_dir, exist_ok=True)

    def _get_file_path(self, account_id: str) -> str:
        """Get the file path for an account"""
        return os.path.join(self.storage_dir, f"{account_id}.json")

    def _serialize_account(self, account: Account) -> Dict:
        """Convert Account object to dictionary for JSON serialization"""
        return {
            "account_id": account.account_id,
            "account_type": account.account_type.name,
            "balance": account._balance,
            "status": account.status.name,
            "creation_date": account.creation_date.isoformat(),
            "transactions": [self._serialize_transaction(t) for t in account._transactions]
        }

    def _serialize_transaction(self, transaction) -> Dict:
        """Convert Transaction object to dictionary for JSON serialization"""
        return {
            "transaction_id": transaction.transaction_id,
            "transaction_type": transaction.transaction_type.name,
            "amount": transaction.amount,
            "account_id": transaction.account_id,
            "timestamp": transaction.timestamp.isoformat()
        }

    def _deserialize_account(self, data: Dict) -> Account:
        """Convert dictionary data back to Account object"""
        # Determine account type and create appropriate account
        account_type = AccountType[data["account_type"]]

        if account_type == AccountType.CHECKING:
            account = CheckingAccount(account_id=data["account_id"], initial_balance=0.0)
        elif account_type == AccountType.SAVINGS:
            account = SavingsAccount(account_id=data["account_id"], initial_balance=0.0)
        else:
            raise ValueError(f"Unknown account type: {data['account_type']}")

        # Set account properties
        account._balance = data["balance"]
        account.status = AccountStatus[data["status"]]
        account.creation_date = datetime.fromisoformat(data["creation_date"])

        # Deserialize transactions if they exist
        if "transactions" in data:
            from domain.transactions import Transaction, TransactionType
            for txn_data in data["transactions"]:
                txn = Transaction(
                    transaction_type=TransactionType[txn_data["transaction_type"]],
                    amount=txn_data["amount"],
                    account_id=txn_data["account_id"],
                    timestamp=datetime.fromisoformat(txn_data["timestamp"])
                )
                # Set the transaction_id explicitly since it's derived in __post_init__
                txn.transaction_id = txn_data["transaction_id"]
                account._transactions.append(txn)

        return account

    def save(self, account: Account) -> None:
        """Save or update an account in the repository"""
        file_path = self._get_file_path(account.account_id)

        # Convert account to dictionary
        account_data = self._serialize_account(account)

        # Write to file
        with open(file_path, 'w') as f:
            json.dump(account_data, f, indent=2)

    def find_by_id(self, account_id: str) -> Optional[Account]:
        """Find an account by its ID"""
        file_path = self._get_file_path(account_id)

        if not os.path.exists(file_path):
            return None

        try:
            with open(file_path, 'r') as f:
                account_data = json.load(f)
                return self._deserialize_account(account_data)
        except (json.JSONDecodeError, FileNotFoundError):
            return None

    def find_all(self) -> List[Account]:
        """Find all accounts"""
        accounts = []

        # Check if directory exists
        if not os.path.exists(self.storage_dir):
            return accounts

        # Iterate through all JSON files in the directory
        for filename in os.listdir(self.storage_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(self.storage_dir, filename)
                try:
                    with open(file_path, 'r') as f:
                        account_data = json.load(f)
                        account = self._deserialize_account(account_data)
                        accounts.append(account)
                except (json.JSONDecodeError, FileNotFoundError):
                    # Skip invalid files
                    continue

        return accounts

    def delete(self, account_id: str) -> None:
        """Delete an account from the repository"""
        file_path = self._get_file_path(account_id)

        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            raise ValueError(f"Account with ID '{account_id}' does not exist.")