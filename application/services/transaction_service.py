from Group5_SWConstruction.Domain.account import Account
from Group5_SWConstruction.Domain.transactions import Transaction

class TransactionService:
    def deposit(self, account: Account, amount: float) -> Transaction:
        return account.deposit(amount)

    def withdraw(self, account: Account, amount: float) -> Transaction:
        return account.withdraw(amount)
