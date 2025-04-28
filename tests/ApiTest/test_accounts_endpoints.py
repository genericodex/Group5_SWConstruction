import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from datetime import datetime
from fastapi import FastAPI
from uuid import uuid4

from api.v1.endpoints.accounts import router
from application.services.account_service import AccountCreationService
from application.services.fund_transfer import FundTransferService
from application.services.transaction_service import TransactionService

from application.exceptions.exceptions import AccountNotFoundError, InvalidTransferError
from infrastructure.repositories.account_repository import AccountRepository
from infrastructure.repositories.transaction_repository import TransactionRepository
from domain.checking_account import CheckingAccount
from domain.savings_account import SavingsAccount
from domain.accounts import ActiveStatus, ClosedStatus
from domain.transactions import Transaction, DepositTransactionType, WithdrawTransactionType, TransferTransactionType
from api.dependencies import (
    get_account_creation_service,
    get_transaction_service,
    get_fund_transfer_service,
    get_account_repository,
    get_transaction_repository,
)

# Setup FastAPI TestClient
app = FastAPI()
app.include_router(router)
client = TestClient(app)

# Test Fixtures
@pytest.fixture
def mock_account_creation_service():
    return MagicMock(spec=AccountCreationService)

@pytest.fixture
def mock_transaction_service():
    return MagicMock(spec=TransactionService)

@pytest.fixture
def mock_fund_transfer_service():
    return MagicMock(spec=FundTransferService)

@pytest.fixture
def mock_account_repository():
    return MagicMock(spec=AccountRepository)

@pytest.fixture
def mock_transaction_repository():
    return MagicMock(spec=TransactionRepository)

@pytest.fixture
def mock_checking_account():
    return CheckingAccount(
        account_id=str(uuid4()),
        username="testuser",
        password="password123",
        initial_balance=100.0
    )

@pytest.fixture
def mock_savings_account():
    return SavingsAccount(
        account_id=str(uuid4()),
        username="testuser",
        password="password123",
        initial_balance=SavingsAccount.MINIMUM_BALANCE
    )

@pytest.fixture(autouse=True)
def override_dependencies(
    mock_account_creation_service,
    mock_transaction_service,
    mock_fund_transfer_service,
    mock_account_repository,
    mock_transaction_repository
):
    app.dependency_overrides.update({
        get_account_creation_service: lambda: mock_account_creation_service,
        get_transaction_service: lambda: mock_transaction_service,
        get_fund_transfer_service: lambda: mock_fund_transfer_service,
        get_account_repository: lambda: mock_account_repository,
        get_transaction_repository: lambda: mock_transaction_repository,
    })
    yield
    app.dependency_overrides.clear()

# Account Creation Tests
@pytest.mark.parametrize("account_type, initial_deposit, account_tier, expected_tier", [
    ("checking", 100.0, "standard", "standard"),
    ("savings", SavingsAccount.MINIMUM_BALANCE, "standard", "standard"),
    ("savings", 1000.0, "standard", "premium"),  # Premium tier for high deposit (>=1000.0)
])
def test_create_account_success(mock_account_creation_service, account_type, initial_deposit, account_tier, expected_tier):
    account_id = str(uuid4())
    mock_account_creation_service.create_account.return_value = account_id

    response = client.post(
        "/accounts",
        json={
            "accountType": account_type,
            "username": "testuser",
            "password": "password123",
            "initialDeposit": initial_deposit,
            "accountTier": account_tier
        }
    )

    assert response.status_code == 201
    assert response.json() == {"account_id": account_id}
    mock_account_creation_service.create_account.assert_called_once_with(
        account_type=account_type,
        username="testuser",
        password="password123",
        initial_deposit=initial_deposit,
        account_tier=account_tier  # Use input account_tier, not expected_tier
    )

@pytest.mark.parametrize("account_type", ["invalid_type", ""])
def test_create_account_invalid_type(account_type):
    response = client.post(
        "/accounts",
        json={
            "accountType": account_type,
            "username": "testuser",
            "password": "password123",
            "initialDeposit": 100.0
        }
    )

    assert response.status_code == 400
    assert "Invalid account type" in response.json()["detail"]

def test_create_account_negative_deposit():
    response = client.post(
        "/accounts",
        json={
            "accountType": "checking",
            "username": "testuser",
            "password": "password123",
            "initialDeposit": -100.0
        }
    )

    assert response.status_code == 400
    assert "Initial deposit must be non-negative" in response.json()["detail"]

