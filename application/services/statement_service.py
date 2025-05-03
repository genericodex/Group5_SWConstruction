from datetime import datetime
from typing import List
from domain.transactions import Transaction
from domain.interest import SavingsInterestStrategy, CheckingInterestStrategy
from application.repositories.transaction_repository import ITransactionRepository
from application.repositories.account_repository import IAccountRepository

class StatementService:
    def __init__(self, transaction_repo: ITransactionRepository, account_repo: IAccountRepository, generator):
        self.transaction_repo = transaction_repo
        self.account_repo = account_repo
        self.generator = generator  # Placeholder for PDF/CSV generator interface

    def generate_statement(self, account_id: str, start_date: datetime, end_date: datetime, format_type: str = "PDF") -> str:
        # Fetch account to determine account type
        account = self.account_repo.get_by_id(account_id)
        if not account:
            raise ValueError("Account not found")

        # Gather relevant transactions
        transactions: List[Transaction] = self.transaction_repo.get_by_account_id(account_id)
        relevant_transactions = [t for t in transactions if start_date <= t.timestamp <= end_date]

        # Determine interest strategy based on account type (simplified)
        if account.account_type.name == "SAVINGS":
            interest_strategy = SavingsInterestStrategy()
        else:  # Assuming CHECKING as default
            interest_strategy = CheckingInterestStrategy()

        # Calculate interest
        balance = sum(t.amount for t in relevant_transactions if t.transaction_type.name == "DEPOSIT") - \
                  sum(t.amount for t in relevant_transactions if t.transaction_type.name == "WITHDRAW")
        interest = interest_strategy.calculate_interest(balance, start_date, end_date)

        # Prepare data for generator
        statement_data = {
            "account_id": account_id,
            "transactions": [t.to_dict() for t in relevant_transactions],
            "interest": interest,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }

        # Pass data to generator
        if format_type.upper() == "PDF":
            return self.generator.generate_pdf(statement_data)
        elif format_type.upper() == "CSV":
            return self.generator.generate_csv(statement_data)
        else:
            raise ValueError("Unsupported format type")