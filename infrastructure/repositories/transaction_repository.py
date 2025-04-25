from typing import List, Optional
import logging
from sqlalchemy.orm import Session
from application.repositories.transaction_repository import ITransactionRepository
from domain.transactions import Transaction
from domain.transactions import DepositTransactionType, WithdrawTransactionType, TransferTransactionType
from infrastructure.database.models import TransactionModel
from application.services.logging_service import LoggingService

# Decorator for logging method calls
def log_method(func):
    def wrapper(*args, **kwargs):
        logger.info(f"Calling {func.__name__} with args: {args[1:]}, kwargs: {kwargs}")
        result = func(*args, **kwargs)
        logger.info(f"Completed {func.__name__}, result: {result}")
        return result
    return wrapper

logger = logging.getLogger(__name__)

class TransactionRepository(ITransactionRepository):
    def __init__(self, db: Session, logging_service: Optional[LoggingService] = None):
        self.db = db
        self.logging_service = logging_service

    @log_method
    def save(self, transaction: Transaction) -> str:
        # Get the type name from the transaction_type object
        transaction_type_name = transaction.transaction_type.name

        # Use a specific logger for this transaction type
        transaction_logger = logging.getLogger(f"transaction.{transaction_type_name.lower()}")
        transaction_logger.info(f"Saving transaction: {transaction.transaction_id}, type: {transaction_type_name}")

        db_transaction = TransactionModel(
            transaction_id=transaction.transaction_id,
            transaction_type=transaction_type_name,  # Store as string
            amount=transaction.amount,
            account_id=transaction.account_id,
            timestamp=transaction.timestamp
        )

        # Add transfer-specific fields if it's a transfer transaction
        if transaction_type_name == "TRANSFER":
            db_transaction.source_account_id = transaction.source_account_id
            db_transaction.destination_account_id = transaction.destination_account_id

        self.db.add(db_transaction)
        self.db.commit()
        self.db.refresh(db_transaction)

        # Log the transaction if logging service is available
        if self.logging_service:
            details = {}
            if transaction_type_name == "TRANSFER":
                details = {
                    "source_account_id": transaction.source_account_id,
                    "destination_account_id": transaction.destination_account_id
                }

            self.logging_service.log_transaction(
                transaction_id=transaction.transaction_id,
                transaction_type=transaction_type_name,
                amount=transaction.amount,
                account_id=transaction.account_id,
                status="completed",
                details=details
            )

        return db_transaction.transaction_id

    @log_method
    def get_by_id(self, transaction_id: str) -> Optional[Transaction]:
        db_transaction = self.db.query(TransactionModel).filter(
            TransactionModel.transaction_id == transaction_id).first()
        if not db_transaction:
            return None

        # Create appropriate transaction type object based on string value
        transaction_type = None
        if db_transaction.transaction_type == "DEPOSIT":
            transaction_type = DepositTransactionType()
        elif db_transaction.transaction_type == "WITHDRAW":
            transaction_type = WithdrawTransactionType()
        elif db_transaction.transaction_type == "TRANSFER":
            transaction_type = TransferTransactionType()

        # Include source and destination account IDs for transfer transactions
        transaction = Transaction(
            transaction_type=transaction_type,
            amount=db_transaction.amount,
            account_id=db_transaction.account_id,
            timestamp=db_transaction.timestamp,
            source_account_id=db_transaction.source_account_id if db_transaction.transaction_type == "TRANSFER" else None,
            destination_account_id=db_transaction.destination_account_id if db_transaction.transaction_type == "TRANSFER" else None
        )

        transaction.transaction_id = db_transaction.transaction_id
        return transaction

    @log_method
    def get_by_account_id(self, account_id: str) -> List[Transaction]:
        db_transactions = self.db.query(TransactionModel).filter(
            (TransactionModel.account_id == account_id) |
            (TransactionModel.source_account_id == account_id) |
            (TransactionModel.destination_account_id == account_id)
        ).all()

        transactions = []
        for db_txn in db_transactions:
            # Create appropriate transaction type object based on string value
            transaction_type = None
            if db_txn.transaction_type == "DEPOSIT":
                transaction_type = DepositTransactionType()
            elif db_txn.transaction_type == "WITHDRAW":
                transaction_type = WithdrawTransactionType()
            elif db_txn.transaction_type == "TRANSFER":
                transaction_type = TransferTransactionType()

            # Include source and destination account IDs for transfer transactions
            transaction = Transaction(
                transaction_type=transaction_type,
                amount=db_txn.amount,
                account_id=db_txn.account_id,
                timestamp=db_txn.timestamp,
                source_account_id=db_txn.source_account_id if db_txn.transaction_type == "TRANSFER" else None,
                destination_account_id=db_txn.destination_account_id if db_txn.transaction_type == "TRANSFER" else None
            )

            transaction.transaction_id = db_txn.transaction_id
            transactions.append(transaction)

        return transactions

    @log_method
    def get_all(self) -> List[Transaction]:
        db_transactions = self.db.query(TransactionModel).all()
        transactions = []

        for db_txn in db_transactions:
            # Create appropriate transaction type object based on string value
            transaction_type = None
            if db_txn.transaction_type == "DEPOSIT":
                transaction_type = DepositTransactionType()
            elif db_txn.transaction_type == "WITHDRAW":
                transaction_type = WithdrawTransactionType()
            elif db_txn.transaction_type == "TRANSFER":
                transaction_type = TransferTransactionType()

            # Include source and destination account IDs for transfer transactions
            transaction = Transaction(
                transaction_type=transaction_type,
                amount=db_txn.amount,
                account_id=db_txn.account_id,
                timestamp=db_txn.timestamp,
                source_account_id=db_txn.source_account_id if db_txn.transaction_type == "TRANSFER" else None,
                destination_account_id=db_txn.destination_account_id if db_txn.transaction_type == "TRANSFER" else None
            )

            transaction.transaction_id = db_txn.transaction_id
            transactions.append(transaction)

        return transactions