import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from fastapi import FastAPI
from domain.accounts import Account, ActiveStatus, AccountType
from api.v1.endpoints.notifications import router
from application.services.notification_service import NotificationService
from infrastructure.repositories.account_repository import AccountRepository
from api.dependencies import get_notification_service, get_account_repository, get_logging_service

# Mock AccountType
class MockAccountType(AccountType):
    @property
    def name(self) -> str:
        return "MOCK"

# Create a test-specific FastAPI app
@pytest.fixture
def test_app():
    app = FastAPI()
    app.include_router(router, prefix="/api/v1")
    return app

@pytest.fixture
def client(test_app):
    return TestClient(test_app)

# Mock Account class with corrected initialization
class MockAccount(Account):
    def __init__(self, account_id, balance=100.0, email=None, phone=None):
        super().__init__(
            account_id=account_id,
            account_type=MockAccountType(),
            username="test_user",
            _password_hash="mock_hash",
            _balance=balance
        )
        self.email = email
        self.phone = phone
        self.status = ActiveStatus()
        self.creation_date = None
        self._observers = []

    def can_withdraw(self, amount: float) -> bool:
        return self._balance >= amount

    def add_observer(self, observer):
        self._observers.append(observer)

# Test fixtures
@pytest.fixture
def mock_notification_service():
    return MagicMock(spec=NotificationService)

@pytest.fixture
def mock_account_repository():
    return MagicMock(spec=AccountRepository)

@pytest.fixture
def mock_logging_service():
    return MagicMock()

# Override dependencies
@pytest.fixture(autouse=True)
def override_dependencies(test_app, mock_notification_service, mock_account_repository, mock_logging_service):
    test_app.dependency_overrides = {
        get_notification_service: lambda: mock_notification_service,
        get_account_repository: lambda: mock_account_repository,
        get_logging_service: lambda: mock_logging_service,
    }
    yield
    test_app.dependency_overrides = {}

# Tests for Subscribe to Notifications
def test_subscribe_to_notifications_email_success(
    client, mock_notification_service, mock_account_repository, mock_logging_service
):
    account_id = "acc123"
    email = "user@example.com"
    account = MockAccount(account_id=account_id)
    mock_account_repository.get_account_by_id.return_value = account
    mock_notification_service.register_account_observers.return_value = None
    mock_account_repository.save.return_value = account_id
    mock_logging_service.info.return_value = None

    response = client.post(
        "/api/v1/notifications/subscribe",
        json={"accountId": account_id, "notifyType": "email", "contactInfo": email}
    )

    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "message": "Successfully subscribed to email notifications"
    }
    assert account.email == email
    mock_notification_service.register_account_observers.assert_called_once_with(account, "standard")
    mock_account_repository.save.assert_called_once_with(account)
    mock_logging_service.info.assert_called_once_with(
        f"Account {account_id} subscribed to email notifications",
        {"account_id": account_id, "notify_type": "email"}
    )

def test_subscribe_to_notifications_sms_success(
    client, mock_notification_service, mock_account_repository, mock_logging_service
):
    account_id = "acc123"
    phone = "+15551234567"
    account = MockAccount(account_id=account_id)
    mock_account_repository.get_account_by_id.return_value = account
    mock_notification_service.register_account_observers.return_value = None
    mock_account_repository.save.return_value = account_id
    mock_logging_service.info.return_value = None

    response = client.post(
        "/api/v1/notifications/subscribe",
        json={"accountId": account_id, "notifyType": "sms", "contactInfo": phone}
    )

    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "message": "Successfully subscribed to sms notifications"
    }
    assert account.phone == phone
    mock_notification_service.register_account_observers.assert_called_once_with(account, "premium")
    mock_account_repository.save.assert_called_once_with(account)
    mock_logging_service.info.assert_called_once_with(
        f"Account {account_id} subscribed to sms notifications",
        {"account_id": account_id, "notify_type": "sms"}
    )

