from abc import ABC, abstractmethod
from typing import List
from domain.transactions import Transaction
from datetime import date
from typing import Dict, Optional

class ITransactionRepository(ABC):
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

    @abstractmethod
    def get_usage(self, account_id: str) -> dict[str, float]:
        """Retrieve daily and monthly transaction usage for the given account."""
        pass

    @abstractmethod
    def reset_usage(self, account_id: str, period: str) -> None:
        """Reset transaction usage for the specified period ('daily' or 'monthly')."""
        pass


class ITransactionLimitRepository(ABC):
    """Interface for transaction limit repository operations."""

    @abstractmethod
    def get_daily_usage(self, account_id: str, transaction_date: date) -> float:
        """
        Get the total amount used for a specific account on a specific date.

        :param account_id: The account identifier
        :param transaction_date: The date to check
        :return: Total amount used on that date
        """
        pass

    @abstractmethod
    def get_monthly_usage(self, account_id: str, year: int, month: int) -> float:
        """
        Get the total amount used for a specific account in a specific month.

        :param account_id: The account identifier
        :param year: The year of the month
        :param month: The month number (1-12)
        :return: Total amount used in that month
        """
        pass

    @abstractmethod
    def add_usage(self, account_id: str, amount: float, transaction_date: date) -> None:
        """
        Add usage amount for a specific account on a specific date.

        :param account_id: The account identifier
        :param amount: The amount to add to usage
        :param transaction_date: The date of the transaction
        """
        pass

    @abstractmethod
    def get_account_limits(self, account_id: str) -> Dict[str, float]:
        """
        Get all transaction limits for a specific account.

        :param account_id: The account identifier
        :return: Dictionary with limit types as keys and limit amounts as values
        """
        pass

    @abstractmethod
    def set_account_limit(self, account_id: str, limit_type: str, limit_amount: float) -> None:
        """
        Set a specific limit for an account.

        :param account_id: The account identifier
        :param limit_type: The type of limit (e.g., "daily", "monthly")
        :param limit_amount: The limit amount
        """
        pass

    @abstractmethod
    def reset_daily_usage(self, account_id: str) -> None:
        """
        Reset daily usage for an account.

        :param account_id: The account identifier
        """
        pass

    @abstractmethod
    def reset_monthly_usage(self, account_id: str) -> None:
        """
        Reset monthly usage for an account.

        :param account_id: The account identifier
        """
        pass
