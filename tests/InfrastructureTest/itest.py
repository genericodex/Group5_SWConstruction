import os
import json
import unittest
import shutil
from datetime import datetime
from uuid import uuid4

from domain.accounts import CheckingAccount, SavingsAccount, Account, AccountType, AccountStatus
from domain.transactions import Transaction, TransactionType
from infrastructure.repositories.FileTransactionRepository import FileTransactionRepository
from infrastructure.repositories.file_account_repository import FileAccountRepository

from infrastructure.storage.file_storage_service import FileStorageService
from infrastructure.factories.repository_factory import RepositoryFactory


class TestFileStorageService(unittest.TestCase):
    """Tests for the FileStorageService class"""

    def setUp(self):
        self.test_dir = "test_data"
        self.storage_service = FileStorageService(self.test_dir)

    def tearDown(self):
        # Clean up test directory after tests
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_get_storage_dir(self):
        """Test creating and getting a storage directory"""
        storage_dir = self.storage_service.get_storage_dir("test_entity")

        # Check that directory exists and is correct
        self.assertTrue(os.path.exists(storage_dir))
        self.assertEqual(storage_dir, os.path.join(self.test_dir, "test_entity"))

    def test_save_load_file(self):
        """Test saving and loading data"""
        test_data = {"id": "test123", "name": "Test Entity", "value": 42}

        # Save data
        self.storage_service.save_to_file("test123", "test_entities", test_data)

        # Load data back
        loaded_data = self.storage_service.load_from_file("test123", "test_entities")

        # Check that loaded data matches original
        self.assertEqual(loaded_data, test_data)

    def test_load_nonexistent_file(self):
        """Test loading a file that doesn't exist"""
        loaded_data = self.storage_service.load_from_file("nonexistent", "test_entities")
        self.assertIsNone(loaded_data)

    def test_delete_file(self):
        """Test deleting a file"""
        test_data = {"id": "test123", "name": "Test Entity"}

        # Save data
        self.storage_service.save_to_file("test123", "test_entities", test_data)

        # Delete file
        result = self.storage_service.delete_file("test123", "test_entities")
        self.assertTrue(result)

        # Check that file no longer exists
        file_path = os.path.join(self.test_dir, "test_entities", "test123.json")
        self.assertFalse(os.path.exists(file_path))

    def test_delete_nonexistent_file(self):
        """Test deleting a file that doesn't exist"""
        result = self.storage_service.delete_file("nonexistent", "test_entities")
        self.assertFalse(result)

    def test_list_all_ids(self):
        """Test listing all entity IDs"""
        # Create some test data
        self.storage_service.save_to_file("id1", "test_entities", {"id": "id1"})
        self.storage_service.save_to_file("id2", "test_entities", {"id": "id2"})
        self.storage_service.save_to_file("id3", "test_entities", {"id": "id3"})

        # Get list of IDs
        ids = self.storage_service.list_all_ids("test_entities")

        # Check that all IDs are present
        self.assertEqual(set(ids), {"id1", "id2", "id3"})


