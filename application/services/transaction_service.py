from application.repositories.account_repository import IAccountRepository
from application.repositories.transaction_repository import ITransactionRepository
from domain.accounts import Account
from domain.transactions import Transaction

class TransactionService:
    def __init__(self, transaction_repository: ITransactionRepository, account_repository: IAccountRepository):
        self.transaction_repository = transaction_repository
        self.account_repository = account_repository

    def deposit(self, account_id: str, amount: float) -> Transaction:
        # Get account from repository
        account = self.account_repository.find_by_id(account_id)
        if not account:
            raise ValueError(f"Account with ID {account_id} not found")

        # Perform deposit
        transaction = account.deposit(amount)

        # Save transaction to repository
        self.transaction_repository.save(transaction)

        # Update account in repository
        self.account_repository.save(account)

        return transaction

    def withdraw(self, account_id: str, amount: float) -> Transaction:
        # Get account from repository
        account = self.account_repository.find_by_id(account_id)
        if not account:
            raise ValueError(f"Account with ID {account_id} not found")

        # Perform withdrawal
        transaction = account.withdraw(amount)

        # Save transaction to repository
        self.transaction_repository.save(transaction)

        # Update account in repository
        self.account_repository.save(account)

        return transaction