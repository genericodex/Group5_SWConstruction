import unittest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from api.v1.endpoints.accounts import router
from api.dependencies import (
    get_account_creation_service,
    get_transaction_service,
    get_account_repository,
    get_transaction_repository,
)
from application.services.account_creation_service import AccountCreationService
from application.services.transaction_service import TransactionService
from infrastructure.repositories.account_repository import AccountRepository
from infrastructure.repositories.transaction_repository import TransactionRepository
from domain.accounts import CheckingAccount, AccountType, AccountStatus
from domain.transactions import Transaction, TransactionType
from datetime import datetime

# Create a FastAPI app with only the accounts router for testing
from fastapi import FastAPI
app = FastAPI()
app.include_router(router, prefix="/v1", tags=["accounts"])
client = TestClient(app)

class TestAccountsAPI(unittest.TestCase):
    def setUp(self):
        # Mock the services and repositories
        self.account_creation_service = MagicMock(spec=AccountCreationService)
        self.transaction_service = MagicMock(spec=TransactionService)
        self.account_repository = MagicMock(spec=AccountRepository)
        self.transaction_repository = MagicMock(spec=TransactionRepository)

        # Mock the dependency injection by overriding the dependency functions directly
        app.dependency_overrides[get_account_creation_service] = lambda: self.account_creation_service
        app.dependency_overrides[get_transaction_service] = lambda: self.transaction_service
        app.dependency_overrides[get_account_repository] = lambda: self.account_repository
        app.dependency_overrides[get_transaction_repository] = lambda: self.transaction_repository

    def tearDown(self):
        # Clear dependency overrides after each test
        app.dependency_overrides.clear()

    def test_create_account_success(self):
        # Arrange
        self.account_creation_service.create_account.return_value = "acc_123"
        payload = {"accountType": "checking", "initialDeposit": 100.0}

        # Act
        response = client.post("/v1/accounts", json=payload)

        # Assert
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), {"account_id": "acc_123"})
        self.account_creation_service.create_account.assert_called_once_with("checking", 100.0)

    def test_create_account_invalid_type(self):
        # Arrange
        payload = {"accountType": "invalid", "initialDeposit": 100.0}

        # Act
        response = client.post("/v1/accounts", json=payload)

        # Assert
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"detail": "Invalid account type. Must be 'checking' or 'savings'."})

    def test_create_account_negative_deposit(self):
        # Arrange
        payload = {"accountType": "checking", "initialDeposit": -50.0}

        # Act
        response = client.post("/v1/accounts", json=payload)

        # Assert
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"detail": "Initial deposit must be non-negative."})

    def test_deposit_success(self):
        # Arrange
        account_id = "acc_123"
        self.transaction_service.deposit.return_value = Transaction(
            transaction_type=TransactionType.DEPOSIT,
            amount=50.0,
            account_id=account_id,
            timestamp=datetime.now()
        )
        account = CheckingAccount(account_id=account_id, initial_balance=100.0)
        # Set the balance to 150.0 by depositing an additional 50.0
        account.deposit(50.0)  # Initial balance is 100.0, so total becomes 150.0
        self.account_repository.get_account_by_id.return_value = account
        payload = {"amount": 50.0}

        # Act
        response = client.post(f"/v1/accounts/{account_id}/deposit", json=payload)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"balance": 150.0})
        self.transaction_service.deposit.assert_called_once_with(account_id, 50.0)

    def test_deposit_negative_amount(self):
        # Arrange
        account_id = "acc_123"
        payload = {"amount": -50.0}

        # Act
        response = client.post(f"/v1/accounts/{account_id}/deposit", json=payload)

        # Assert
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"detail": "Deposit amount must be positive."})

    def test_deposit_account_not_found(self):
        # Arrange
        account_id = "acc_123"
        self.transaction_service.deposit.return_value = Transaction(
            transaction_type=TransactionType.DEPOSIT,
            amount=50.0,
            account_id=account_id,
            timestamp=datetime.now()
        )
        self.account_repository.get_account_by_id.return_value = None
        payload = {"amount": 50.0}

        # Act
        response = client.post(f"/v1/accounts/{account_id}/deposit", json=payload)

        # Assert
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "Account not found after deposit."})

    def test_withdraw_success(self):
        # Arrange
        account_id = "acc_123"
        self.transaction_service.withdraw.return_value = Transaction(
            transaction_type=TransactionType.WITHDRAW,
            amount=50.0,
            account_id=account_id,
            timestamp=datetime.now()
        )
        account = CheckingAccount(account_id=account_id, initial_balance=100.0)
        # Balance is already 100.0 from initial_balance, no additional adjustment needed
        self.account_repository.get_account_by_id.return_value = account
        payload = {"amount": 50.0}

        # Act
        response = client.post(f"/v1/accounts/{account_id}/withdraw", json=payload)

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"balance": 100.0})
        self.transaction_service.withdraw.assert_called_once_with(account_id, 50.0)

    def test_withdraw_negative_amount(self):
        # Arrange
        account_id = "acc_123"
        payload = {"amount": -50.0}

        # Act
        response = client.post(f"/v1/accounts/{account_id}/withdraw", json=payload)

        # Assert
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"detail": "Withdrawal amount must be positive."})

    def test_withdraw_account_not_found(self):
        # Arrange
        account_id = "acc_123"
        self.transaction_service.withdraw.return_value = Transaction(
            transaction_type=TransactionType.WITHDRAW,
            amount=50.0,
            account_id=account_id,
            timestamp=datetime.now()
        )
        self.account_repository.get_account_by_id.return_value = None
        payload = {"amount": 50.0}

        # Act
        response = client.post(f"/v1/accounts/{account_id}/withdraw", json=payload)

        # Assert
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "Account not found after withdrawal."})

    def test_get_balance_success(self):
        # Arrange
        account_id = "acc_123"
        account = CheckingAccount(account_id=account_id, initial_balance=100.0)
        # Balance is already 100.0 from initial_balance, no additional adjustment needed
        self.account_repository.get_account_by_id.return_value = account

        # Act
        response = client.get(f"/v1/accounts/{account_id}/balance")

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "account_id": account_id,
            "balance": 100.0,
            "availableBalance": 100.0
        })
        self.account_repository.get_account_by_id.assert_called_once_with(account_id)

    def test_get_balance_account_not_found(self):
        # Arrange
        account_id = "acc_123"
        self.account_repository.get_account_by_id.return_value = None

        # Act
        response = client.get(f"/v1/accounts/{account_id}/balance")

        # Assert
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "Account not found."})

    def test_get_transactions_success(self):
        # Arrange
        account_id = "acc_123"
        timestamp = datetime.now()
        transactions = [
            Transaction(
                transaction_type=TransactionType.DEPOSIT,
                amount=100.0,
                account_id=account_id,
                timestamp=timestamp
            )
        ]
        transactions[0].transaction_id = "txn_123"
        self.transaction_repository.get_by_account_id.return_value = transactions

        # Act
        response = client.get(f"/v1/accounts/{account_id}/transactions")

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [{
            "transaction_id": "txn_123",
            "transaction_type": "DEPOSIT",
            "amount": 100.0,
            "account_id": account_id,
            "timestamp": timestamp.isoformat()
        }])
        self.transaction_repository.get_by_account_id.assert_called_once_with(account_id)

    def test_get_transactions_empty(self):
        # Arrange
        account_id = "acc_123"
        self.transaction_repository.get_by_account_id.return_value = []

        # Act
        response = client.get(f"/v1/accounts/{account_id}/transactions")

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])
        self.transaction_repository.get_by_account_id.assert_called_once_with(account_id)

if __name__ == "__main__":
    unittest.main()