from typing import List
from sqlalchemy.orm import Session
from application.repositories.transaction_repository import ITransactionRepository
from domain.transactions import Transaction, TransactionType
from infrastructure.database.models import TransactionModel


class TransactionRepository(ITransactionRepository):
    def __init__(self, db: Session):
        self.db = db

    def save_transaction(self, transaction: Transaction) -> str:
        db_transaction = TransactionModel(
            transaction_id=transaction.get_transaction_id(),
            transaction_type=transaction.get_transaction_type(),
            amount=transaction.get_amount(),
            account_id=transaction.account_id,
            timestamp=transaction.timestamp
        )
        self.db.add(db_transaction)
        self.db.commit()
        self.db.refresh(db_transaction)
        return db_transaction.transaction_id

    def get_transactions_for_account(self, account_id: str) -> List[Transaction]:
        db_transactions = self.db.query(TransactionModel).filter(TransactionModel.account_id == account_id).all()
        transactions = []
        for db_txn in db_transactions:
            transaction = Transaction(
                transaction_type=db_txn.transaction_type,
                amount=db_txn.amount,
                account_id=db_txn.account_id,
                timestamp=db_txn.timestamp
            )
            # Set the transaction_id (since Transaction's __post_init__ would normally generate it)
            transaction.transaction_id = db_txn.transaction_id
            transactions.append(transaction)
        return transactions