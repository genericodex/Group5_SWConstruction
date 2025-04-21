from application.services.notification_service import INotificationService
from domain.accounts import Account
from domain.accounts import AccountType
from typing import Dict


class InMemoryAuthenticationService:
    def __init__(self, notification_service: INotificationService):
        """Inject the notification service."""
        self.notification_service = notification_service
        self.accounts: Dict[str, Account] = {}

    def register(self, account_id: str, username: str, password: str, account_type: AccountType) -> Account:
        if username in (account.username for account in self.accounts.values()):
            raise ValueError("Username already exists!")

        account = Account(
            account_id=account_id,
            username=username,
            password=password,
            account_type=account_type
        )
        self.accounts[account_id] = account

        # Send notification
        self.notification_service.notify(f"User {username} has been successfully registered!")
        return account

    def login(self, username: str, password: str) -> Account:
        for account in self.accounts.values():
            if account.username == username and account.verify_password(password):
                # Send notification
                self.notification_service.notify(f"User {username} has logged in!")
                return account
        raise ValueError("Invalid username or password")

    def withdraw(self, account_id: str, amount: float) -> None:
        account = self.accounts.get(account_id)
        if account is None:
            raise ValueError("Account not found!")
        if account.balance < amount:
            raise ValueError("Insufficient balance!")

        account.balance -= amount

        # Send notification
        self.notification_service.notify(
            f"User {account.username} withdrew {amount:.2f}. New balance: {account.balance:.2f}")

    def deposit(self, account_id: str, amount: float) -> None:
        account = self.accounts.get(account_id)
        if account is None:
            raise ValueError("Account not found!")

        account.balance += amount

        # Send notification
        self.notification_service.notify(
            f"User {account.username} deposited {amount:.2f}. New balance: {account.balance:.2f}")
