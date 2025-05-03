from datetime import datetime
from typing import List
from domain.transactions import Transaction
from domain.monthly_statement import MonthlyStatement


class MonthlyStatementBuilder:
    def __init__(self):
        self._statement = None

    def create_new_statement(self, account_id: str, start_date: datetime, end_date: datetime):
        self._statement = MonthlyStatement(
            account_id=account_id,
            statement_period=f"{start_date.strftime('%B %Y')}",
            start_date=start_date,
            end_date=end_date,
            starting_balance=0.0,
            ending_balance=0.0,
            interest_earned=0.0,
            transactions=[]
        )
        return self

    def with_transactions(self, transactions: List[Transaction]):
        self._statement.transactions = transactions
        return self

    def with_starting_balance(self, balance: float):
        self._statement.starting_balance = balance
        return self

    def with_ending_balance(self, balance: float):
        self._statement.ending_balance = balance
        return self

    def with_interest_earned(self, interest: float):
        self._statement.interest_earned = interest
        return self

    def build(self) -> MonthlyStatement:
        return self._statement