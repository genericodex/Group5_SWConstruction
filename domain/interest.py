from datetime import datetime
from domain.accounts import InterestStrategy
from domain.interest_repository import IInterestRepository


class DynamicInterestStrategy(InterestStrategy):
    """Interest strategy that retrieves rates from a repository"""

    def __init__(self, interest_repository: IInterestRepository, account_type: str):
        """
        Initialize dynamic interest strategy.

        :param interest_repository: Repository to retrieve interest rates
        :param account_type: Type of account for rate lookups
        """
        self.interest_repository = interest_repository
        self.account_type = account_type

    def calculate_interest(self, balance: float, start_date: datetime, end_date: datetime) -> float:
        """
        Calculate interest based on balance and period using dynamic rates.

        :param balance: Account balance
        :param start_date: Start date for interest calculation
        :param end_date: End date for interest calculation
        :return: Calculated interest amount
        """
        annual_rate = self.interest_repository.get_interest_rate(self.account_type)
        days = (end_date - start_date).days
        daily_rate = annual_rate / 365
        return balance * daily_rate * days


class SavingsInterestStrategy(InterestStrategy):
    def __init__(self, annual_rate: float = 0.025):  # 2.5% default
        self.annual_rate = annual_rate

    def calculate_interest(self, balance: float, start_date: datetime, end_date: datetime) -> float:
        days = (end_date - start_date).days
        daily_rate = self.annual_rate / 365
        return balance * daily_rate * days


class CheckingInterestStrategy(InterestStrategy):
    def __init__(self, annual_rate: float = 0.001):  # 0.1% default
        self.annual_rate = annual_rate

    def calculate_interest(self, balance: float, start_date: datetime, end_date: datetime) -> float:
        days = (end_date - start_date).days
        daily_rate = self.annual_rate / 365
        return balance * daily_rate * days