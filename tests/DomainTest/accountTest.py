import unittest
from unittest.mock import Mock
from domain.checking_account import CheckingAccount, CheckingAccountType
from domain.savings_account import SavingsAccount, SavingsAccountType
from domain.transactions import Transaction

class TestAccount(unittest.TestCase):
    def setUp(self):
<<<<<<< HEAD
        self.account = CheckingAccount("C12345", "testuser", "password123", 500.0)

    def test_initialization(self):
        self.assertEqual(self.account.account_id, "C12345")
        self.assertEqual(self.account.username, "testuser")
        self.assertEqual(self.account.get_balance(), 500.0)
        self.assertEqual(self.account.account_type, AccountType.CHECKING)
        self.assertEqual(self.account.status, AccountStatus.ACTIVE)
        self.assertIsInstance(self.account.creation_date, datetime)

    def test_password_verification(self):
        self.assertTrue(self.account.verify_password("password123"))
        self.assertFalse(self.account.verify_password("wrongpassword"))

    def test_deposit(self):
        initial_balance = self.account.balance
        amount = 100.0

        transaction = self.account.deposit(amount)

        self.assertEqual(self.account.balance, initial_balance + amount)
        self.assertEqual(transaction.amount, amount)
        self.assertEqual(transaction.transaction_type, TransactionType.DEPOSIT)
        self.assertEqual(transaction.account_id, self.account.account_id)

        # Check that transaction was added to history
        transactions = self.account.get_transactions()
        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0], transaction)
=======
        # Set up a checking account for general tests
        self.account = CheckingAccount(
            account_id="acc123",
            username="user1",
            password="password123",
            initial_balance=0.0
        )

    def test_initialization(self):
        """Test that an account is initialized correctly."""
        self.assertEqual(self.account.account_id, "acc123")
        self.assertEqual(self.account.account_type.name, "CHECKING")
        self.assertEqual(self.account.username, "user1")
        self.assertEqual(self.account.get_balance(), 0.0)
        self.assertEqual(self.account.status.name, "ACTIVE")
        self.assertTrue(self.account.verify_password("password123"))
        self.assertFalse(self.account.verify_password("wrongpassword"))

    def test_deposit_positive_amount(self):
        """Test depositing a positive amount."""
        transaction = self.account.deposit(100.0)
        self.assertEqual(self.account.get_balance(), 100.0)
        self.assertEqual(len(self.account.get_transactions()), 1)
        self.assertEqual(transaction.transaction_type.name, "DEPOSIT")
        self.assertEqual(transaction.amount, 100.0)
>>>>>>> c761c5edffc07abf770bfbaa78990093ce673367

    def test_deposit_negative_amount(self):
        """Test depositing a negative amount raises an error."""
        with self.assertRaises(ValueError):
            self.account.deposit(-50.0)

    def test_withdraw_valid_amount(self):
        """Test withdrawing a valid amount."""
        self.account.deposit(100.0)
        transaction = self.account.withdraw(50.0)
        self.assertEqual(self.account.get_balance(), 50.0)
        self.assertEqual(len(self.account.get_transactions()), 2)
        self.assertEqual(transaction.transaction_type.name, "WITHDRAW")
        self.assertEqual(transaction.amount, 50.0)

    def test_withdraw_exceeds_balance(self):
        """Test withdrawing more than the balance raises an error."""
        self.account.deposit(50.0)
        with self.assertRaises(ValueError):
            self.account.withdraw(100.0)

    def test_withdraw_negative_amount(self):
        """Test withdrawing a negative amount raises an error."""
        self.account.deposit(100.0)
        with self.assertRaises(ValueError):
            self.account.withdraw(-50.0)

    def test_transfer_valid_amount(self):
        """Test transferring a valid amount."""
        other_account = CheckingAccount(
            account_id="acc456",
            username="user2",
            password="password456",
            initial_balance=0.0
        )
        self.account.deposit(100.0)
        transaction = self.account.transfer(50.0, other_account)
        self.assertEqual(self.account.get_balance(), 50.0)
        self.assertEqual(other_account.get_balance(), 50.0)
        self.assertEqual(len(self.account.get_transactions()), 2)
        self.assertEqual(len(other_account.get_transactions()), 1)
        self.assertEqual(transaction.transaction_type.name, "TRANSFER")
        self.assertEqual(transaction.amount, 50.0)

    def test_transfer_exceeds_balance(self):
        """Test transferring more than the balance raises an error."""
        other_account = CheckingAccount(
            account_id="acc456",
            username="user2",
            password="password456",
            initial_balance=0.0
        )
        self.account.deposit(50.0)
        with self.assertRaises(ValueError):
            self.account.transfer(100.0, other_account)

    def test_transfer_negative_amount(self):
        """Test transferring a negative amount raises an error."""
        other_account = CheckingAccount(
            account_id="acc456",
            username="user2",
            password="password456",
            initial_balance=0.0
        )
        self.account.deposit(100.0)
        with self.assertRaises(ValueError):
            self.account.transfer(-50.0, other_account)

    def test_password_verification(self):
        """Test password verification."""
        self.assertTrue(self.account.verify_password("password123"))
        self.assertFalse(self.account.verify_password("wrongpassword"))

    def test_observer_notification(self):
        """Test observer notification on transaction."""
        observer = Mock()
        self.account.add_observer(observer)
        self.account.deposit(100.0)
        observer.assert_called_once()
        args = observer.call_args[0]
        self.assertIsInstance(args[0], Transaction)
        self.assertEqual(args[0].transaction_type.name, "DEPOSIT")

    def test_transaction_history(self):
        """Test transaction history recording."""
        self.account.deposit(100.0)
        self.account.withdraw(50.0)
        transactions = self.account.get_transactions()
        self.assertEqual(len(transactions), 2)
        self.assertEqual(transactions[0].transaction_type.name, "DEPOSIT")
        self.assertEqual(transactions[1].transaction_type.name, "WITHDRAW")

