import unittest
from datetime import datetime
from sqlalchemy.orm import Session
from domain.transactions import Transaction, TransactionType
from domain.accounts import CheckingAccount
from infrastructure.database.models import TransactionModel
from infrastructure.repositories.transaction_repository import TransactionRepository
from infrastructure.repositories.account_repository import AccountRepository
from tests.InfrastructureTest.test_utils import setup_database, get_test_session, teardown_database


class TestTransactionRepository(unittest.TestCase):
    def setUp(self):
        # Set up the in-memory database before each test
        setup_database()
        self.session = get_test_session()
        self.account_repo = AccountRepository(self.session)
        self.transaction_repo = TransactionRepository(self.session)

    def tearDown(self):
        # Close the session and tear down the database after each test
        self.session.close()
        teardown_database()

    def test_save_transaction(self):
        # Arrange: Create an account first
        account = CheckingAccount(account_id="acc1", initial_balance=500.0)
        self.account_repo.create_account(account)

        # Create a transaction
        transaction = Transaction(
            transaction_type=TransactionType.DEPOSIT,
            amount=100.0,
            account_id="acc1",
            timestamp=datetime.now()
        )

        # Act
        transaction_id = self.transaction_repo.save_transaction(transaction)

        # Assert
        self.assertEqual(transaction_id, transaction.get_transaction_id())
        db_transaction = self.session.query(TransactionModel).filter(TransactionModel.transaction_id == transaction_id).first()
        self.assertIsNotNone(db_transaction)
        self.assertEqual(db_transaction.transaction_type, TransactionType.DEPOSIT)
        self.assertEqual(db_transaction.amount, 100.0)
        self.assertEqual(db_transaction.account_id, "acc1")

    def test_get_transactions_for_account(self):
        # Arrange: Create an account
        account = CheckingAccount(account_id="acc2", initial_balance=500.0)
        self.account_repo.create_account(account)

        # Create two transactions
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
        self.transaction_repo.save_transaction(transaction1)
        self.transaction_repo.save_transaction(transaction2)

        # Act
        transactions = self.transaction_repo.get_transactions_for_account("acc2")

        # Assert
        self.assertEqual(len(transactions), 2)
        self.assertEqual(transactions[0].get_transaction_id(), transaction1.get_transaction_id())
        self.assertEqual(transactions[0].get_amount(), 200.0)
        self.assertEqual(transactions[0].get_transaction_type(), TransactionType.DEPOSIT)
        self.assertEqual(transactions[1].get_transaction_id(), transaction2.get_transaction_id())
        self.assertEqual(transactions[1].get_amount(), 50.0)
        self.assertEqual(transactions[1].get_transaction_type(), TransactionType.WITHDRAW)

    def test_get_transactions_for_account_no_transactions(self):
        # Arrange: Create an account with no transactions
        account = CheckingAccount(account_id="acc3", initial_balance=500.0)
        self.account_repo.create_account(account)

        # Act
        transactions = self.transaction_repo.get_transactions_for_account("acc3")

        # Assert
        self.assertEqual(len(transactions), 0)

if __name__ == "__main__":
    unittest.main()