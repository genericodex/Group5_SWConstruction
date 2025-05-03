"""
Implementation of the transaction limit repository in the infrastructure layer.
This handles the storage and retrieval of transaction limits and usage data.
"""
from datetime import date
from typing import Dict, Optional, Any
import json
import os

from application.repositories.transaction_repository import ITransactionLimitRepository


class TransactionLimitRepositoryImpl(ITransactionLimitRepository):
    """Implementation of transaction limit repository using file storage."""

    def __init__(self, data_directory: str, logging_service=None):
        """
        Initialize the transaction limit repository.

        :param data_directory: Directory to store limit data files
        :param logging_service: Optional logging service
        """
        self.data_directory = data_directory
        self.logging_service = logging_service
        self._ensure_directory_exists()

        # Cache to reduce file I/O
        self._limits_cache: Dict[str, Dict[str, float]] = {}
        self._daily_usage_cache: Dict[str, Dict[str, float]] = {}
        self._monthly_usage_cache: Dict[str, Dict[str, float]] = {}

    def _ensure_directory_exists(self) -> None:
        """Ensure the data directory exists."""
        if not os.path.exists(self.data_directory):
            os.makedirs(self.data_directory)
            if self.logging_service:
                self.logging_service.info(f"Created transaction limits directory: {self.data_directory}")

    def _get_limits_file_path(self, account_id: str) -> str:
        """Get the file path for account limits."""
        return os.path.join(self.data_directory, f"{account_id}_limits.json")

    def _get_daily_usage_file_path(self, account_id: str) -> str:
        """Get the file path for daily usage."""
        return os.path.join(self.data_directory, f"{account_id}_daily_usage.json")

    def _get_monthly_usage_file_path(self, account_id: str) -> str:
        """Get the file path for monthly usage."""
        return os.path.join(self.data_directory, f"{account_id}_monthly_usage.json")

    def _read_json_file(self, file_path: str) -> Dict[str, Any]:
        """Read data from a JSON file."""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as file:
                    return json.load(file)
            return {}
        except (json.JSONDecodeError, IOError) as e:
            if self.logging_service:
                self.logging_service.error(f"Error reading file {file_path}: {str(e)}")
            return {}

    def _write_json_file(self, file_path: str, data: Dict[str, Any]) -> None:
        """Write data to a JSON file."""
        try:
            with open(file_path, 'w') as file:
                json.dump(data, file)
        except IOError as e:
            if self.logging_service:
                self.logging_service.error(f"Error writing file {file_path}: {str(e)}")

    def get_daily_usage(self, account_id: str, transaction_date: date) -> float:
        """
        Get daily usage for an account on a specific date.

        :param account_id: Account identifier
        :param transaction_date: Date to check
        :return: Total used amount on that date
        """
        date_str = transaction_date.isoformat()

        # Check cache first
        if account_id in self._daily_usage_cache:
            return self._daily_usage_cache[account_id].get(date_str, 0.0)

        # Read from file if not in cache
        file_path = self._get_daily_usage_file_path(account_id)
        data = self._read_json_file(file_path)

        # Update cache
        self._daily_usage_cache[account_id] = data

        return data.get(date_str, 0.0)

    def get_monthly_usage(self, account_id: str, year: int, month: int) -> float:
        """
        Get monthly usage for an account in a specific month.

        :param account_id: Account identifier
        :param year: Year of the month
        :param month: Month number (1-12)
        :return: Total used amount in that month
        """
        month_key = f"{year}-{month:02d}"

        # Check cache first
        if account_id in self._monthly_usage_cache:
            return self._monthly_usage_cache[account_id].get(month_key, 0.0)

        # Read from file if not in cache
        file_path = self._get_monthly_usage_file_path(account_id)
        data = self._read_json_file(file_path)

        # Update cache
        self._monthly_usage_cache[account_id] = data

        return data.get(month_key, 0.0)

    def add_usage(self, account_id: str, amount: float, transaction_date: date) -> None:
        """
        Add usage amount for an account on a specific date.

        :param account_id: Account identifier
        :param amount: Amount to add
        :param transaction_date: Date of the transaction
        """
        # Update daily usage
        date_str = transaction_date.isoformat()
        month_key = f"{transaction_date.year}-{transaction_date.month:02d}"

        # Update daily usage cache and file
        if account_id not in self._daily_usage_cache:
            file_path = self._get_daily_usage_file_path(account_id)
            self._daily_usage_cache[account_id] = self._read_json_file(file_path)

        current_daily = self._daily_usage_cache[account_id].get(date_str, 0.0)
        self._daily_usage_cache[account_id][date_str] = current_daily + amount

        daily_file_path = self._get_daily_usage_file_path(account_id)
        self._write_json_file(daily_file_path, self._daily_usage_cache[account_id])

        # Update monthly usage cache and file
        if account_id not in self._monthly_usage_cache:
            file_path = self._get_monthly_usage_file_path(account_id)
            self._monthly_usage_cache[account_id] = self._read_json_file(file_path)

        current_monthly = self._monthly_usage_cache[account_id].get(month_key, 0.0)
        self._monthly_usage_cache[account_id][month_key] = current_monthly + amount

        monthly_file_path = self._get_monthly_usage_file_path(account_id)
        self._write_json_file(monthly_file_path, self._monthly_usage_cache[account_id])

        if self.logging_service:
            self.logging_service.debug(
                f"Added usage for account {account_id}",
                {
                    "account_id": account_id,
                    "amount": amount,
                    "date": date_str,
                    "new_daily_total": self._daily_usage_cache[account_id][date_str],
                    "new_monthly_total": self._monthly_usage_cache[account_id][month_key]
                }
            )

    def get_account_limits(self, account_id: str) -> Dict[str, float]:
        """
        Get all transaction limits for an account.

        :param account_id: Account identifier
        :return: Dictionary with limit types and amounts
        """
        # Check cache first
        if account_id in self._limits_cache:
            return self._limits_cache[account_id]

        # Read from file if not in cache
        file_path = self._get_limits_file_path(account_id)
        data = self._read_json_file(file_path)

        # Set default limits if none exist
        if not data:
            data = {
                "daily": 1000.0,  # Default daily limit
                "monthly": 20000.0  # Default monthly limit
            }
            self._write_json_file(file_path, data)

        # Update cache
        self._limits_cache[account_id] = data

        return data

    def set_account_limit(self, account_id: str, limit_type: str, limit_amount: float) -> None:
        """
        Set a specific limit for an account.

        :param account_id: Account identifier
        :param limit_type: Type of limit (e.g., "daily", "monthly")
        :param limit_amount: Limit amount
        """
        # Validate limit amount
        if limit_amount < 0:
            error_msg = f"Limit amount cannot be negative: {limit_amount}"
            if self.logging_service:
                self.logging_service.error(error_msg)
            raise ValueError(error_msg)

        # Get current limits
        limits = self.get_account_limits(account_id)

        # Update limit
        limits[limit_type] = limit_amount

        # Update cache
        self._limits_cache[account_id] = limits

        # Write to file
        file_path = self._get_limits_file_path(account_id)
        self._write_json_file(file_path, limits)

        if self.logging_service:
            self.logging_service.info(
                f"Updated {limit_type} limit for account {account_id}",
                {
                    "account_id": account_id,
                    "limit_type": limit_type,
                    "limit_amount": limit_amount
                }
            )

    def reset_daily_usage(self, account_id: str) -> None:
        """
        Reset daily usage for an account.

        :param account_id: Account identifier
        """
        # Clear cache
        if account_id in self._daily_usage_cache:
            del self._daily_usage_cache[account_id]

        # Clear file
        file_path = self._get_daily_usage_file_path(account_id)
        self._write_json_file(file_path, {})

        if self.logging_service:
            self.logging_service.info(f"Reset daily usage for account {account_id}")

    def reset_monthly_usage(self, account_id: str) -> None:
        """
        Reset monthly usage for an account.

        :param account_id: Account identifier
        """
        # Clear cache
        if account_id in self._monthly_usage_cache:
            del self._monthly_usage_cache[account_id]

        # Clear file
        file_path = self._get_monthly_usage_file_path(account_id)
        self._write_json_file(file_path, {})

        if self.logging_service:
            self.logging_service.info(f"Reset monthly usage for account {account_id}")