class TestSavingsAccount(unittest.TestCase):
    def setUp(self):
<<<<<<< HEAD
        self.account = SavingsAccount("S12345", "testuser", "password123", 500.0)

    def test_initialization(self):
        self.assertEqual(self.account.account_id, "S12345")
        self.assertEqual(self.account.username, "testuser")
        self.assertEqual(self.account.get_balance(), 500.0)
        self.assertEqual(self.account.account_type, AccountType.SAVINGS)
        self.assertEqual(self.account.status, AccountStatus.ACTIVE)
        self.assertIsInstance(self.account.creation_date, datetime)
=======
        # Set up a savings account with a minimum balance of 100.0
        self.account = SavingsAccount(
            account_id="acc789",
            username="user2",
            password="password456",
            initial_balance=200.0
        )

    def test_savings_withdraw_above_minimum(self):
        """Test withdrawing keeps balance above minimum."""
        transaction = self.account.withdraw(50.0)
        self.assertEqual(self.account.get_balance(), 150.0)
        self.assertEqual(transaction.transaction_type.name, "WITHDRAW")
        self.assertEqual(transaction.amount, 50.0)
>>>>>>> c761c5edffc07abf770bfbaa78990093ce673367

    def test_savings_withdraw_below_minimum(self):
        """Test withdrawing below minimum balance raises an error."""
        with self.assertRaises(ValueError):
            self.account.withdraw(150.0)  # Would bring balance to 50.0 < 100.0

<<<<<<< HEAD

class TestBusinessRuleService(unittest.TestCase):
    def setUp(self):
        self.checking = CheckingAccount("C12345", "testuser", "password123", 500.0)
        self.savings = SavingsAccount("S12345", "testuser", "password123", 500.0)
        self.service = BusinessRuleService()

    def test_check_withdraw_allowed(self):
        # Checking account
        self.assertTrue(self.service.check_withdraw_allowed(self.checking, 500.0))
        self.assertFalse(self.service.check_withdraw_allowed(self.checking, 500.01))

        # Savings account
        withdrawable_amount = self.savings.balance - SavingsAccount.MINIMUM_BALANCE
        self.assertTrue(self.service.check_withdraw_allowed(self.savings, withdrawable_amount))
        self.assertFalse(self.service.check_withdraw_allowed(self.savings, withdrawable_amount + 0.01))

    def test_validate_deposit_amount(self):
        self.assertTrue(self.service.validate_deposit_amount(1.0))
        self.assertTrue(self.service.validate_deposit_amount(0.01))
        self.assertFalse(self.service.validate_deposit_amount(0.0))
        self.assertFalse(self.service.validate_deposit_amount(-1.0))


if __name__ == '__main__':
=======
if __name__ == "__main__":
>>>>>>> c761c5edffc07abf770bfbaa78990093ce673367
    unittest.main()