import unittest
from unittest.mock import MagicMock
from datetime import datetime
from sqlalchemy.orm import Session
from infrastructure.database.models import AccountModel
from domain.accounts import ActiveStatus, ClosedStatus
from domain.checking_account import CheckingAccount, CheckingAccountType
from domain.savings_account import SavingsAccount, SavingsAccountType
from infrastructure.repositories.account_repository import AccountRepository


class TestAccountRepository(unittest.TestCase):
    def setUp(self):
        # Mock the database session
        self.db_session = MagicMock(spec=Session)
        self.repo = AccountRepository(self.db_session)

    def test_create_account_checking(self):
        # Arrange
        account = CheckingAccount(
            account_id="chk_001",
            username="testuser",
            password="pass123",
            initial_balance=500.0
        )
        account.creation_date = datetime.now()
        account.status = ActiveStatus()

        # Mock database interactions
        self.db_session.add.return_value = None
        self.db_session.commit.return_value = None
        self.db_session.refresh.return_value = None

        # Act
        result = self.repo.create_account(account)

        # Assert
        self.assertEqual(result, "chk_001")
        self.db_session.add.assert_called_once()
        self.db_session.commit.assert_called_once()
        self.db_session.refresh.assert_called_once()
        added_account = self.db_session.add.call_args[0][0]
        self.assertEqual(added_account.account_type, "CHECKING")
        self.assertEqual(added_account.status, "ACTIVE")
        self.assertEqual(added_account.balance, 500.0)

    def test_create_account_savings(self):
        # Arrange
        account = SavingsAccount(
            account_id="sav_001",
            username="testuser",
            password="pass123",
            initial_balance=1000.0
        )
        account.creation_date = datetime.now()
        account.status = ActiveStatus()

        # Mock database interactions
        self.db_session.add.return_value = None
        self.db_session.commit.return_value = None
        self.db_session.refresh.return_value = None

        # Act
        result = self.repo.create_account(account)

        # Assert
        self.assertEqual(result, "sav_001")
        self.db_session.add.assert_called_once()
        self.db_session.commit.assert_called_once()
        self.db_session.refresh.assert_called_once()
        added_account = self.db_session.add.call_args[0][0]
        self.assertEqual(added_account.account_type, "SAVINGS")
        self.assertEqual(added_account.status, "ACTIVE")
        self.assertEqual(added_account.balance, 1000.0)

    def test_get_account_by_id_checking(self):
        # Arrange
        db_account = AccountModel(
            account_id="chk_001",
            account_type="CHECKING",
            username="testuser",
            password_hash="hashed_pass",
            balance=750.0,
            status="ACTIVE",
            creation_date=datetime.now()
        )
        self.db_session.query.return_value.filter.return_value.first.return_value = db_account

        # Act
        result = self.repo.get_account_by_id("chk_001")

        # Assert
        self.assertIsInstance(result, CheckingAccount)
        self.assertEqual(result.account_id, "chk_001")
        self.assertEqual(result.get_balance(), 750.0)
        self.assertEqual(result._password_hash, "hashed_pass")
        self.assertIsInstance(result.account_type, CheckingAccountType)
        self.assertIsInstance(result.status, ActiveStatus)

    def test_get_account_by_id_savings(self):
        # Arrange
        db_account = AccountModel(
            account_id="sav_001",
            account_type="SAVINGS",
            username="testuser",
            password_hash="hashed_pass",
            balance=1500.0,
            status="ACTIVE",
            creation_date=datetime.now()
        )
        self.db_session.query.return_value.filter.return_value.first.return_value = db_account

        # Act
        result = self.repo.get_account_by_id("sav_001")

        # Assert
        self.assertIsInstance(result, SavingsAccount)
        self.assertEqual(result.account_id, "sav_001")
        self.assertEqual(result.get_balance(), 1500.0)
        self.assertEqual(result._password_hash, "hashed_pass")
        self.assertIsInstance(result.account_type, SavingsAccountType)
        self.assertIsInstance(result.status, ActiveStatus)

    def test_get_account_by_id_not_found(self):
        # Arrange
        self.db_session.query.return_value.filter.return_value.first.return_value = None

        # Act
        result = self.repo.get_account_by_id("non_existent")

        # Assert
        self.assertIsNone(result)

    def test_update_account(self):
        # Arrange
        account = CheckingAccount(
            account_id="chk_001",
            username="testuser",
            password="pass123",
            initial_balance=1000.0
        )
        account.update_balance(200.0)  # Balance becomes 1200.0
        account.status = ClosedStatus()
        db_account = AccountModel(
            account_id="chk_001",
            account_type="CHECKING",
            username="testuser",
            password_hash="hashed_pass",
            balance=1000.0,
            status="ACTIVE"
        )
        self.db_session.query.return_value.filter.return_value.first.return_value = db_account

        # Act
        self.repo.update_account(account)

        # Assert
        self.assertEqual(db_account.balance, 1200.0)
        self.assertEqual(db_account.status, "CLOSED")
        self.db_session.commit.assert_called_once()

    def test_save_new_account(self):
        # Arrange
        account = SavingsAccount(
            account_id="sav_001",
            username="testuser",
            password="pass123",
            initial_balance=2000.0
        )
        account.status = ActiveStatus()
        self.db_session.query.return_value.filter.return_value.first.return_value = None
        self.db_session.add.return_value = None
        self.db_session.commit.return_value = None
        self.db_session.refresh.return_value = None

        # Act
        result = self.repo.save(account)

        # Assert
        self.assertEqual(result, "sav_001")
        self.db_session.add.assert_called_once()
        self.db_session.commit.assert_called_once()

    def test_save_existing_account(self):
        # Arrange
        account = CheckingAccount(
            account_id="chk_001",
            username="testuser",
            password="pass123",
            initial_balance=1000.0
        )
        account.update_balance(300.0)  # Balance becomes 1300.0
        account.status = ActiveStatus()
        db_account = AccountModel(
            account_id="chk_001",
            account_type="CHECKING",
            username="testuser",
            password_hash="hashed_pass",
            balance=1000.0,
            status="ACTIVE"
        )
        self.db_session.query.return_value.filter.return_value.first.return_value = db_account

        # Act
        result = self.repo.save(account)

        # Assert
        self.assertEqual(result, "chk_001")
        self.assertEqual(db_account.balance, 1300.0)
        self.assertEqual(db_account.status, "ACTIVE")
        self.db_session.commit.assert_called_once()

    def test_delete_account(self):
        # Arrange
        db_account = AccountModel(account_id="chk_001")
        self.db_session.query.return_value.filter.return_value.first.return_value = db_account

        # Act
        self.repo.delete("chk_001")

        # Assert
        self.db_session.delete.assert_called_once_with(db_account)
        self.db_session.commit.assert_called_once()

    def test_get_all_accounts(self):
        # Arrange
        db_accounts = [
            AccountModel(
                account_id="chk_001",
                account_type="CHECKING",
                username="user1",
                password_hash="hash1",
                balance=1000.0,
                status="ACTIVE",
                creation_date=datetime.now()
            ),
            AccountModel(
                account_id="sav_001",
                account_type="SAVINGS",
                username="user2",
                password_hash="hash2",
                balance=2000.0,
                status="CLOSED",
                creation_date=datetime.now()
            )
        ]
        self.db_session.query.return_value.all.return_value = db_accounts

        # Act
        result = self.repo.get_all()

        # Assert
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], CheckingAccount)
        self.assertIsInstance(result[1], SavingsAccount)
        self.assertEqual(result[0].get_balance(), 1000.0)
        self.assertEqual(result[1].get_balance(), 2000.0)
        self.assertIsInstance(result[0].status, ActiveStatus)
        self.assertIsInstance(result[1].status, ClosedStatus)


if __name__ == '__main__':
    unittest.main()