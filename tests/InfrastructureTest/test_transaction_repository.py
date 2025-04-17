import unittest
from datetime import datetime
from sqlalchemy.orm import Session

from domain.checking_account import CheckingAccount
from domain.transactions import Transaction, TransactionType

from infrastructure.database.models import TransactionModel
from infrastructure.repositories.transaction_repository import TransactionRepository
from infrastructure.repositories.account_repository import AccountRepository
from tests.InfrastructureTest.test_utils import setup_database, get_test_session, teardown_database


class TestTransactionRepository(unittest.TestCase):
    def setUp(self):
        # Set up the in-memory database before each test
        setup_database()
        self.session: Session = get_test_session()
        self.account_repo = AccountRepository(self.session)
        self.transaction_repo = TransactionRepository(self.session)

    def tearDown(self):
        # Close the session and tear down the database after each test
        self.session.close()
        teardown_database()

    def test_save_transaction(self):
        # Arrange
        account = CheckingAccount(account_id="acc1", initial_balance=500.0)
        self.account_repo.create_account(account)

        transaction = Transaction(
            transaction_type=TransactionType.DEPOSIT,
            amount=100.0,
            account_id="acc1",
            timestamp=datetime.now()
        )

        # Act
        transaction_id = self.transaction_repo.save(transaction)

        # Assert
        self.assertEqual(transaction_id, transaction.get_transaction_id())
        db_transaction = self.session.query(TransactionModel).filter(
            TransactionModel.transaction_id == transaction_id
        ).first()
        self.assertIsNotNone(db_transaction)
        self.assertEqual(db_transaction.transaction_type, TransactionType.DEPOSIT)
        self.assertEqual(db_transaction.amount, 100.0)
        self.assertEqual(db_transaction.account_id, "acc1")

    def test_get_transactions_for_account(self):
        # Arrange
        account = CheckingAccount(account_id="acc2", initial_balance=500.0)
        self.account_repo.create_account(account)

        transaction1 = Transaction(
            transaction_type=TransactionType.DEPOSIT,
            amount=200.0,
            account_id="acc2",
            timestamp=datetime.now()
        )
        transaction2 = Transaction(
            transaction_type=TransactionType.WITHDRAW,
            amount=50.0,
            account_id="acc2",
            timestamp=datetime.now()
        )

        self.transaction_repo.save(transaction1)
        self.transaction_repo.save(transaction2)

        # Act
        transactions = self.transaction_repo.get_by_account_id("acc2")

        # Assert
        self.assertEqual(len(transactions), 2)

        ids = [t.get_transaction_id() for t in transactions]
        self.assertIn(transaction1.get_transaction_id(), ids)
        self.assertIn(transaction2.get_transaction_id(), ids)

    def test_get_transactions_for_account_no_transactions(self):
        # Arrange
        account = CheckingAccount(account_id="acc3", initial_balance=300.0)
        self.account_repo.create_account(account)

        # Act
        transactions = self.transaction_repo.get_by_account_id("acc3")

        # Assert
        self.assertEqual(len(transactions), 0)


if __name__ == "__main__":
    unittest.main()