class TestFileAccountRepository(unittest.TestCase):
    """Tests for the FileAccountRepository class"""

    def setUp(self):
        self.test_dir = "test_accounts"
        self.repo = FileAccountRepository(self.test_dir)

    def tearDown(self):
        # Clean up test directory after tests
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_save_and_find_checking_account(self):
        """Test saving and retrieving a checking account"""
        # Create a checking account
        account_id = str(uuid4())
        account = CheckingAccount(account_id, 500.0)

        # Save account
        self.repo.save(account)

        # Retrieve account
        retrieved_account = self.repo.find_by_id(account_id)

        # Check that retrieved account matches original
        self.assertIsNotNone(retrieved_account)
        self.assertEqual(retrieved_account.account_id, account_id)
        self.assertEqual(retrieved_account.account_type, AccountType.CHECKING)
        self.assertEqual(retrieved_account.balance, 500.0)
        self.assertEqual(retrieved_account.status, AccountStatus.ACTIVE)

    def test_save_and_find_savings_account(self):
        """Test saving and retrieving a savings account"""
        # Create a savings account
        account_id = str(uuid4())
        account = SavingsAccount(account_id, 1000.0)

        # Save account
        self.repo.save(account)

        # Retrieve account
        retrieved_account = self.repo.find_by_id(account_id)

        # Check that retrieved account matches original
        self.assertIsNotNone(retrieved_account)
        self.assertEqual(retrieved_account.account_id, account_id)
        self.assertEqual(retrieved_account.account_type, AccountType.SAVINGS)
        self.assertEqual(retrieved_account.balance, 1000.0)
        self.assertEqual(retrieved_account.status, AccountStatus.ACTIVE)

    def test_update_account(self):
        """Test updating an existing account"""
        # Create and save an account
        account_id = str(uuid4())
        account = CheckingAccount(account_id, 500.0)
        self.repo.save(account)

        # Update account
        account.update_balance(250.0)  # Deposit 250
        self.repo.save(account)

        # Retrieve updated account
        updated_account = self.repo.find_by_id(account_id)

        # Check that balance was updated
        self.assertEqual(updated_account.balance, 750.0)

    def test_find_nonexistent_account(self):
        """Test finding an account that doesn't exist"""
        account = self.repo.find_by_id("nonexistent-id")
        self.assertIsNone(account)

    def test_delete_account(self):
        """Test deleting an account"""
        # Create and save an account
        account_id = str(uuid4())
        account = CheckingAccount(account_id, 500.0)
        self.repo.save(account)

        # Delete account
        self.repo.delete(account_id)

        # Check that account no longer exists
        deleted_account = self.repo.find_by_id(account_id)
        self.assertIsNone(deleted_account)

    def test_delete_nonexistent_account(self):
        """Test deleting an account that doesn't exist"""
        with self.assertRaises(ValueError):
            self.repo.delete("nonexistent-id")

    def test_find_all_accounts(self):
        """Test finding all accounts"""
        # Create and save multiple accounts
        account1 = CheckingAccount(str(uuid4()), 500.0)
        account2 = SavingsAccount(str(uuid4()), 1000.0)
        account3 = CheckingAccount(str(uuid4()), 750.0)

        self.repo.save(account1)
        self.repo.save(account2)
        self.repo.save(account3)

        # Find all accounts
        accounts = self.repo.find_all()

        # Check that all accounts are retrieved
        self.assertEqual(len(accounts), 3)

        # Check that accounts have correct types
        account_types = [a.account_type for a in accounts]
        self.assertEqual(account_types.count(AccountType.CHECKING), 2)
        self.assertEqual(account_types.count(AccountType.SAVINGS), 1)

    def test_account_with_transactions(self):
        """Test saving and retrieving an account with transactions"""
        # Create an account
        account_id = str(uuid4())
        account = CheckingAccount(account_id, 1000.0)

        # Add some transactions
        deposit = Transaction(TransactionType.DEPOSIT, 500.0, account_id)
        withdraw = Transaction(TransactionType.WITHDRAW, 200.0, account_id)

        account._transactions.append(deposit)
        account._transactions.append(withdraw)

        # Save account
        self.repo.save(account)

        # Retrieve account
        retrieved_account = self.repo.find_by_id(account_id)

        # Check that transactions were saved and retrieved
        self.assertEqual(len(retrieved_account._transactions), 2)

        # Check transaction details
        txns = retrieved_account._transactions
        self.assertEqual(txns[0].transaction_type, TransactionType.DEPOSIT)
        self.assertEqual(txns[0].amount, 500.0)
        self.assertEqual(txns[1].transaction_type, TransactionType.WITHDRAW)
        self.assertEqual(txns[1].amount, 200.0)


