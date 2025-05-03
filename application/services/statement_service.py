from datetime import datetime
from typing import List

from application.services.statement_generator import IStatementGenerator
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

        transactions: List[Transaction] = self.transaction_repo.get_by_account_id(account_id)
        relevant_transactions = [t for t in transactions if start_date <= t.timestamp <= end_date]

        if account.account_type.name == "SAVINGS":
            interest_strategy = SavingsInterestStrategy()
        else:  # Assuming CHECKING as default
            interest_strategy = CheckingInterestStrategy()

        balance = sum(t.amount for t in relevant_transactions if t.transaction_type.name == "DEPOSIT") - \
                 sum(t.amount for t in relevant_transactions if t.transaction_type.name == "WITHDRAW")
        interest = interest_strategy.calculate_interest(balance, start_date, end_date)

        statement_data = {
            "account_id": account_id,
            "transactions": [t.to_dict() for t in relevant_transactions],
            "interest": interest,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }

        if format_type.upper() == "PDF":
            return self.generator.generate_pdf(statement_data)
        elif format_type.upper() == "CSV":
            return self.generator.generate_csv(statement_data)
        else:
            raise ValueError("Unsupported format type")