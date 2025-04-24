import unittest
from datetime import datetime
from unittest.mock import patch

from domain.accounts import Account, CheckingAccount, SavingsAccount, AccountStatus, AccountType, BusinessRuleService
from domain.transactions import Transaction, TransactionType


class TestCheckingAccount(unittest.TestCase):
    def setUp(self):
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

    def test_deposit_negative_amount(self):
        with self.assertRaises(ValueError):
            self.account.deposit(-50.0)

    def test_withdraw(self):
        initial_balance = self.account.balance
        amount = 100.0

        transaction = self.account.withdraw(amount)

        self.assertEqual(self.account.balance, initial_balance - amount)
        self.assertEqual(transaction.amount, amount)
        self.assertEqual(transaction.transaction_type, TransactionType.WITHDRAW)

    def test_withdraw_negative_amount(self):
        with self.assertRaises(ValueError):
            self.account.withdraw(-50.0)

    def test_withdraw_insufficient_funds(self):
        with self.assertRaises(ValueError):
            self.account.withdraw(self.account.balance + 100.0)

    def test_can_withdraw(self):
        self.assertTrue(self.account.can_withdraw(self.account.balance))
        self.assertTrue(self.account.can_withdraw(self.account.balance - 1))
        self.assertFalse(self.account.can_withdraw(self.account.balance + 1))


class TestSavingsAccount(unittest.TestCase):
    def setUp(self):
        self.account = SavingsAccount("S12345", "testuser", "password123", 500.0)

    def test_initialization(self):
        self.assertEqual(self.account.account_id, "S12345")
        self.assertEqual(self.account.username, "testuser")
        self.assertEqual(self.account.get_balance(), 500.0)
        self.assertEqual(self.account.account_type, AccountType.SAVINGS)
        self.assertEqual(self.account.status, AccountStatus.ACTIVE)
        self.assertIsInstance(self.account.creation_date, datetime)

    def test_can_withdraw_with_minimum_balance(self):
        # Should be able to withdraw to minimum balance
        withdrawable_amount = self.account.balance - SavingsAccount.MINIMUM_BALANCE
        self.assertTrue(self.account.can_withdraw(withdrawable_amount))

        # Should not be able to withdraw below minimum balance
        self.assertFalse(self.account.can_withdraw(withdrawable_amount + 0.01))

    def test_withdraw_respects_minimum_balance(self):
        # Should succeed: withdrawing to minimum balance
        withdrawable_amount = self.account.balance - SavingsAccount.MINIMUM_BALANCE
        transaction = self.account.withdraw(withdrawable_amount)
        self.assertEqual(self.account.balance, SavingsAccount.MINIMUM_BALANCE)

        # Should fail: withdrawing below minimum balance
        with self.assertRaises(ValueError):
            self.account.withdraw(0.01)


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
    unittest.main()