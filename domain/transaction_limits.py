"""
Transaction limits domain class.
This handles the business rules for transaction limits.
"""
from datetime import datetime, date
from typing import Dict, List, Optional

from application.repositories.transaction_repository import ITransactionLimitRepository
from domain.transactions import Transaction



class TransactionLimits:
    """
    Manages transaction limits for accounts.
    Uses a repository to store and retrieve limits and usage data.
    """

    def __init__(self,
                 transaction_limit_repository: ITransactionLimitRepository,
                 account_id: str):
        """
        Initialize transaction limits for an account.

        :param transaction_limit_repository: Repository for limits and usage data
        :param account_id: The account identifier
        """
        self.transaction_limit_repository = transaction_limit_repository
        self.account_id = account_id
        self._limits = None  # Lazy-loaded limits

    def _get_limits(self) -> Dict[str, float]:
        """Get limits from repository (lazy-loaded)."""
        if self._limits is None:
            self._limits = self.transaction_limit_repository.get_account_limits(self.account_id)
        return self._limits

    def get_daily_limit(self) -> float:
        """Get the daily transaction limit."""
        return self._get_limits().get("daily", float('inf'))

    def get_monthly_limit(self) -> float:
        """Get the monthly transaction limit."""
        return self._get_limits().get("monthly", float('inf'))

    def set_daily_limit(self, amount: float) -> None:
        """Set the daily transaction limit."""
        self.transaction_limit_repository.set_account_limit(self.account_id, "daily", amount)
        if self._limits is not None:
            self._limits["daily"] = amount

    def set_monthly_limit(self, amount: float) -> None:
        """Set the monthly transaction limit."""
        self.transaction_limit_repository.set_account_limit(self.account_id, "monthly", amount)
        if self._limits is not None:
            self._limits["monthly"] = amount

    def get_daily_usage(self, transaction_date: Optional[date] = None) -> float:
        """
        Get daily usage for a specific date.

        :param transaction_date: Date to check (defaults to today)
        :return: Total amount used on that date
        """
        if transaction_date is None:
            transaction_date = datetime.now().date()

        return self.transaction_limit_repository.get_daily_usage(
            self.account_id, transaction_date)

    def get_monthly_usage(self, year: Optional[int] = None, month: Optional[int] = None) -> float:
        """
        Get monthly usage for a specific month.

        :param year: Year of the month (defaults to current year)
        :param month: Month number (1-12) (defaults to current month)
        :return: Total amount used in that month
        """
        if year is None or month is None:
            now = datetime.now()
            year = year or now.year
            month = month or now.month

        return self.transaction_limit_repository.get_monthly_usage(
            self.account_id, year, month)

    def can_process_transaction(self, amount: float, transaction_date: Optional[date] = None) -> bool:
        """
        Check if a transaction can be processed within limits.

        :param amount: Transaction amount
        :param transaction_date: Date of the transaction (defaults to today)
        :return: True if transaction is within limits, False otherwise
        """
        if transaction_date is None:
            transaction_date = datetime.now().date()

        # Get current usage
        daily_usage = self.get_daily_usage(transaction_date)

        # Get current limits
        daily_limit = self.get_daily_limit()

        # Check daily limit
        if daily_limit is not None and daily_usage + amount > daily_limit:
            return False

        # Get monthly usage if we passed the daily check
        year, month = transaction_date.year, transaction_date.month
        monthly_usage = self.get_monthly_usage(year, month)

        # Get monthly limit
        monthly_limit = self.get_monthly_limit()

        # Check monthly limit
        if monthly_limit is not None and monthly_usage + amount > monthly_limit:
            return False

        return True

    def record_transaction(self, amount: float, transaction_date: Optional[date] = None) -> None:
        """
        Record a transaction in the usage data.

        :param amount: Transaction amount
        :param transaction_date: Date of the transaction (defaults to today)
        """
        if transaction_date is None:
            transaction_date = datetime.now().date()

        self.transaction_limit_repository.add_usage(
            self.account_id, amount, transaction_date)