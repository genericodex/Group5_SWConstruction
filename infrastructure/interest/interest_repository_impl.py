from domain.interest_repository import IInterestRepository
from infrastructure.interest.interest_data_source import InterestDataSource
from typing import Dict, Optional


class InterestRepositoryImpl(IInterestRepository):
    """Implementation of the interest repository interface from the domain layer"""

    def __init__(self, interest_data_source: InterestDataSource, logging_service=None):
        """
        Initialize interest repository implementation.

        :param interest_data_source: Data source for interest rates
        :param logging_service: Optional service for logging operations
        """
        self.interest_data_source = interest_data_source
        self.logging_service = logging_service
        # Cache to optimize frequent access to interest rates
        self._cache: Dict[str, float] = {}

    def get_interest_rate(self, account_type: str) -> float:
        """
        Get interest rate for a specific account type.

        :param account_type: The type of account (e.g., "savings", "checking")
        :return: The interest rate as a float
        :raises ValueError: If interest rate is not found
        """
        # Check cache first
        if account_type in self._cache:
            return self._cache[account_type]

        # Get from data source if not in cache
        rate = self.interest_data_source.get(account_type)

        if rate is None:
            error_msg = f"Interest rate for account type '{account_type}' not found."
            if self.logging_service:
                self.logging_service.error(error_msg)
            raise ValueError(error_msg)

        # Update cache
        self._cache[account_type] = rate

        if self.logging_service:
            self.logging_service.debug(
                f"Retrieved interest rate for {account_type}",
                {"account_type": account_type, "rate": rate}
            )

        return rate

    def set_interest_rate(self, account_type: str, rate: float) -> None:
        """
        Set or update interest rate for a specific account type.

        :param account_type: The type of account
        :param rate: The interest rate to set as a float
        """
        if rate < 0:
            error_msg = f"Interest rate cannot be negative: {rate}"
            if self.logging_service:
                self.logging_service.error(error_msg)
            raise ValueError(error_msg)

        self.interest_data_source.set(account_type, rate)

        # Update cache
        self._cache[account_type] = rate

        if self.logging_service:
            self.logging_service.info(
                f"Updated interest rate for {account_type}",
                {"account_type": account_type, "new_rate": rate}
            )

    def clear_cache(self) -> None:
        """Clear the interest rate cache"""
        self._cache.clear()

        if self.logging_service:
            self.logging_service.debug("Interest rate cache cleared")