def test_create_savings_account_below_minimum(mock_account_creation_service):
    mock_account_creation_service.create_account.side_effect = ValueError(
        f"Savings account requires a minimum deposit of ${SavingsAccount.MINIMUM_BALANCE}"
    )

    response = client.post(
        "/accounts",
        json={
            "accountType": "savings",
            "username": "testuser",
            "password": "password123",
            "initialDeposit": SavingsAccount.MINIMUM_BALANCE - 0.01
        }
    )

    assert response.status_code == 400
    assert "minimum deposit" in response.json()["detail"]

def test_create_account_value_error(mock_account_creation_service):
    mock_account_creation_service.create_account.side_effect = ValueError("Invalid username")

    response = client.post(
        "/accounts",
        json={
            "accountType": "checking",
            "username": "",
            "password": "password123",
            "initialDeposit": 100.0
        }
    )

    assert response.status_code == 400
    assert "Invalid username" in response.json()["detail"]

# Deposit Tests
def test_deposit_success(mock_transaction_service, mock_account_repository, mock_checking_account):
    account_id = mock_checking_account.account_id
    transaction_id = str(uuid4())
    mock_transaction = Transaction(
        transaction_type=DepositTransactionType(),
        amount=50.0,
        account_id=account_id,
        timestamp=datetime.now()
    )
    mock_transaction.transaction_id = transaction_id
    mock_transaction_service.deposit.return_value = mock_transaction
    mock_account_repository.get_account_by_id.return_value = mock_checking_account
    mock_checking_account._balance = 150.0

    response = client.post(
        f"/accounts/{account_id}/deposit",
        json={"amount": 50.0}
    )

    assert response.status_code == 200
    assert response.json() == {"balance": 150.0, "transaction_id": transaction_id}
    mock_transaction_service.deposit.assert_called_once_with(account_id, 50.0)

@pytest.mark.parametrize("amount, error_message", [
    (-50.0, "Deposit amount must be positive"),
    (0.0, "Deposit amount must be positive")
])
def test_deposit_invalid_amount(amount, error_message):
    response = client.post(
        "/accounts/acc123/deposit",
        json={"amount": amount}
    )

    assert response.status_code == 400
    assert error_message in response.json()["detail"]

def test_deposit_account_not_found(mock_transaction_service, mock_account_repository):
    account_id = str(uuid4())
    mock_account_repository.get_account_by_id.return_value = None
    mock_transaction_service.deposit.side_effect = ValueError(f"Account with ID {account_id} not found")

    response = client.post(
        f"/accounts/{account_id}/deposit",
        json={"amount": 50.0}
    )

    assert response.status_code == 400
    assert "Account with ID" in response.json()["detail"]

def test_deposit_inactive_account(mock_transaction_service, mock_account_repository, mock_checking_account):
    account_id = mock_checking_account.account_id
    mock_checking_account.status = ClosedStatus()
    mock_account_repository.get_account_by_id.return_value = mock_checking_account
    mock_transaction_service.deposit.side_effect = ValueError("Account is not active")

    response = client.post(
        f"/accounts/{account_id}/deposit",
        json={"amount": 50.0}
    )

    assert response.status_code == 400
    assert "Account is not active" in response.json()["detail"]

# Withdraw Tests
def test_withdraw_checking_success(mock_transaction_service, mock_account_repository, mock_checking_account):
    account_id = mock_checking_account.account_id
    transaction_id = str(uuid4())
    mock_transaction = Transaction(
        transaction_type=WithdrawTransactionType(),
        amount=30.0,
        account_id=account_id,
        timestamp=datetime.now()
    )
    mock_transaction.transaction_id = transaction_id
    mock_transaction_service.withdraw.return_value = mock_transaction
    mock_account_repository.get_account_by_id.return_value = mock_checking_account
    mock_checking_account._balance = 70.0

    response = client.post(
        f"/accounts/{account_id}/withdraw",
        json={"amount": 30.0}
    )

    assert response.status_code == 200
    assert response.json() == {"balance": 70.0, "transaction_id": transaction_id}
    mock_transaction_service.withdraw.assert_called_once_with(account_id, 30.0)

def test_withdraw_savings_success(mock_transaction_service, mock_account_repository, mock_savings_account):
    account_id = mock_savings_account.account_id
    transaction_id = str(uuid4())
    mock_transaction = Transaction(
        transaction_type=WithdrawTransactionType(),
        amount=50.0,
        account_id=account_id,
        timestamp=datetime.now()
    )
    mock_transaction.transaction_id = transaction_id
    mock_transaction_service.withdraw.return_value = mock_transaction
    mock_account_repository.get_account_by_id.return_value = mock_savings_account
    mock_savings_account._balance = SavingsAccount.MINIMUM_BALANCE + 50.0

    response = client.post(
        f"/accounts/{account_id}/withdraw",
        json={"amount": 50.0}
    )

    assert response.status_code == 200
    assert response.json() == {"balance": SavingsAccount.MINIMUM_BALANCE + 50.0, "transaction_id": transaction_id}
    mock_transaction_service.withdraw.assert_called_once_with(account_id, 50.0)

