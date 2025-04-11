from abc import ABC, abstractmethod
from typing import Dict, List
from domain.accounts import Account


# Abstract Base Class for AccountRepository
class IAccountRepository(ABC):
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


