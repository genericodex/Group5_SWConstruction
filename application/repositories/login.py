
from abc import ABC, abstractmethod
from domain.accounts import Account


class IAuthenticationService(ABC):
    @abstractmethod
    def login(self, username: str, password: str) -> Account:
        """Logs a user in by verifying credentials."""
        pass
