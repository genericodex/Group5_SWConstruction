from typing import Optional
from sqlalchemy.orm import Session

from application.BankApplicationLayer import AccountRepository, TransactionRepository
from domain.transactions import Transaction
from domain.accounts import Account
from fastapi import HTTPException





class FundTransferService:
    def __init__(self, account_repo: AccountRepository, transaction_repo: TransactionRepository):
        self.account_repo = account_repo
        self.transaction_repo = transaction_repo

    def transfer_funds(self, from_account_id: str, to_account_id: str, amount: float) -> str:
        """
        Transfer funds from one account to another.

        :param from_account_id: The ID of the source account.
        :param to_account_id: The ID of the target account.
        :param amount: Amount of funds to transfer.
        :return: A transfer transaction ID for reference.
        """

        if amount <= 0:
            raise HTTPException(status_code=400, detail="Transfer amount must be greater than zero.")

        # Retrieve source and target accounts
        from_account: Optional[Account] = self.account_repo.get_account_by_id(from_account_id)
        to_account: Optional[Account] = self.account_repo.get_account_by_id(to_account_id)

        if not from_account:
            raise HTTPException(status_code=404, detail=f"Source account '{from_account_id}' not found.")
        if not to_account:
            raise HTTPException(status_code=404, detail=f"Target account '{to_account_id}' not found.")

        # Validate sufficient balance in source account
        if from_account.balance < amount:
            raise HTTPException(status_code=400, detail="Insufficient funds in source account.")

        # Perform the transfer
        from_account.balance -= amount
        to_account.balance += amount

        # Update the accounts in the database
        self.account_repo.update_account(from_account)
        self.account_repo.update_account(to_account)

        # Log the transaction
        transfer_transaction = Transaction(
            transaction_type="TRANSFER",
            amount=amount,
            source_account_id=from_account_id,
            target_account_id=to_account_id
        )
        transaction_id = self.transaction_repo.create_transaction(transfer_transaction)

        return transaction_id
