import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from domain.monthly_statement import MonthlyStatement
from domain.savings_account import SavingsAccount

from domain.transactions import (
    Transaction, DepositTransactionType, WithdrawTransactionType, TransferTransactionType
)
from domain.interest import SavingsInterestStrategy

class MonthlyStatementTest(unittest.TestCase):
    def setUp(self):
        # Fixed dates for testing
        self.start_date = datetime(2025, 5, 1)
        self.end_date = datetime(2025, 5, 31)
        self.account_id = "acc_123"
        self.username = "test_user"
        self.password = "password123"

        # Create a mock SavingsAccount
        self.account = SavingsAccount(
            account_id=self.account_id,
            username=self.username,
            password=self.password,
            initial_balance=1000.0
        )
        self.account.set_interest_strategy(SavingsInterestStrategy(annual_rate=0.025))  # 2.5%
        self.account._transactions = []  # Clear transactions for each test

        # Mock datetime for consistent testing
        self.patcher = patch('domain.accounts.datetime')
        self.mock_datetime = self.patcher.start()
        self.mock_datetime.now.return_value = self.start_date

    def tearDown(self):
        self.patcher.stop()

    def test_generate_statement_with_multiple_transactions(self):
        # Arrange: Add transactions to the account
        transactions = [
            Transaction(
                transaction_type=DepositTransactionType(),
                amount=500.0,
                account_id=self.account_id,
                timestamp=datetime(2025, 5, 2)
            ),
            Transaction(
                transaction_type=WithdrawTransactionType(),
                amount=200.0,
                account_id=self.account_id,
                timestamp=datetime(2025, 5, 3)
            ),
            Transaction(
                transaction_type=TransferTransactionType(),
                amount=100.0,
                account_id=self.account_id,
                source_account_id=self.account_id,
                destination_account_id="acc_456",
                timestamp=datetime(2025, 5, 4)
            )
        ]
        self.account._transactions = transactions
        self.account._balance = 1200.0  # 1000 + 500 - 200 - 100

        # Act: Generate the statement
        statement = self.account.generate_monthly_statement(self.start_date, self.end_date)

        # Assert: Verify statement details
        self.assertEqual(statement.account_id, self.account_id)
        self.assertEqual(statement.statement_period, "May 2025")
        self.assertEqual(statement.start_date, self.start_date)
        self.assertEqual(statement.end_date, self.end_date)
        self.assertEqual(statement.starting_balance, 1000.0)  # Corrected: 1200 - (500 - 200 - 100)
        self.assertEqual(statement.ending_balance, 1200.0)
        self.assertEqual(len(statement.transactions), 3)
        self.assertAlmostEqual(
            statement.interest_earned,
            1200.0 * (0.025 / 365) * 30,  # Use 30 days for May 1 to May 31
            places=5
        )

        # Verify transaction summaries
        self.assertEqual(statement.total_deposits, 500.0)
        self.assertEqual(statement.total_withdrawals, 200.0)
        self.assertEqual(statement.total_transfers_out, 100.0)
        self.assertEqual(statement.total_transfers_in, 0.0)

    def test_generate_statement_with_no_transactions(self):
        # Arrange: No transactions in the period
        self.account._transactions = []
        self.account._balance = 1000.0

        # Act: Generate the statement
        statement = self.account.generate_monthly_statement(self.start_date, self.end_date)

        # Assert: Verify statement details
        self.assertEqual(statement.account_id, self.account_id)
        self.assertEqual(statement.starting_balance, 1000.0)
        self.assertEqual(statement.ending_balance, 1000.0)
        self.assertEqual(len(statement.transactions), 0)
        self.assertAlmostEqual(
            statement.interest_earned,
            1000.0 * (0.025 / 365) * 30,  # 30 days of interest
            places=5
        )
        self.assertEqual(statement.total_deposits, 0.0)
        self.assertEqual(statement.total_withdrawals, 0.0)
        self.assertEqual(statement.total_transfers_in, 0.0)
        self.assertEqual(statement.total_transfers_out, 0.0)

    def test_generate_statement_with_transactions_outside_period(self):
        # Arrange: Add a transaction outside the period
        transaction = Transaction(
            transaction_type=DepositTransactionType(),
            amount=500.0,
            account_id=self.account_id,
            timestamp=datetime(2025, 4, 30)  # Before period
        )
        self.account._transactions = [transaction]
        self.account._balance = 1500.0

        # Act: Generate the statement
        statement = self.account.generate_monthly_statement(self.start_date, self.end_date)

        # Assert: Verify statement ignores out-of-period transaction
        self.assertEqual(statement.starting_balance, 1500.0)  # Current balance (no transactions in period)
        self.assertEqual(statement.ending_balance, 1500.0)
        self.assertEqual(len(statement.transactions), 0)
        self.assertAlmostEqual(
            statement.interest_earned,
            1500.0 * (0.025 / 365) * 30,
            places=5
        )

    def test_generate_statement_with_transfer_in(self):
        # Arrange: Add a transfer-in transaction
        transaction = Transaction(
            transaction_type=TransferTransactionType(),
            amount=300.0,
            account_id=self.account_id,
            source_account_id="acc_456",
            destination_account_id=self.account_id,
            timestamp=datetime(2025, 5, 5)
        )
        self.account._transactions = [transaction]
        self.account._balance = 1300.0  # 1000 + 300

        # Act: Generate the statement
        statement = self.account.generate_monthly_statement(self.start_date, self.end_date)

        # Assert: Verify transfer-in is counted
        self.assertEqual(statement.starting_balance, 1000.0)  # 1300 - 300
        self.assertEqual(statement.ending_balance, 1300.0)
        self.assertEqual(len(statement.transactions), 1)
        self.assertEqual(statement.total_transfers_in, 300.0)
        self.assertEqual(statement.total_transfers_out, 0.0)

    def test_generate_statement_no_interest_strategy(self):
        # Arrange: Remove interest strategy
        self.account.interest_strategy = None
        self.account._transactions = []
        self.account._balance = 1000.0

        # Act: Generate the statement
        statement = self.account.generate_monthly_statement(self.start_date, self.end_date)

        # Assert: Verify no interest is earned
        self.assertEqual(statement.interest_earned, 0.0)
        self.assertEqual(statement.starting_balance, 1000.0)
        self.assertEqual(statement.ending_balance, 1000.0)

    def test_generate_statement_edge_case_same_day(self):
        # Arrange: Same start and end date
        same_day = datetime(2025, 5, 1)
        self.account._transactions = []
        self.account._balance = 1000.0

        # Act: Generate the statement
        statement = self.account.generate_monthly_statement(same_day, same_day)

        # Assert: Verify zero interest and correct balances
        self.assertEqual(statement.starting_balance, 1000.0)
        self.assertEqual(statement.ending_balance, 1000.0)
        self.assertEqual(statement.interest_earned, 0.0)
        self.assertEqual(len(statement.transactions), 0)

if __name__ == '__main__':
    unittest.main()