@pytest.mark.parametrize("amount, error_message", [
    (-30.0, "Withdrawal amount must be positive"),
    (0.0, "Withdrawal amount must be positive")
])
def test_withdraw_invalid_amount(amount, error_message):
    response = client.post(
        "/accounts/acc123/withdraw",
        json={"amount": amount}
    )

    assert response.status_code == 400
    assert error_message in response.json()["detail"]

def test_withdraw_checking_insufficient_funds(mock_transaction_service, mock_account_repository, mock_checking_account):
    account_id = mock_checking_account.account_id
    mock_checking_account._balance = 50.0
    mock_transaction_service.withdraw.side_effect = ValueError("Insufficient funds")
    mock_account_repository.get_account_by_id.return_value = mock_checking_account

    response = client.post(
        f"/accounts/{account_id}/withdraw",
        json={"amount": 100.0}
    )

    assert response.status_code == 400
    assert "Insufficient funds" in response.json()["detail"]

def test_withdraw_savings_below_minimum(mock_transaction_service, mock_account_repository, mock_savings_account):
    account_id = mock_savings_account.account_id
    mock_savings_account._balance = SavingsAccount.MINIMUM_BALANCE + 10.0
    mock_transaction_service.withdraw.side_effect = ValueError("Withdrawal amount exceeds available balance")
    mock_account_repository.get_account_by_id.return_value = mock_savings_account

    response = client.post(
        f"/accounts/{account_id}/withdraw",
        json={"amount": 20.0}
    )

    assert response.status_code == 400
    assert "Withdrawal amount exceeds available balance" in response.json()["detail"]

def test_withdraw_inactive_account(mock_transaction_service, mock_account_repository, mock_checking_account):
    account_id = mock_checking_account.account_id
    mock_checking_account.status = ClosedStatus()
    mock_account_repository.get_account_by_id.return_value = mock_checking_account
    mock_transaction_service.withdraw.side_effect = ValueError("Account is not active")

    response = client.post(
        f"/accounts/{account_id}/withdraw",
        json={"amount": 30.0}
    )

    assert response.status_code == 400
    assert "Account is not active" in response.json()["detail"]

# Transfer Tests
def test_transfer_funds_success(mock_fund_transfer_service, mock_account_repository, mock_checking_account, mock_savings_account):
    source_id = mock_checking_account.account_id
    dest_id = mock_savings_account.account_id
    transaction_id = str(uuid4())
    mock_fund_transfer_service.transfer_funds.return_value = transaction_id
    mock_account_repository.get_account_by_id.side_effect = [mock_checking_account, mock_savings_account]
    mock_checking_account._balance = 450.0
    mock_savings_account._balance = SavingsAccount.MINIMUM_BALANCE + 50.0

    response = client.post(
        "/accounts/transfer",
        json={
            "sourceAccountId": source_id,
            "destinationAccountId": dest_id,
            "amount": 50.0
        }
    )

    assert response.status_code == 200
    result = response.json()
    assert result["transaction_id"] == transaction_id
    assert result["source_account"]["account_id"] == source_id
    assert result["source_account"]["balance"] == 450.0
    assert result["destination_account"]["account_id"] == dest_id
    assert result["destination_account"]["balance"] == SavingsAccount.MINIMUM_BALANCE + 50.0
    mock_fund_transfer_service.transfer_funds.assert_called_once_with(
        from_account_id=source_id,
        to_account_id=dest_id,
        amount=50.0
    )

@pytest.mark.parametrize("amount, error_message", [
    (-50.0, "Transfer amount must be positive"),
    (0.0, "Transfer amount must be positive")
])
def test_transfer_invalid_amount(amount, error_message):
    response = client.post(
        "/accounts/transfer",
        json={
            "sourceAccountId": "acc123",
            "destinationAccountId": "acc456",
            "amount": amount
        }
    )

    assert response.status_code == 400
    assert error_message in response.json()["detail"]

def test_transfer_account_not_found(mock_fund_transfer_service):
    source_id = str(uuid4())
    dest_id = str(uuid4())
    mock_fund_transfer_service.transfer_funds.side_effect = AccountNotFoundError(f"Source account '{source_id}' not found")

    response = client.post(
        "/accounts/transfer",
        json={
            "sourceAccountId": source_id,
            "destinationAccountId": dest_id,
            "amount": 50.0
        }
    )

    assert response.status_code == 404
    assert f"Source account '{source_id}' not found" in response.json()["detail"]

