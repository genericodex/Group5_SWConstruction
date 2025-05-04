from datetime import datetime, timedelta
from typing import Dict, List
from domain.accounts import Account
from domain.transactions import Transaction

class TransactionLimits:
    def __init__(self, daily_limit: float = None, monthly_limit: float = None):
        self.daily_limit = daily_limit
        self.monthly_limit = monthly_limit
        self.daily_totals: Dict[str, float] = {}
        self.monthly_totals: Dict[str, float] = {}
        self.transactions: List[Transaction] = []

    def can_process_transaction(self, account_id: str, amount: float) -> bool:
        today = datetime.now().date()
        current_month = today.replace(day=1)

        # Update totals
        if today not in self.daily_totals:
            self.daily_totals = {today: 0.0}
        if current_month not in self.monthly_totals:
            self.monthly_totals = {current_month: 0.0}

        # Check limits
        if self.daily_limit and (self.daily_totals[today] + amount) > self.daily_limit:
            return False
        if self.monthly_limit and (self.monthly_totals[current_month] + amount) > self.monthly_limit:
            return False

        return True

    def record_transaction(self, transaction: Transaction):
        self.transactions.append(transaction)
        today = datetime.now().date()
        current_month = today.replace(day=1)
        
        self.daily_totals[today] = self.daily_totals.get(today, 0.0) + transaction.amount
        self.monthly_totals[current_month] = self.monthly_totals.get(current_month, 0.0) + transaction.amount
