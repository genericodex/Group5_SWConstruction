from abc import ABC, abstractmethod
from typing import Dict


class IAccountConstraintsRepository(ABC):
    """Interface for account constraints repository operations"""

    @abstractmethod
    def create_constraints(self, account_id: str) -> None:
        """Create default constraints for a new account

        Args:
            account_id: The account identifier
        """
        pass

    @abstractmethod
    def get_usage(self, account_id: str) -> Dict[str, float]:
        """Get current usage for account

        Args:
            account_id: The account identifier

        Returns:
            Dict with daily and monthly usage
        """
        pass

    @abstractmethod
    def reset_usage(self, account_id: str, period: str) -> None:
        """Reset usage for a specific period

        Args:
            account_id: The account identifier
            period: Either "daily" or "monthly"

        Raises:
            ValueError: If period is invalid or constraints not found
        """
        pass

    @abstractmethod
    def update_usage(self, account_id: str, amount: float, period: str) -> None:
        """Update usage for a specific period

        Args:
            account_id: The account identifier
            amount: Amount to add to current usage
            period: Either "daily" or "monthly"

        Raises:
            ValueError: If period is invalid, constraints not found, or limit exceeded
        """
        pass

    @abstractmethod
    def get_limits(self, account_id: str) -> Dict[str, float]:
        """Get account limits

        Args:
            account_id: The account identifier

        Returns:
            Dict with daily and monthly limits
        """
        pass

    @abstractmethod
    def update_limits(self, account_id: str, daily_limit: float, monthly_limit: float) -> None:
        """Update account limits

        Args:
            account_id: The account identifier
            daily_limit: New daily limit
            monthly_limit: New monthly limit

        Raises:
            ValueError: If constraints not found
        """
        pass