def test_subscribe_to_notifications_account_not_found(client, mock_account_repository):
    account_id = "non_existent"
    mock_account_repository.get_account_by_id.return_value = None

    response = client.post(
        "/api/v1/notifications/subscribe",
        json={"accountId": account_id, "notifyType": "email", "contactInfo": "user@example.com"}
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Account not found."}

def test_subscribe_to_notifications_invalid_type(client):
    response = client.post(
        "/api/v1/notifications/subscribe",
        json={"accountId": "acc123", "notifyType": "invalid_type", "contactInfo": "user@example.com"}
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid notification type. Must be 'email' or 'sms'."}

def test_subscribe_to_notifications_exception(
    client, mock_notification_service, mock_account_repository, mock_logging_service
):
    account_id = "acc123"
    account = MockAccount(account_id=account_id)
    mock_account_repository.get_account_by_id.return_value = account
    mock_notification_service.register_account_observers.side_effect = Exception("Service unavailable")
    mock_logging_service.error.return_value = None

    response = client.post(
        "/api/v1/notifications/subscribe",
        json={"accountId": account_id, "notifyType": "email", "contactInfo": "user@example.com"}
    )

    assert response.status_code == 500
    assert response.json() == {"detail": "Failed to subscribe to notifications: Service unavailable"}
    mock_logging_service.error.assert_called_once_with(
        "Failed to subscribe to notifications: Service unavailable",
        {"account_id": account_id, "notify_type": "email"}
    )

# Tests for Unsubscribe from Notifications
def test_unsubscribe_from_notifications_email_success(
    client, mock_notification_service, mock_account_repository, mock_logging_service
):
    account_id = "acc123"
    account = MockAccount(account_id=account_id, email="user@example.com")
    mock_account_repository.get_account_by_id.return_value = account
    mock_notification_service.register_account_observers.return_value = None
    mock_account_repository.save.return_value = account_id
    mock_logging_service.info.return_value = None

    response = client.post(
        "/api/v1/notifications/unsubscribe",
        json={"accountId": account_id, "notifyType": "email", "contactInfo": "user@example.com"}
    )

    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "message": "Successfully unsubscribed from email notifications"
    }
    assert account.email is None
    mock_notification_service.register_account_observers.assert_called_once_with(account, "default")
    mock_account_repository.save.assert_called_once_with(account)
    mock_logging_service.info.assert_called_once_with(
        f"Account {account_id} unsubscribed from email notifications",
        {"account_id": account_id, "notify_type": "email"}
    )

def test_unsubscribe_from_notifications_sms_success(
    client, mock_notification_service, mock_account_repository, mock_logging_service
):
    account_id = "acc123"
    account = MockAccount(account_id=account_id, phone="+15551234567")
    mock_account_repository.get_account_by_id.return_value = account
    mock_notification_service.register_account_observers.return_value = None
    mock_account_repository.save.return_value = account_id
    mock_logging_service.info.return_value = None

    response = client.post(
        "/api/v1/notifications/unsubscribe",
        json={"accountId": account_id, "notifyType": "sms", "contactInfo": "+15551234567"}
    )

    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "message": "Successfully unsubscribed from sms notifications"
    }
    assert account.phone is None
    mock_notification_service.register_account_observers.assert_called_once_with(account, "default")
    mock_account_repository.save.assert_called_once_with(account)
    mock_logging_service.info.assert_called_once_with(
        f"Account {account_id} unsubscribed from sms notifications",
        {"account_id": account_id, "notify_type": "sms"}
    )

def test_unsubscribe_from_notifications_account_not_found(client, mock_account_repository):
    account_id = "non_existent"
    mock_account_repository.get_account_by_id.return_value = None

    response = client.post(
        "/api/v1/notifications/unsubscribe",
        json={"accountId": account_id, "notifyType": "email", "contactInfo": "user@example.com"}
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Account not found."}

def test_unsubscribe_from_notifications_invalid_type(client):
    response = client.post(
        "/api/v1/notifications/unsubscribe",
        json={"accountId": "acc123", "notifyType": "invalid_type", "contactInfo": "user@example.com"}
    )

    assert response.status_code == 400  # Verify API logic if this still fails with 500
    assert response.json() == {"detail": "Invalid notification type. Must be 'email' or 'sms'."}

def test_unsubscribe_from_notifications_exception(
    client, mock_notification_service, mock_account_repository, mock_logging_service
):
    account_id = "acc123"
    account = MockAccount(account_id=account_id, email="user@example.com")
    mock_account_repository.get_account_by_id.return_value = account
    mock_account_repository.save.side_effect = Exception("Database error")
    mock_logging_service.error.return_value = None

    response = client.post(
        "/api/v1/notifications/unsubscribe",
        json={"accountId": account_id, "notifyType": "email", "contactInfo": "user@example.com"}
    )

    assert response.status_code == 500
    assert response.json() == {"detail": "Failed to unsubscribe from notifications: Database error"}
    mock_logging_service.error.assert_called_once_with(
        "Failed to unsubscribe from notifications: Database error",
        {"account_id": account_id, "notify_type": "email"}
    )