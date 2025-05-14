import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from datetime import datetime
from fastapi import FastAPI
from api.v1.endpoints.finances import router
from application.services.interest_service import InterestService
from application.services.limit_enforcement_service import LimitEnforcementService
from application.services.statement_service import StatementService
from application.services.logging_service import LoggingService
from api.dependencies import get_interest_service, get_limit_enforcement_service, get_statement_service, get_logging_service

# Create a test-specific FastAPI app
app = FastAPI()
app.include_router(router, prefix="/api/v1")
client = TestClient(app)

# Test fixtures
@pytest.fixture
def mock_interest_service():
    return MagicMock(spec=InterestService)

@pytest.fixture
def mock_limit_enforcement_service():
    return MagicMock(spec=LimitEnforcementService)

@pytest.fixture
def mock_statement_service():
    return MagicMock(spec=StatementService)

@pytest.fixture
def mock_logging_service():
    return MagicMock(spec=LoggingService)

# Override dependencies
@pytest.fixture(autouse=True)
def override_dependencies(
    mock_interest_service,
    mock_limit_enforcement_service,
    mock_statement_service,
    mock_logging_service
):
    app.dependency_overrides = {
        get_interest_service: lambda: mock_interest_service,
        get_limit_enforcement_service: lambda: mock_limit_enforcement_service,
        get_statement_service: lambda: mock_statement_service,
        get_logging_service: lambda: mock_logging_service,
    }
    yield
    app.dependency_overrides.clear()

# Interest Calculation Tests
def test_calculate_interest_success(mock_interest_service, mock_logging_service):
    account_id = "acc123"
    calculation_date = "2025-05-12"
    interest_applied = 10.0
    updated_balance = 110.0
    mock_account = MagicMock()
    mock_account._balance = updated_balance
    mock_interest_service.apply_interest_to_account.return_value = interest_applied
    mock_interest_service.account_repository = MagicMock()
    mock_interest_service.account_repository.get_by_id.return_value = mock_account

    response = client.post(
        f"/api/v1/accounts/{account_id}/interest/calculate",
        json={"calculationDate": calculation_date}
    )

    assert response.status_code == 200
    result = response.json()
    assert result["account_id"] == account_id
    assert result["interest_applied"] == interest_applied
    assert result["updated_balance"] == updated_balance
    mock_interest_service.apply_interest_to_account.assert_called_once_with(account_id, end_date=datetime(2025, 5, 12))
    mock_logging_service.info.assert_called_once_with(
        f"Interest calculated for account {account_id}",
        {"account_id": account_id, "interest_applied": interest_applied, "updated_balance": updated_balance}
    )

def test_calculate_interest_account_not_found(mock_interest_service, mock_logging_service):
    account_id = "non_existent"
    mock_interest_service.account_repository = MagicMock()
    mock_interest_service.account_repository.get_by_id.return_value = None
    mock_interest_service.apply_interest_to_account.return_value = 0.0  # Ensures no unexpected exceptions

    response = client.post(
        f"/api/v1/accounts/{account_id}/interest/calculate",
        json={"calculationDate": "2025-05-12"}
    )

    assert response.status_code == 404
    assert "Account not found" in response.json()["detail"]

def test_calculate_interest_invalid_date(mock_logging_service):
    account_id = "acc123"
    response = client.post(
        f"/api/v1/accounts/{account_id}/interest/calculate",
        json={"calculationDate": "invalid_date"}
    )

    assert response.status_code == 400
    assert "time data 'invalid_date' does not match format '%Y-%m-%d'" in response.json()["detail"]
    mock_logging_service.error.assert_called_once_with(
        f"Failed to calculate interest: time data 'invalid_date' does not match format '%Y-%m-%d'",
        {"account_id": account_id}
    )

