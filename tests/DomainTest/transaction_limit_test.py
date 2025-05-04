import unittest
from unittest.mock import patch
from datetime import datetime, date
from domain.transaction_limits import TransactionLimits
from domain.transactions import Transaction, DepositTransactionType

class TransactionLimitsTest(unittest.TestCase):
    def setUp(self):
        self.daily_limit = 1000.0
        self.monthly_limit = 5000.0
        self.limits = TransactionLimits(daily_limit=self.daily_limit, monthly_limit=self.monthly_limit)
        self.account_id = "acc_123"
        self.fixed_date = datetime(2025, 5, 1)

    @patch('domain.transaction_limits.datetime')
    def test_transaction_within_limits(self, mock_datetime):
        mock_datetime.now.return_value = self.fixed_date
        mock_datetime.date.return_value = self.fixed_date.date()

        # Test a transaction within limits
        result = self.limits.can_process_transaction(self.account_id, 500.0)
        self.assertTrue(result)

        # Record the transaction
        transaction = Transaction(
            transaction_type=DepositTransactionType(),
            amount=500.0,
            account_id=self.account_id,
            timestamp=self.fixed_date
        )
        self.limits.record_transaction(transaction)

        # Verify totals
        self.assertEqual(self.limits.daily_totals[date(2025, 5, 1)], 500.0)
        self.assertEqual(self.limits.monthly_totals[date(2025, 5, 1)], 500.0)

    @patch('domain.transaction_limits.datetime')
    def test_exceed_daily_limit(self, mock_datetime):
        mock_datetime.now.return_value = self.fixed_date
        mock_datetime.date.return_value = self.fixed_date.date()

        # Record a transaction that uses most of the daily limit
        transaction = Transaction(
            transaction_type=DepositTransactionType(),
            amount=900.0,
            account_id=self.account_id,
            timestamp=self.fixed_date
        )
        self.limits.record_transaction(transaction)

        # Test a transaction that exceeds the daily limit
        result = self.limits.can_process_transaction(self.account_id, 200.0)
        self.assertFalse(result)

    @patch('domain.transaction_limits.datetime')
    def test_exceed_monthly_limit(self, mock_datetime):
        mock_datetime.now.return_value = self.fixed_date
        mock_datetime.date.return_value = self.fixed_date.date()

        # Record a transaction that uses most of the monthly limit
        transaction = Transaction(
            transaction_type=DepositTransactionType(),
            amount=4900.0,
            account_id=self.account_id,
            timestamp=self.fixed_date
        )
        self.limits.record_transaction(transaction)

        # Test a transaction that exceeds the monthly limit
        result = self.limits.can_process_transaction(self.account_id, 200.0)
        self.assertFalse(result)

    @patch('domain.transaction_limits.datetime')
    def test_new_day_resets_daily_total(self, mock_datetime):
        # Simulate first day
        mock_datetime.now.return_value = self.fixed_date
        mock_datetime.date.return_value = self.fixed_date.date()
        transaction = Transaction(
            transaction_type=DepositTransactionType(),
            amount=500.0,
            account_id=self.account_id,
            timestamp=self.fixed_date
        )
        self.limits.record_transaction(transaction)

        # Simulate next day
        next_day = datetime(2025, 5, 2)
        mock_datetime.now.return_value = next_day
        mock_datetime.date.return_value = next_day.date()

        # Test a new transaction on the next day
        result = self.limits.can_process_transaction(self.account_id, 500.0)
        self.assertTrue(result)

        # Record and verify daily total reset
        transaction = Transaction(
            transaction_type=DepositTransactionType(),
            amount=500.0,
            account_id=self.account_id,
            timestamp=next_day
        )
        self.limits.record_transaction(transaction)
        self.assertEqual(self.limits.daily_totals[date(2025, 5, 2)], 500.0)
        self.assertEqual(self.limits.daily_totals[date(2025, 5, 1)], 500.0)  # Old total preserved
        self.assertEqual(self.limits.monthly_totals[date(2025, 5, 1)], 1000.0)  # Monthly accumulates

if __name__ == '__main__':
    unittest.main()