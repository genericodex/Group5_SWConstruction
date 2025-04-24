import unittest
from unittest.mock import MagicMock, create_autospec
from application.repositories.account_repository import IAccountRepository
from application.repositories.transaction_repository import ITransactionRepository
from application.services.fund_transfer import FundTransferService
from application.services.notification_service import NotificationService
from application.exceptions.exceptions import AccountNotFoundError, InvalidTransferError
from domain.accounts import Account
from domain.transactions import Transaction


class TestFundTransferService(unittest.TestCase):
    def setUp(self):
        self.account_repo = create_autospec(IAccountRepository)
        self.transaction_repo = create_autospec(ITransactionRepository)
        self.notification_service = create_autospec(NotificationService)

        self.service = FundTransferService(
            self.account_repo,
            self.transaction_repo,
            self.notification_service
        )

    def test_successful_transfer(self):
        from_account = MagicMock(spec=Account)
        to_account = MagicMock(spec=Account)

        from_account.account_id = "acc1"
        to_account.account_id = "acc2"
        from_account.balance = 1000
        to_account.balance = 500

        transaction = MagicMock(spec=Transaction)
        transaction.transaction_id = "tx123"
        transaction.amount = 200
        transaction.from_account_id = "acc1"
        transaction.to_account_id = "acc2"
        transaction.transaction_type = "TRANSFER"

        from_account.transfer.return_value = transaction

        self.account_repo.get_by_id.side_effect = lambda x: from_account if x == "acc1" else to_account

        result = self.service.transfer_funds("acc1", "acc2", 200)

        # Assertions
        self.assertEqual(result, "tx123")
        from_account.transfer.assert_called_once_with(200, to_account)
        self.account_repo.save.assert_any_call(from_account)
        self.account_repo.save.assert_any_call(to_account)
        self.transaction_repo.save.assert_called_once_with(transaction)

        self.assertEqual(transaction.amount, 200)
        self.assertEqual(transaction.from_account_id, "acc1")
        self.assertEqual(transaction.to_account_id, "acc2")
        self.assertEqual(transaction.transaction_type, "TRANSFER")

    def test_insufficient_funds(self):
        from_account = MagicMock(spec=Account)
        to_account = MagicMock(spec=Account)
        from_account.transfer.side_effect = ValueError("Insufficient funds for transfer")

        self.account_repo.get_by_id.side_effect = lambda x: from_account if x == "acc1" else to_account

        with self.assertRaises(InvalidTransferError) as context:
            self.service.transfer_funds("acc1", "acc2", 9999)

        self.assertEqual(str(context.exception), "Insufficient funds for transfer")

    def test_source_account_not_found(self):
        self.account_repo.get_by_id.side_effect = lambda x: None if x == "acc1" else MagicMock(spec=Account)

        with self.assertRaises(AccountNotFoundError) as context:
            self.service.transfer_funds("acc1", "acc2", 100)

        self.assertEqual(str(context.exception), "Source account 'acc1' not found.")

    def test_target_account_not_found(self):
        self.account_repo.get_by_id.side_effect = lambda x: MagicMock(spec=Account) if x == "acc1" else None

        with self.assertRaises(AccountNotFoundError) as context:
            self.service.transfer_funds("acc1", "acc2", 100)

        self.assertEqual(str(context.exception), "Target account 'acc2' not found.")

    def test_invalid_transfer_amount_zero(self):
        from_account = MagicMock(spec=Account)
        to_account = MagicMock(spec=Account)
        from_account.transfer.side_effect = ValueError("Transfer amount must be positive")

        self.account_repo.get_by_id.side_effect = lambda x: from_account if x == "acc1" else to_account

        with self.assertRaises(InvalidTransferError) as context:
            self.service.transfer_funds("acc1", "acc2", 0)

        self.assertEqual(str(context.exception), "Transfer amount must be positive")

    def test_invalid_transfer_amount_negative(self):
        from_account = MagicMock(spec=Account)
        to_account = MagicMock(spec=Account)
        from_account.transfer.side_effect = ValueError("Transfer amount must be positive")

        self.account_repo.get_by_id.side_effect = lambda x: from_account if x == "acc1" else to_account

        with self.assertRaises(InvalidTransferError) as context:
            self.service.transfer_funds("acc1", "acc2", -50)

        self.assertEqual(str(context.exception), "Transfer amount must be positive")


if __name__ == '__main__':
    unittest.main()
