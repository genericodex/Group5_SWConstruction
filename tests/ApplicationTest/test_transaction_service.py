import pytest
from unittest.mock import MagicMock
from application.services.transaction_service import TransactionService
from application.services.notification_service import NotificationService
from domain.accounts import Account
from domain.transactions import Transaction


def test_deposit_success():
    mock_account_repo = MagicMock()
    mock_transaction_repo = MagicMock()
    mock_notification_service = MagicMock(spec=NotificationService)
    service = TransactionService(mock_transaction_repo, mock_account_repo, mock_notification_service)

    mock_account = MagicMock(spec=Account)
    mock_transaction = MagicMock(spec=Transaction)
    mock_account.deposit.return_value = mock_transaction
    mock_account_repo.get_by_id.return_value = mock_account

    transaction = service.deposit("acc1", 100.0)

    mock_account_repo.get_by_id.assert_called_with("acc1")
    mock_account.deposit.assert_called_with(100.0)
    mock_transaction_repo.save.assert_called_with(mock_transaction)
    mock_account_repo.save.assert_called_with(mock_account)
    assert transaction == mock_transaction


def test_deposit_non_existing_account():
    mock_account_repo = MagicMock()
    mock_transaction_repo = MagicMock()
    mock_notification_service = MagicMock(spec=NotificationService)
    service = TransactionService(mock_transaction_repo, mock_account_repo, mock_notification_service)
    mock_account_repo.get_by_id.return_value = None

    with pytest.raises(ValueError, match="Account with ID acc1 not found"):
        service.deposit("acc1", 100.0)


def test_withdraw_success():
    mock_account_repo = MagicMock()
    mock_transaction_repo = MagicMock()
    mock_notification_service = MagicMock(spec=NotificationService)
    service = TransactionService(mock_transaction_repo, mock_account_repo, mock_notification_service)

    mock_account = MagicMock(spec=Account)
    mock_transaction = MagicMock(spec=Transaction)
    mock_account.withdraw.return_value = mock_transaction
    mock_account_repo.get_by_id.return_value = mock_account

    transaction = service.withdraw("acc1", 50.0)

    mock_account_repo.get_by_id.assert_called_with("acc1")
    mock_account.withdraw.assert_called_with(50.0)
    mock_transaction_repo.save.assert_called_with(mock_transaction)
    mock_account_repo.save.assert_called_with(mock_account)
    assert transaction == mock_transaction


def test_withdraw_non_existing_account():
    mock_account_repo = MagicMock()
    mock_transaction_repo = MagicMock()
    mock_notification_service = MagicMock(spec=NotificationService)
    service = TransactionService(mock_transaction_repo, mock_account_repo, mock_notification_service)
    mock_account_repo.get_by_id.return_value = None

    with pytest.raises(ValueError, match="Account with ID acc1 not found"):
        service.withdraw("acc1", 50.0)