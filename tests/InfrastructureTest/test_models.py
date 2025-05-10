import unittest
from datetime import datetime
from unittest.mock import patch
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from infrastructure.database.db import Base
from infrastructure.database.models import AccountModel, TransactionModel, AccountConstraintsModel


class TestModels(unittest.TestCase):
    def setUp(self):
        # Create an in-memory SQLite database for testing
        self.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    def tearDown(self):
        self.session.close()
        Base.metadata.drop_all(self.engine)

    def test_account_model_creation(self):
        # Test AccountModel creation and default values
        account = AccountModel(
            account_id="ACC123",
            account_type="CHECKING",
            username="testuser",
            password_hash="hashed_password",
            balance=1000.0,
            status="ACTIVE"
        )

        self.session.add(account)
        self.session.commit()

        # Query the account
        saved_account = self.session.query(AccountModel).filter_by(account_id="ACC123").first()
        self.assertIsNotNone(saved_account)
        self.assertEqual(saved_account.account_id, "ACC123")
        self.assertEqual(saved_account.account_type, "CHECKING")
        self.assertEqual(saved_account.username, "testuser")
        self.assertEqual(saved_account.password_hash, "hashed_password")
        self.assertEqual(saved_account.balance, 1000.0)
        self.assertEqual(saved_account.status, "ACTIVE")
        self.assertIsInstance(saved_account.creation_date, datetime)

    def test_account_model_default_values(self):
        # Test AccountModel with minimal required fields
        account = AccountModel(
            account_id="ACC124",
            account_type="SAVINGS",
            username="testuser2",
            password_hash="hashed_password2"
        )

        self.session.add(account)
        self.session.commit()

        saved_account = self.session.query(AccountModel).filter_by(account_id="ACC124").first()
        self.assertEqual(saved_account.balance, 0.0)
        self.assertEqual(saved_account.status, "ACTIVE")
        self.assertIsInstance(saved_account.creation_date, datetime)

    def test_transaction_model_creation(self):
        # First create an account
        account = AccountModel(
            account_id="ACC125",
            account_type="CHECKING",
            username="testuser3",
            password_hash="hashed_password3"
        )

        # Create a transaction
        transaction = TransactionModel(
            transaction_id="TXN123",
            transaction_type="DEPOSIT",
            amount=500.0,
            account_id="ACC125"
        )

        self.session.add(account)
        self.session.add(transaction)
        self.session.commit()

        saved_transaction = self.session.query(TransactionModel).filter_by(transaction_id="TXN123").first()
        self.assertIsNotNone(saved_transaction)
        self.assertEqual(saved_transaction.transaction_type, "DEPOSIT")
        self.assertEqual(saved_transaction.amount, 500.0)
        self.assertEqual(saved_transaction.account_id, "ACC125")
        self.assertIsInstance(saved_transaction.timestamp, datetime)
        self.assertIsNone(saved_transaction.source_account_id)
        self.assertIsNone(saved_transaction.destination_account_id)

    def test_transaction_model_relationship(self):
        # Test the relationship between AccountModel and TransactionModel
        account = AccountModel(
            account_id="ACC126",
            account_type="CHECKING",
            username="testuser4",
            password_hash="hashed_password4"
        )

        transaction = TransactionModel(
            transaction_id="TXN124",
            transaction_type="WITHDRAWAL",
            amount=200.0,
            account_id="ACC126"
        )

        self.session.add(account)
        self.session.add(transaction)
        self.session.commit()

        saved_account = self.session.query(AccountModel).filter_by(account_id="ACC126").first()
        self.assertEqual(len(saved_account.transactions), 1)
        self.assertEqual(saved_account.transactions[0].transaction_id, "TXN124")

    def test_account_constraints_model(self):
        # Test AccountConstraintsModel creation
        account = AccountModel(
            account_id="ACC127",
            account_type="CHECKING",
            username="testuser5",
            password_hash="hashed_password5"
        )

        constraints = AccountConstraintsModel(
            account_id="ACC127",
            daily_usage=1000.0,
            monthly_usage=5000.0,
            daily_limit=20000.0,
            monthly_limit=100000.0
        )

        self.session.add(account)
        self.session.add(constraints)
        self.session.commit()

        saved_constraints = self.session.query(AccountConstraintsModel).filter_by(account_id="ACC127").first()
        self.assertIsNotNone(saved_constraints)
        self.assertEqual(saved_constraints.daily_usage, 1000.0)
        self.assertEqual(saved_constraints.monthly_usage, 5000.0)
        self.assertEqual(saved_constraints.daily_limit, 20000.0)
        self.assertEqual(saved_constraints.monthly_limit, 100000.0)

    def test_account_constraints_default_values(self):
        # Test AccountConstraintsModel default values
        account = AccountModel(
            account_id="ACC128",
            account_type="SAVINGS",
            username="testuser6",
            password_hash="hashed_password6"
        )

        constraints = AccountConstraintsModel(
            account_id="ACC128"
        )

        self.session.add(account)
        self.session.add(constraints)
        self.session.commit()

        saved_constraints = self.session.query(AccountConstraintsModel).filter_by(account_id="ACC128").first()
        self.assertEqual(saved_constraints.daily_usage, 0.0)
        self.assertEqual(saved_constraints.monthly_usage, 0.0)
        self.assertEqual(saved_constraints.daily_limit, 10000.0)
        self.assertEqual(saved_constraints.monthly_limit, 50000.0)

    def test_timestamp_default_value(self):
        # Test that timestamp is set correctly
        fixed_timestamp = datetime(2023, 1, 1, 12, 0, 0)

        account = AccountModel(
            account_id="ACC129",
            account_type="CHECKING",
            username="testuser7",
            password_hash="hashed_password7"
        )

        transaction = TransactionModel(
            transaction_id="TXN125",
            transaction_type="TRANSFER",
            amount=300.0,
            account_id="ACC129",
            timestamp=fixed_timestamp
        )

        self.session.add(account)
        self.session.add(transaction)
        self.session.commit()

        saved_transaction = self.session.query(TransactionModel).filter_by(transaction_id="TXN125").first()
        self.assertEqual(saved_transaction.timestamp, fixed_timestamp)


if __name__ == '__main__':
    unittest.main()