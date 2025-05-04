from abc import ABC, abstractmethod


class IInterestRepository(ABC):
    """Interface for the interest repository in the domain layer"""

    @abstractmethod
    def get_interest_rate(self, account_type: str) -> float:
        """
        Get interest rate for a specific account type.

        :param account_type: The type of account (e.g., "savings", "checking")
        :return: The interest rate as a float
        :raises ValueError: If interest rate is not found
        """
        pass

    @abstractmethod
    def set_interest_rate(self, account_type: str, rate: float) -> None:
        """
        Set or update interest rate for a specific account type.

        :param account_type: The type of account
        :param rate: The interest rate to set as a float
        """
        pass