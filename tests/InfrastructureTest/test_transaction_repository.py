import unittest
from unittest.mock import MagicMock
from datetime import datetime
from sqlalchemy.orm import Session
from infrastructure.database.models import TransactionModel
from infrastructure.repositories.transaction_repository import TransactionRepository
from domain.transactions import Transaction, DepositTransactionType, WithdrawTransactionType, TransferTransactionType
from application.services.logging_service import LoggingService


class TestTransactionRepository(unittest.TestCase):
    def setUp(self):
        # Mock the database session and logging service
        self.db_session = MagicMock(spec=Session)
        self.logging_service = MagicMock(spec=LoggingService)
        self.repo = TransactionRepository(self.db_session, self.logging_service)

    def test_save_deposit_transaction(self):
        # Arrange
        transaction = Transaction(
            transaction_type=DepositTransactionType(),
            amount=100.0,
            account_id="acc_001",
            timestamp=datetime.now()
        )

        # Mock database interactions
        self.db_session.add.return_value = None
        self.db_session.commit.return_value = None
        self.db_session.refresh.return_value = None

        # Act
        result = self.repo.save(transaction)

        # Assert
        self.assertEqual(result, transaction.transaction_id)
        self.db_session.add.assert_called_once()
        self.db_session.commit.assert_called_once()
        self.db_session.refresh.assert_called_once()
        added_transaction = self.db_session.add.call_args[0][0]
        self.assertEqual(added_transaction.transaction_type, "DEPOSIT")
        self.assertEqual(added_transaction.amount, 100.0)
        self.logging_service.log_transaction.assert_called_once_with(
            transaction_id=transaction.transaction_id,
            transaction_type="DEPOSIT",
            amount=100.0,
            account_id="acc_001",
            status="completed",
            details={}
        )

    def test_save_transfer_transaction(self):
        # Arrange
        transaction = Transaction(
            transaction_type=TransferTransactionType(),
            amount=200.0,
            account_id="acc_001",
            timestamp=datetime.now(),
            source_account_id="acc_001",
            destination_account_id="acc_002"
        )

        # Mock database interactions
        self.db_session.add.return_value = None
        self.db_session.commit.return_value = None
        self.db_session.refresh.return_value = None

        # Act
        result = self.repo.save(transaction)

        # Assert
        self.assertEqual(result, transaction.transaction_id)
        self.db_session.add.assert_called_once()
        self.db_session.commit.assert_called_once()
        self.db_session.refresh.assert_called_once()
        added_transaction = self.db_session.add.call_args[0][0]
        self.assertEqual(added_transaction.transaction_type, "TRANSFER")
        self.assertEqual(added_transaction.source_account_id, "acc_001")
        self.assertEqual(added_transaction.destination_account_id, "acc_002")
        self.logging_service.log_transaction.assert_called_once_with(
            transaction_id=transaction.transaction_id,
            transaction_type="TRANSFER",
            amount=200.0,
            account_id="acc_001",
            status="completed",
            details={"source_account_id": "acc_001", "destination_account_id": "acc_002"}
        )

    def test_get_by_id_deposit(self):
        # Arrange
        db_transaction = TransactionModel(
            transaction_id="txn_001",
            transaction_type="DEPOSIT",
            amount=150.0,
            account_id="acc_001",
            timestamp=datetime.now()
        )
        self.db_session.query.return_value.filter.return_value.first.return_value = db_transaction

        # Act
        result = self.repo.get_by_id("txn_001")

        # Assert
        self.assertIsInstance(result, Transaction)
        self.assertEqual(result.transaction_id, "txn_001")
        self.assertIsInstance(result.transaction_type, DepositTransactionType)
        self.assertEqual(result.amount, 150.0)
        self.assertEqual(result.account_id, "acc_001")

    def test_get_by_id_transfer(self):
        # Arrange
        db_transaction = TransactionModel(
            transaction_id="txn_002",
            transaction_type="TRANSFER",
            amount=300.0,
            account_id="acc_001",
            timestamp=datetime.now(),
            source_account_id="acc_001",
            destination_account_id="acc_002"
        )
        self.db_session.query.return_value.filter.return_value.first.return_value = db_transaction

        # Act
        result = self.repo.get_by_id("txn_002")

        # Assert
        self.assertIsInstance(result, Transaction)
        self.assertEqual(result.transaction_id, "txn_002")
        self.assertIsInstance(result.transaction_type, TransferTransactionType)
        self.assertEqual(result.amount, 300.0)
        self.assertEqual(result.source_account_id, "acc_001")
        self.assertEqual(result.destination_account_id, "acc_002")

    def test_get_by_id_not_found(self):
        # Arrange
        self.db_session.query.return_value.filter.return_value.first.return_value = None

        # Act
        result = self.repo.get_by_id("txn_nonexistent")

        # Assert
        self.assertIsNone(result)

    def test_get_by_account_id(self):
        # Arrange
        db_transactions = [
            TransactionModel(
                transaction_id="txn_001",
                transaction_type="DEPOSIT",
                amount=100.0,
                account_id="acc_001",
                timestamp=datetime.now()
            ),
            TransactionModel(
                transaction_id="txn_002",
                transaction_type="TRANSFER",
                amount=200.0,
                account_id="acc_001",
                timestamp=datetime.now(),
                source_account_id="acc_001",
                destination_account_id="acc_002"
            )
        ]
        self.db_session.query.return_value.filter.return_value.all.return_value = db_transactions

        # Act
        result = self.repo.get_by_account_id("acc_001")

        # Assert
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0].transaction_type, DepositTransactionType)
        self.assertIsInstance(result[1].transaction_type, TransferTransactionType)
        self.assertEqual(result[0].amount, 100.0)
        self.assertEqual(result[1].amount, 200.0)
        self.assertEqual(result[1].source_account_id, "acc_001")
        self.assertEqual(result[1].destination_account_id, "acc_002")

    def test_get_all(self):
        # Arrange
        db_transactions = [
            TransactionModel(
                transaction_id="txn_001",
                transaction_type="DEPOSIT",
                amount=100.0,
                account_id="acc_001",
                timestamp=datetime.now()
            ),
            TransactionModel(
                transaction_id="txn_002",
                transaction_type="WITHDRAW",
                amount=50.0,
                account_id="acc_001",
                timestamp=datetime.now()
            ),
            TransactionModel(
                transaction_id="txn_003",
                transaction_type="TRANSFER",
                amount=200.0,
                account_id="acc_001",
                timestamp=datetime.now(),
                source_account_id="acc_001",
                destination_account_id="acc_002"
            )
        ]
        self.db_session.query.return_value.all.return_value = db_transactions

        # Act
        result = self.repo.get_all()

        # Assert
        self.assertEqual(len(result), 3)
        self.assertIsInstance(result[0].transaction_type, DepositTransactionType)
        self.assertIsInstance(result[1].transaction_type, WithdrawTransactionType)
        self.assertIsInstance(result[2].transaction_type, TransferTransactionType)
        self.assertEqual(result[0].amount, 100.0)
        self.assertEqual(result[1].amount, 50.0)
        self.assertEqual(result[2].amount, 200.0)
        self.assertEqual(result[2].source_account_id, "acc_001")
        self.assertEqual(result[2].destination_account_id, "acc_002")


if __name__ == '__main__':
    unittest.main()