class TestFileTransactionRepository(unittest.TestCase):
    """Tests for the FileTransactionRepository class"""

    def setUp(self):
        self.test_dir = "test_transactions"
        self.repo = FileTransactionRepository(self.test_dir)

    def tearDown(self):
        # Clean up test directory after tests
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_save_and_find_transaction(self):
        """Test saving and retrieving a transaction"""
        # Create a transaction
        account_id = str(uuid4())
        transaction = Transaction(TransactionType.DEPOSIT, 500.0, account_id)
        transaction_id = transaction.transaction_id

        # Save transaction
        self.repo.save(transaction)

        # Retrieve transaction
        retrieved_transaction = self.repo.find_by_id(transaction_id)

        # Check that retrieved transaction matches original
        self.assertIsNotNone(retrieved_transaction)
        self.assertEqual(retrieved_transaction.transaction_id, transaction_id)
        self.assertEqual(retrieved_transaction.transaction_type, TransactionType.DEPOSIT)
        self.assertEqual(retrieved_transaction.amount, 500.0)
        self.assertEqual(retrieved_transaction.account_id, account_id)

    def test_find_transactions_by_account(self):
        """Test finding transactions by account ID"""
        # Create multiple transactions for the same account
        account_id = str(uuid4())
        txn1 = Transaction(TransactionType.DEPOSIT, 500.0, account_id)
        txn2 = Transaction(TransactionType.WITHDRAW, 200.0, account_id)
        txn3 = Transaction(TransactionType.DEPOSIT, 300.0, account_id)

        # Create a transaction for a different account
        other_account_id = str(uuid4())
        other_txn = Transaction(TransactionType.DEPOSIT, 1000.0, other_account_id)

        # Save all transactions
        self.repo.save(txn1)
        self.repo.save(txn2)
        self.repo.save(txn3)
        self.repo.save(other_txn)

        # Find transactions by account ID
        account_transactions = self.repo.find_by_account_id(account_id)

        # Check that only transactions for the specified account are returned
        self.assertEqual(len(account_transactions), 3)

        # Check transaction details
        transaction_amounts = [t.amount for t in account_transactions]
        self.assertIn(500.0, transaction_amounts)
        self.assertIn(200.0, transaction_amounts)
        self.assertIn(300.0, transaction_amounts)

    def test_find_all_transactions(self):
        """Test finding all transactions"""
        # Create and save multiple transactions
        account1_id = str(uuid4())
        account2_id = str(uuid4())

        txn1 = Transaction(TransactionType.DEPOSIT, 500.0, account1_id)
        txn2 = Transaction(TransactionType.WITHDRAW, 200.0, account1_id)
        txn3 = Transaction(TransactionType.DEPOSIT, 1000.0, account2_id)

        self.repo.save(txn1)
        self.repo.save(txn2)
        self.repo.save(txn3)

        # Find all transactions
        transactions = self.repo.find_all()

        # Check that all transactions are retrieved
        self.assertEqual(len(transactions), 3)

        # Check that transactions have correct types
        txn_types = [t.transaction_type for t in transactions]
        self.assertEqual(txn_types.count(TransactionType.DEPOSIT), 2)
        self.assertEqual(txn_types.count(TransactionType.WITHDRAW), 1)


class TestRepositoryFactory(unittest.TestCase):
    """Tests for the RepositoryFactory class"""

    def setUp(self):
        self.test_dir = "test_factory_data"
        self.factory = RepositoryFactory(self.test_dir)

    def tearDown(self):
        # Clean up test directory after tests
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_get_instance_singleton(self):
        """Test that get_instance returns a singleton"""
        factory1 = RepositoryFactory.get_instance()
        factory2 = RepositoryFactory.get_instance()

        # Both should be the same instance
        self.assertIs(factory1, factory2)

    def test_get_account_repository(self):
        """Test getting an account repository"""
        account_repo = self.factory.get_account_repository()

        # Should return a FileAccountRepository
        self.assertIsInstance(account_repo, FileAccountRepository)

        # Should return the same instance when called again
        account_repo2 = self.factory.get_account_repository()
        self.assertIs(account_repo, account_repo2)

    def test_get_transaction_repository(self):
        """Test getting a transaction repository"""
        transaction_repo = self.factory.get_transaction_repository()

        # Should return a FileTransactionRepository
        self.assertIsInstance(transaction_repo, FileTransactionRepository)

        # Should return the same instance when called again
        transaction_repo2 = self.factory.get_transaction_repository()
        self.assertIs(transaction_repo, transaction_repo2)


class TestIntegration(unittest.TestCase):
    """Integration tests for the infrastructure layer"""

    def setUp(self):
        self.test_dir = "test_integration_data"
        self.factory = RepositoryFactory(self.test_dir)
        self.account_repo = self.factory.get_account_repository()
        self.transaction_repo = self.factory.get_transaction_repository()

    def tearDown(self):
        # Clean up test directory after tests
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_account_with_transactions_workflow(self):
        """Test a complete workflow with accounts and transactions"""
        # Create a checking account
        account_id = str(uuid4())
        account = CheckingAccount(account_id, 1000.0)
        self.account_repo.save(account)

        # Create and save transactions
        deposit = Transaction(TransactionType.DEPOSIT, 500.0, account_id)
        self.transaction_repo.save(deposit)

        withdraw = Transaction(TransactionType.WITHDRAW, 300.0, account_id)
        self.transaction_repo.save(withdraw)

        # Retrieve account and update balance
        retrieved_account = self.account_repo.find_by_id(account_id)
        retrieved_account.update_balance(deposit.amount)
        retrieved_account.update_balance(-withdraw.amount)
        self.account_repo.save(retrieved_account)

        # Get transactions for account
        account_transactions = self.transaction_repo.find_by_account_id(account_id)

        # Check transactions
        self.assertEqual(len(account_transactions), 2)

        # Check final account balance
        final_account = self.account_repo.find_by_id(account_id)
        self.assertEqual(final_account.balance, 1200.0)  # 1000 + 500 - 300


if __name__ == "__main__":
    unittest.main()