from typing import Dict

from application.repositories.login import IAuthenticationService
from domain.accounts import Account, AccountType
from domain.savings_account import SavingsAccount


class InMemoryAuthenticationService(IAuthenticationService):
    def __init__(self):
        # In-memory storage for accounts (username as key for simplicity)
        self._accounts: Dict[str, Account] = {}

    def register(self, account_id: str, username: str, password: str, account_type: AccountType) -> Account:
        """Registers a new user with an account."""
        if username in self._accounts:
            raise ValueError(f"Username '{username}' already exists.")

        # Create a new account instance
        account = SavingsAccount(account_id=account_id, account_type=account_type, username=username)
        account.hash_password(password)
        self._accounts[username] = account
        return account

    def login(self, username: str, password: str) -> Account:
        """Attempts to log a user in by validating their credentials."""
        if username not in self._accounts:
            raise ValueError("Invalid username or password.")

        account = self._accounts[username]
        if not account.verify_password(password):
            raise ValueError("Invalid username or password.")

        return account

# For simplicity: SavingsAccount/CheckingAccount classes can be reused here as needed.
