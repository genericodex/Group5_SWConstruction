from abc import ABC, abstractmethod
from typing import Dict, List
from domain.accounts import Account


# Abstract Base Class for AccountRepository
class AccountRepository(ABC):
    @abstractmethod
    def save(self, account: Account) -> None:
        """Save or update an account in the repository."""
        pass

    @abstractmethod
    def get_by_id(self, account_id: str) -> Account:
        """Retrieve an account by its unique ID."""
        pass

    @abstractmethod
    def get_all(self) -> List[Account]:
        """Retrieve all accounts."""
        pass

    @abstractmethod
    def delete(self, account_id: str) -> None:

        """Delete an account by its unique ID."""
        pass


# Concrete implementation using in-memory dictionary
class InMemoryAccountRepository(AccountRepository):
    def __init__(self):
        self._accounts: Dict[str, Account] = {}

    def save(self, account: Account) -> None:
        """Insert or update an account."""
        self._accounts[account.account_id] = account

    def get_by_id(self, account_id: str) -> Account:
        """Fetch an account by ID."""
        account = self._accounts.get(account_id)
        if not account:
            raise ValueError(f"Account with ID '{account_id}' not found.")
        return account

    def get_all(self) -> List[Account]:
        """Return a list of all accounts."""
        return list(self._accounts.values())

    def delete(self, account_id: str) -> None:
        """Remove an account by ID."""
        if account_id in self._accounts:
            del self._accounts[account_id]
        else:
            raise ValueError(f"Account with ID '{account_id}' does not exist.")

