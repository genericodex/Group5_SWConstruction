from datetime import datetime
from typing import List
from domain.monthly_statement import MonthlyStatement
from infrastructure.adapters.statement_adapter import IStatementGenerator
from domain.transactions import Transaction
from domain.interest import SavingsInterestStrategy, CheckingInterestStrategy
from application.repositories.transaction_repository import ITransactionRepository
from application.repositories.account_repository import IAccountRepository

class StatementService:
    def __init__(self, transaction_repo: ITransactionRepository,
                 account_repo: IAccountRepository,
                 generator: IStatementGenerator):
        self.transaction_repo = transaction_repo
        self.account_repo = account_repo
        self.generator = generator

    def generate_statement(self, account_id: str, start_date: datetime,
                          end_date: datetime, format_type: str = "PDF") -> str:
        account = self.account_repo.get_by_id(account_id)
        if not account:
            raise ValueError("Account not found")

        # Fetch all transactions for accurate balance calculation
        all_transactions: List[Transaction] = self.transaction_repo.get_by_account_id(account_id)
        transactions_before = [t for t in all_transactions if t.timestamp < start_date]
        transactions_during = [t for t in all_transactions if start_date <= t.timestamp <= end_date]

        # Calculate starting and ending balances
        starting_balance = (sum(t.amount for t in transactions_before if t.transaction_type.name == "DEPOSIT") -
                            sum(t.amount for t in transactions_before if t.transaction_type.name == "WITHDRAW"))
        net_change = (sum(t.amount for t in transactions_during if t.transaction_type.name == "DEPOSIT") -
                      sum(t.amount for t in transactions_during if t.transaction_type.name == "WITHDRAW"))
        ending_balance = starting_balance + net_change

        # Calculate interest
        interest_strategy = SavingsInterestStrategy() if account.account_type.name == "SAVINGS" else CheckingInterestStrategy()
        interest = interest_strategy.calculate_interest(ending_balance, start_date, end_date)

        # Create domain object
        statement = MonthlyStatement(
            account_id=account_id,
            statement_period=start_date.strftime("%B %Y"),
            start_date=start_date,
            end_date=end_date,
            starting_balance=starting_balance,
            ending_balance=ending_balance,
            interest_earned=interest,
            transactions=transactions_during
        )

        # Delegate to infrastructure
        return self.generator.generate(statement, format_type)