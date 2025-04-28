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
    mock_logging_service = MagicMock()  # Add mock for LoggingService
    service = TransactionService(mock_transaction_repo, mock_account_repo, mock_notification_service, mock_logging_service)

    mock_account = MagicMock(spec=Account)
    mock_transaction = MagicMock(spec=Transaction)
    mock_transaction.transaction_id = "tx123"  # Add transaction_id for logging
    mock_account.deposit.return_value = mock_transaction
    mock_account_repo.get_by_id.return_value = mock_account

    transaction = service.deposit("acc1", 100.0)

    # Existing assertions
    mock_account_repo.get_by_id.assert_called_with("acc1")
    mock_account.deposit.assert_called_with(100.0)
    mock_transaction_repo.save.assert_called_with(mock_transaction)
    mock_account_repo.save.assert_called_with(mock_account)
    assert transaction == mock_transaction

    # Optional: Verify logging calls
    mock_logging_service.log_service_call.assert_any_call(
        service_name="TransactionService",
        method_name="deposit",
        status="started",
        duration_ms=0,
        params={"account_id": "acc1", "amount": 100.0}
    )
    mock_logging_service.log_transaction.assert_called_once_with(
        transaction_id="tx123",
        transaction_type="DEPOSIT",
        amount=100.0,
        account_id="acc1",
        status="success"
    )
    mock_logging_service.log_service_call.assert_any_call(
        service_name="TransactionService",
        method_name="deposit",
        status="success",
        duration_ms=mock_logging_service.log_service_call.call_args[1]["duration_ms"],
        params={"account_id": "acc1", "amount": 100.0},
        result=f"Transaction ID: {mock_transaction.transaction_id}"
    )


def test_deposit_non_existing_account():
    mock_account_repo = MagicMock()
    mock_transaction_repo = MagicMock()
    mock_notification_service = MagicMock(spec=NotificationService)
    mock_logging_service = MagicMock()  # Add mock for LoggingService
    service = TransactionService(mock_transaction_repo, mock_account_repo, mock_notification_service, mock_logging_service)
    mock_account_repo.get_by_id.return_value = None

    with pytest.raises(ValueError, match="Account with ID acc1 not found"):
        service.deposit("acc1", 100.0)

    # Optional: Verify logging call for failure
    mock_logging_service.log_service_call.assert_any_call(
        service_name="TransactionService",
        method_name="deposit",
        status="started",
        duration_ms=0,
        params={"account_id": "acc1", "amount": 100.0}
    )
    mock_logging_service.log_service_call.assert_any_call(
        service_name="TransactionService",
        method_name="deposit",
        status="failed",
        duration_ms=mock_logging_service.log_service_call.call_args[1]["duration_ms"],
        params={"account_id": "acc1", "amount": 100.0},
        error="Account with ID acc1 not found"
    )


def test_withdraw_success():
    mock_account_repo = MagicMock()
    mock_transaction_repo = MagicMock()
    mock_notification_service = MagicMock(spec=NotificationService)
    mock_logging_service = MagicMock()  # Add mock for LoggingService
    service = TransactionService(mock_transaction_repo, mock_account_repo, mock_notification_service, mock_logging_service)

    mock_account = MagicMock(spec=Account)
    mock_transaction = MagicMock(spec=Transaction)
    mock_transaction.transaction_id = "tx456"  # Add transaction_id for logging
    mock_account.withdraw.return_value = mock_transaction
    mock_account_repo.get_by_id.return_value = mock_account

    transaction = service.withdraw("acc1", 50.0)

    # Existing assertions
    mock_account_repo.get_by_id.assert_called_with("acc1")
    mock_account.withdraw.assert_called_with(50.0)
    mock_transaction_repo.save.assert_called_with(mock_transaction)
    mock_account_repo.save.assert_called_with(mock_account)
    assert transaction == mock_transaction

    # Optional: Verify logging calls
    mock_logging_service.log_service_call.assert_any_call(
        service_name="TransactionService",
        method_name="withdraw",
        status="started",
        duration_ms=0,
        params={"account_id": "acc1", "amount": 50.0}
    )
    mock_logging_service.log_transaction.assert_called_once_with(
        transaction_id="tx456",
        transaction_type="WITHDRAW",
        amount=50.0,
        account_id="acc1",
        status="success"
    )
    mock_logging_service.log_service_call.assert_any_call(
        service_name="TransactionService",
        method_name="withdraw",
        status="success",
        duration_ms=mock_logging_service.log_service_call.call_args[1]["duration_ms"],
        params={"account_id": "acc1", "amount": 50.0},
        result=f"Transaction ID: {mock_transaction.transaction_id}"
    )


def test_withdraw_non_existing_account():
    mock_account_repo = MagicMock()
    mock_transaction_repo = MagicMock()
    mock_notification_service = MagicMock(spec=NotificationService)
    mock_logging_service = MagicMock()  # Add mock for LoggingService
    service = TransactionService(mock_transaction_repo, mock_account_repo, mock_notification_service, mock_logging_service)
    mock_account_repo.get_by_id.return_value = None

    with pytest.raises(ValueError, match="Account with ID acc1 not found"):
        service.withdraw("acc1", 50.0)

    # Optional: Verify logging call for failure
    mock_logging_service.log_service_call.assert_any_call(
        service_name="TransactionService",
        method_name="withdraw",
        status="started",
        duration_ms=0,
        params={"account_id": "acc1", "amount": 50.0}
    )
    mock_logging_service.log_service_call.assert_any_call(
        service_name="TransactionService",
        method_name="withdraw",
        status="failed",
        duration_ms=mock_logging_service.log_service_call.call_args[1]["duration_ms"],
        params={"account_id": "acc1", "amount": 50.0},
        error="Account with ID acc1 not found"
    )