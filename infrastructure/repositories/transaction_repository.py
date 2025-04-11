from typing import List, Optional
from sqlalchemy.orm import Session
from application.repositories.transaction_repository import ITransactionRepository
from domain.transactions import Transaction, TransactionType
from infrastructure.database.models import TransactionModel


class TransactionRepository(ITransactionRepository):
    def __init__(self, db: Session):
        self.db = db

    def save(self, transaction: Transaction) -> str:
        db_transaction = TransactionModel(
            transaction_id=transaction.get_transaction_id(),  # Use transaction's ID
            transaction_type=transaction.transaction_type,
            amount=transaction.amount,
            account_id=transaction.account_id,
            timestamp=transaction.timestamp
        )
        self.db.add(db_transaction)
        self.db.commit()
        self.db.refresh(db_transaction)
        return db_transaction.transaction_id

    def get_by_id(self, transaction_id: str) -> Optional[Transaction]:
        db_transaction = self.db.query(TransactionModel).filter(TransactionModel.transaction_id == transaction_id).first()
        if not db_transaction:
            return None
        transaction = Transaction(
            transaction_type=db_transaction.transaction_type,
            amount=db_transaction.amount,
            account_id=db_transaction.account_id,
            timestamp=db_transaction.timestamp
        )
        transaction.transaction_id = db_transaction.transaction_id
        return transaction

    def get_by_account_id(self, account_id: str) -> List[Transaction]:
        db_transactions = self.db.query(TransactionModel).filter(TransactionModel.account_id == account_id).all()
        transactions = []
        for db_txn in db_transactions:
            transaction = Transaction(
                transaction_type=db_txn.transaction_type,
                amount=db_txn.amount,
                account_id=db_txn.account_id,
                timestamp=db_txn.timestamp
            )
            transaction.transaction_id = db_txn.transaction_id
            transactions.append(transaction)
        return transactions

    def get_all(self) -> List[Transaction]:
        db_transactions = self.db.query(TransactionModel).all()
        transactions = []
        for db_txn in db_transactions:
            transaction = Transaction(
                transaction_type=db_txn.transaction_type,
                amount=db_txn.amount,
                account_id=db_txn.account_id,
                timestamp=db_txn.timestamp
            )
            transaction.transaction_id = db_txn.transaction_id
            transactions.append(transaction)
        return transactions