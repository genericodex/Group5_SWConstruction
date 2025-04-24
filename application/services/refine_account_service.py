from fastapi import Depends
from sqlalchemy.orm import Session
from application.services.account_service import AccountCreationService
from application.services.fund_transfer import FundTransferService
from application.services.transaction_service import TransactionService

from infrastructure.Notifications.notifications import NotificationService
from infrastructure.database.db import get_db
from domain.accounts import Account
from domain.transactions import Transaction


class RefineAccountService:
    def __init__(
            self,
            account_creation_service: AccountCreationService,
            transaction_service: TransactionService,
            fund_transfer_service: FundTransferService,
            notification_service: NotificationService
    ):
        self.account_creation_service = account_creation_service
        self.transaction_service = transaction_service
        self.fund_transfer_service = fund_transfer_service
        self.notification_service = notification_service

    def create_account_with_validation(self, account_data: Account) -> str:
        """Create an account after validating necessary parameters."""
        # Example validation (extend as needed):
        if account_data.balance < 0:
            raise ValueError("Initial balance cannot be negative")
        if not account_data.account_id:
            raise ValueError("Account ID is required")

        # Create the account using AccountCreationService
        account_id = self.account_creation_service.create_account(account_data)

        # Notify of the account creation (optional step)
        self.notification_service.notify(f"Account {account_id} was created successfully.")

        return account_id

    def transfer_funds_refined(self, from_account: str, to_account: str, amount: float) -> str:
        """Refine fund transfer logic including validations and notification."""
        # Validate transfer parameters
        if amount <= 0:
            raise ValueError("The transfer amount must be greater than zero")
        if not from_account or not to_account:
            raise ValueError("Both source and destination accounts are required")

        # Example - check balance before transferring funds
        source_account_balance = self.transaction_service.get_account_balance(from_account)
        if source_account_balance < amount:
            raise ValueError("Insufficient balance for the transfer")

        # Perform the transfer using FundTransferService
        transfer_id = self.fund_transfer_service.transfer_funds(from_account, to_account, amount)

        # Notify the users involved
        self.notification_service.notify(
            f"Transfer of {amount} from account {from_account} to {to_account} completed successfully."
        )

        return transfer_id

    def summarize_account_activity(self, account_id: str):
        """
        Combine account details and transaction summary.
        """
        # Get account details
        account_details = self.account_creation_service.get_account_by_id(account_id)

        if not account_details:
            raise ValueError(f"Account with ID {account_id} does not exist")

        # Get all transactions for the account
        account_transactions = self.transaction_service.get_transactions_for_account(account_id)

        # Refine and return summary
        summary = {
            "account_id": account_id,
            "details": account_details,
            "transactions": account_transactions,
        }

        return summary