# Update Limits Tests
def test_update_limits_success(mock_limit_enforcement_service, mock_logging_service):
    account_id = "acc123"
    daily_limit = 1000.0
    monthly_limit = 5000.0
    mock_limit_enforcement_service.update_account_limits.return_value = None

    response = client.patch(
        f"/api/v1/accounts/{account_id}/limits",
        json={"dailyLimit": daily_limit, "monthlyLimit": monthly_limit}
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Limits updated successfully"}
    mock_limit_enforcement_service.update_account_limits.assert_called_once_with(account_id, daily_limit, monthly_limit)
    mock_logging_service.info.assert_called_once_with(
        f"Updated limits for account {account_id}",
        {"account_id": account_id, "daily_limit": daily_limit, "monthly_limit": monthly_limit}
    )

def test_update_limits_invalid_values(mock_limit_enforcement_service, mock_logging_service):
    account_id = "acc123"
    daily_limit = -100.0
    monthly_limit = 5000.0
    mock_limit_enforcement_service.update_account_limits.side_effect = ValueError("Limits cannot be negative")

    response = client.patch(
        f"/api/v1/accounts/{account_id}/limits",
        json={"dailyLimit": daily_limit, "monthlyLimit": monthly_limit}
    )

    assert response.status_code == 400
    assert "Limits cannot be negative" in response.json()["detail"]
    mock_logging_service.error.assert_called_once()

# Retrieve Limits Tests
def test_get_limits_success(mock_limit_enforcement_service, mock_logging_service):
    account_id = "acc123"
    limits = {"daily": 1000.0, "monthly": 5000.0}
    usage = {"daily": 200.0, "monthly": 1000.0}
    mock_limit_enforcement_service.constraints_repository = MagicMock()
    mock_limit_enforcement_service.constraints_repository.get_limits.return_value = limits
    mock_limit_enforcement_service.constraints_repository.get_usage.return_value = usage

    response = client.get(f"/api/v1/accounts/{account_id}/limits")

    assert response.status_code == 200
    result = response.json()
    assert result["daily_limit"] == limits["daily"]
    assert result["monthly_limit"] == limits["monthly"]
    assert result["daily_usage"] == usage["daily"]
    assert result["monthly_usage"] == usage["monthly"]
    mock_logging_service.info.assert_called_once_with(
        f"Retrieved limits for account {account_id}",
        {"account_id": account_id, "limits": result}
    )

def test_get_limits_service_exception(mock_limit_enforcement_service, mock_logging_service):
    account_id = "acc123"
    mock_limit_enforcement_service.constraints_repository = MagicMock()
    mock_limit_enforcement_service.constraints_repository.get_limits.side_effect = Exception("Service error")

    response = client.get(f"/api/v1/accounts/{account_id}/limits")

    assert response.status_code == 500
    assert "Failed to retrieve limits" in response.json()["detail"]
    mock_logging_service.error.assert_called_once()

# Monthly Statement Tests
def test_generate_statement_success(mock_statement_service, mock_logging_service, tmp_path):
    account_id = "acc123"
    year = 2025
    month = 5
    format = "pdf"
    file_path = tmp_path / "statement.pdf"
    file_path.write_text("dummy content")  # Create a dummy file
    mock_statement_service.generate_statement.return_value = str(file_path)

    response = client.get(
        f"/api/v1/accounts/{account_id}/statement",
        params={"year": year, "month": month, "format": format}
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.headers["content-disposition"] == f'attachment; filename="statement_{account_id}_{year}_05.pdf"'

    mock_statement_service.generate_statement.assert_called_once_with(
        account_id, datetime(2025, 5, 1), datetime(2025, 5, 31), "PDF"
    )
    mock_logging_service.info.assert_called_once_with(
        f"Generated statement for account {account_id}",
        {"account_id": account_id, "year": year, "month": month, "format": format}
    )

def test_generate_statement_invalid_month(mock_statement_service, mock_logging_service):
    account_id = "acc123"
    year = 2025
    month = 13
    format = "pdf"

    response = client.get(
        f"/api/v1/accounts/{account_id}/statement",
        params={"year": year, "month": month, "format": format}
    )

    assert response.status_code == 400
    assert "Month must be between 1 and 12" in response.json()["detail"]

def test_generate_statement_invalid_format(mock_statement_service, mock_logging_service):
    account_id = "acc123"
    year = 2025
    month = 5
    format = "invalid"

    response = client.get(
        f"/api/v1/accounts/{account_id}/statement",
        params={"year": year, "month": month, "format": format}
    )

    assert response.status_code == 400
    assert "Format must be 'pdf' or 'csv'" in response.json()["detail"]

def test_generate_statement_service_exception(mock_statement_service, mock_logging_service):
    account_id = "acc123"
    year = 2025
    month = 5
    format = "pdf"
    mock_statement_service.generate_statement.side_effect = Exception("Service error")

    response = client.get(
        f"/api/v1/accounts/{account_id}/statement",
        params={"year": year, "month": month, "format": format}
    )

    assert response.status_code == 500
    assert "Failed to generate statement" in response.json()["detail"]
    mock_logging_service.error.assert_called_once()