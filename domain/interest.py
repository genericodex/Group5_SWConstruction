from datetime import datetime
from domain.accounts import InterestStrategy

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