def test_transfer_same_account(mock_fund_transfer_service):
    account_id = str(uuid4())
    mock_fund_transfer_service.transfer_funds.side_effect = InvalidTransferError("Cannot transfer to the same account")

    response = client.post(
        "/accounts/transfer",
        json={
            "sourceAccountId": account_id,
            "destinationAccountId": account_id,
            "amount": 50.0
        }
    )

    assert response.status_code == 400
    assert "Cannot transfer to the same account" in response.json()["detail"]

def test_transfer_inactive_account(mock_fund_transfer_service, mock_account_repository, mock_checking_account, mock_savings_account):
    source_id = mock_checking_account.account_id
    dest_id = mock_savings_account.account_id
    mock_checking_account.status = ClosedStatus()
    mock_account_repository.get_account_by_id.side_effect = [mock_checking_account, mock_savings_account]
    mock_fund_transfer_service.transfer_funds.side_effect = InvalidTransferError("One or both accounts are not active")

    response = client.post(
        "/accounts/transfer",
        json={
            "sourceAccountId": source_id,
            "destinationAccountId": dest_id,
            "amount": 50.0
        }
    )

    assert response.status_code == 400
    assert "One or both accounts are not active" in response.json()["detail"]

# Get Balance Tests
def test_get_balance_success(mock_account_repository, mock_checking_account):
    account_id = mock_checking_account.account_id
    mock_checking_account._balance = 500.0
    mock_account_repository.get_account_by_id.return_value = mock_checking_account

    response = client.get(f"/accounts/{account_id}/balance")

    assert response.status_code == 200
    result = response.json()
    assert result["account_id"] == account_id
    assert result["balance"] == 500.0
    assert result["availableBalance"] == 500.0
    assert result["status"] == "ACTIVE"

def test_get_balance_closed_account(mock_account_repository, mock_checking_account):
    account_id = mock_checking_account.account_id
    mock_checking_account.status = ClosedStatus()
    mock_checking_account._balance = 500.0
    mock_account_repository.get_account_by_id.return_value = mock_checking_account

    response = client.get(f"/accounts/{account_id}/balance")

    assert response.status_code == 200
    result = response.json()
    assert result["account_id"] == account_id
    assert result["balance"] == 500.0
    assert result["availableBalance"] == 500.0
    assert result["status"] == "CLOSED"

def test_get_balance_account_not_found(mock_account_repository):
    account_id = str(uuid4())
    mock_account_repository.get_account_by_id.return_value = None

    response = client.get(f"/accounts/{account_id}/balance")

    assert response.status_code == 404
    assert "Account not found" in response.json()["detail"]

# Get Transactions Tests
def test_get_transactions_success(mock_transaction_repository, mock_checking_account):
    account_id = mock_checking_account.account_id
    now = datetime.now()
    mock_transactions = [
        Transaction(
            transaction_type=DepositTransactionType(),
            amount=100.0,
            account_id=account_id,
            timestamp=now
        ),
        Transaction(
            transaction_type=WithdrawTransactionType(),
            amount=30.0,
            account_id=account_id,
            timestamp=now
        ),
        Transaction(
            transaction_type=TransferTransactionType(),
            amount=50.0,
            account_id=account_id,
            timestamp=now,
            source_account_id=account_id,
            destination_account_id=str(uuid4())
        )
    ]
    for i, tx in enumerate(mock_transactions):
        tx.transaction_id = f"tx{i+1}"
    mock_transaction_repository.get_by_account_id.return_value = mock_transactions

    response = client.get(f"/accounts/{account_id}/transactions")

    assert response.status_code == 200
    transactions = response.json()
    assert len(transactions) == 3
    assert transactions[0]["transaction_id"] == "tx1"
    assert transactions[0]["transaction_type"] == "DEPOSIT"
    assert transactions[0]["amount"] == 100.0
    assert transactions[1]["transaction_id"] == "tx2"
    assert transactions[1]["transaction_type"] == "WITHDRAW"
    assert transactions[1]["amount"] == 30.0
    assert transactions[2]["transaction_id"] == "tx3"
    assert transactions[2]["transaction_type"] == "TRANSFER"
    assert transactions[2]["source_account_id"] == account_id
    assert transactions[2]["destination_account_id"] is not None

def test_get_transactions_empty(mock_transaction_repository, mock_checking_account):
    account_id = mock_checking_account.account_id
    mock_transaction_repository.get_by_account_id.return_value = []

    response = client.get(f"/accounts/{account_id}/transactions")

    assert response.status_code == 200
    transactions = response.json()
    assert len(transactions) == 0