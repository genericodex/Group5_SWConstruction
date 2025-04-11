import unittest
from sqlalchemy.orm import Session
from domain.accounts import CheckingAccount, SavingsAccount, AccountType, AccountStatus
from infrastructure.database.models import AccountModel
from infrastructure.repositories.account_repository import AccountRepository
from tests.InfrastructureTest.test_utils import setup_database, get_test_session, teardown_database


class TestAccountRepository(unittest.TestCase):
    def setUp(self):
        # Set up the in-memory database before each test
        setup_database()
        self.session = get_test_session()
        self.repo = AccountRepository(self.session)

    def tearDown(self):
        # Close the session and tear down the database after each test
        self.session.close()
        teardown_database()

    def test_create_account_checking(self):
        # Arrange
        account = CheckingAccount(account_id="acc1", initial_balance=500.0)

        # Act
        account_id = self.repo.create_account(account)

        # Assert
        self.assertEqual(account_id, "acc1")
        db_account = self.session.query(AccountModel).filter(AccountModel.account_id == "acc1").first()
        self.assertIsNotNone(db_account)
        self.assertEqual(db_account.account_type, AccountType.CHECKING)
        self.assertEqual(db_account.balance, 500.0)
        self.assertEqual(db_account.status, AccountStatus.ACTIVE)

    def test_create_account_savings(self):
        # Arrange
        account = SavingsAccount(account_id="acc2", initial_balance=1000.0)

        # Act
        account_id = self.repo.create_account(account)

        # Assert
        self.assertEqual(account_id, "acc2")
        db_account = self.session.query(AccountModel).filter(AccountModel.account_id == "acc2").first()
        self.assertIsNotNone(db_account)
        self.assertEqual(db_account.account_type, AccountType.SAVINGS)
        self.assertEqual(db_account.balance, 1000.0)
        self.assertEqual(db_account.status, AccountStatus.ACTIVE)

    def test_get_account_by_id_checking(self):
        # Arrange
        account = CheckingAccount(account_id="acc3", initial_balance=300.0)
        self.repo.create_account(account)

        # Act
        retrieved_account = self.repo.get_account_by_id("acc3")

        # Assert
        self.assertIsNotNone(retrieved_account)
        self.assertIsInstance(retrieved_account, CheckingAccount)
        self.assertEqual(retrieved_account.account_id, "acc3")
        self.assertEqual(retrieved_account.balance, 300.0)
        self.assertEqual(retrieved_account.account_type, AccountType.CHECKING)

    def test_get_account_by_id_savings(self):
        # Arrange
        account = SavingsAccount(account_id="acc4", initial_balance=1500.0)
        self.repo.create_account(account)

        # Act
        retrieved_account = self.repo.get_account_by_id("acc4")

        # Assert
        self.assertIsNotNone(retrieved_account)
        self.assertIsInstance(retrieved_account, SavingsAccount)
        self.assertEqual(retrieved_account.account_id, "acc4")
        self.assertEqual(retrieved_account.balance, 1500.0)
        self.assertEqual(retrieved_account.account_type, AccountType.SAVINGS)

    def test_get_account_by_id_not_found(self):
        # Act
        retrieved_account = self.repo.get_account_by_id("non_existent")

        # Assert
        self.assertIsNone(retrieved_account)

    def test_update_account(self):
        # Arrange
        account = CheckingAccount(account_id="acc5", initial_balance=200.0)
        self.repo.create_account(account)

        # Modify the account
        account.update_balance(100.0)  # New balance: 300.0
        account.status = AccountStatus.CLOSED

        # Act
        self.repo.update_account(account)

        # Assert
        db_account = self.session.query(AccountModel).filter(AccountModel.account_id == "acc5").first()
        self.assertEqual(db_account.balance, 300.0)
        self.assertEqual(db_account.status, AccountStatus.CLOSED)

    def test_update_account_not_found(self):
        # Arrange
        account = CheckingAccount(account_id="acc6", initial_balance=200.0)

        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.repo.update_account(account)
        self.assertTrue("Account with ID acc6 not found" in str(context.exception))

if __name__ == "__main__":
    unittest.main()