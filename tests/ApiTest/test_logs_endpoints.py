import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session

from api.v1.endpoints.logs import router
from infrastructure.repositories.account_repository import AccountRepository
from api.dependencies import get_logging_service, get_db

# Create a FastAPI TestClient
from fastapi import FastAPI

app = FastAPI()
app.include_router(router)
client = TestClient(app)


class MockAccount:
    def __init__(self, account_id, balance=100.0):
        self.account_id = account_id
        self._balance = balance


# Test fixtures
@pytest.fixture
def mock_account_repository():
    repo = MagicMock(spec=AccountRepository)
    return repo


@pytest.fixture
def mock_logging_service():
    service = MagicMock()
    return service


@pytest.fixture
def mock_db_session():
    session = MagicMock(spec=Session)
    return session


# Override dependencies for testing
@pytest.fixture(autouse=True)
def override_dependencies(mock_logging_service, mock_db_session):
    def mock_get_logging_service():
        return mock_logging_service

    def mock_get_db():
        yield mock_db_session

    app.dependency_overrides[get_logging_service] = mock_get_logging_service
    app.dependency_overrides[get_db] = mock_get_db
    yield
    app.dependency_overrides.clear()


# Tests for Get Transaction Logs
def test_get_transaction_logs_no_filters(mock_logging_service):
    response = client.get("/logs/transactions")
    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "success"
    assert result["message"] == "Transaction logs retrieved"
    assert "filters" in result
    assert "logs" in result
    mock_logging_service.info.assert_called_once()


def test_get_transaction_logs_with_filters(mock_logging_service):
    response = client.get(
        "/logs/transactions?start_date=2023-01-01&end_date=2023-12-31&account_id=acc123&transaction_type=deposit"
    )
    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "success"
    filters = result["filters"]
    assert filters["start_date"] == "2023-01-01"
    assert filters["end_date"] == "2023-12-31"
    assert filters["account_id"] == "acc123"
    assert filters["transaction_type"] == "deposit"
    mock_logging_service.info.assert_called_once()


# Tests for Get Account Logs
def test_get_account_logs_account_exists(mock_db_session, mock_logging_service, mock_account_repository):
    account_id = "acc123"
    mock_account = MockAccount(account_id)
    mock_account_repository.get_account_by_id.return_value = mock_account

    with patch("api.v1.endpoints.logs.AccountRepository", return_value=mock_account_repository):
        response = client.get(f"/accounts/{account_id}/logs")
        assert response.status_code == 200
        result = response.json()
        assert result["status"] == "success"
        assert account_id in result["message"]
        filters = result["filters"]
        assert filters["account_id"] == account_id
        mock_logging_service.info.assert_called_once()


def test_get_account_logs_with_filters(mock_db_session, mock_logging_service, mock_account_repository):
    account_id = "acc123"
    mock_account = MockAccount(account_id)
    mock_account_repository.get_account_by_id.return_value = mock_account

    with patch("api.v1.endpoints.logs.AccountRepository", return_value=mock_account_repository):
        response = client.get(
            f"/accounts/{account_id}/logs?start_date=2023-01-01&end_date=2023-12-31&log_type=transaction"
        )
        assert response.status_code == 200
        result = response.json()
        assert result["status"] == "success"
        filters = result["filters"]
        assert filters["account_id"] == account_id
        assert filters["start_date"] == "2023-01-01"
        assert filters["end_date"] == "2023-12-31"
        assert filters["log_type"] == "transaction"
        mock_logging_service.info.assert_called_once()


def test_get_account_logs_account_not_found(mock_db_session, mock_logging_service, mock_account_repository):
    account_id = "non_existent"
    mock_account_repository.get_account_by_id.return_value = None

    with patch("api.v1.endpoints.logs.AccountRepository", return_value=mock_account_repository):
        response = client.get(f"/accounts/{account_id}/logs")
        assert response.status_code == 404
        assert "Account not found" in response.json()["detail"]