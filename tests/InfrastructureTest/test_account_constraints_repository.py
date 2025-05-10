import pytest
from unittest.mock import Mock
from sqlalchemy.orm import Session
from infrastructure.database.models import AccountConstraintsModel
from infrastructure.repositories.account_constraints_repository import AccountConstraintsRepository


@pytest.fixture
def mock_db_session():
    return Mock(spec=Session)

@pytest.fixture
def mock_logging_service():
    return Mock()

@pytest.fixture
def repository(mock_db_session, mock_logging_service):
    return AccountConstraintsRepository(mock_db_session, mock_logging_service)

def test_create_constraints(repository, mock_db_session, mock_logging_service):
    account_id = "test_account_1"
    
    repository.create_constraints(account_id)
    
    # Verify logging
    mock_logging_service.info.assert_any_call(
        f"Creating default constraints for account {account_id}",
        {"account_id": account_id}
    )
    mock_logging_service.info.assert_any_call(
        f"Default constraints created for account {account_id}",
        {"account_id": account_id}
    )
    
    # Verify database operations
    assert mock_db_session.add.called
    assert mock_db_session.commit.called

def test_get_usage_existing_constraints(repository, mock_db_session, mock_logging_service):
    account_id = "test_account_1"
    constraints = AccountConstraintsModel(
        account_id=account_id,
        daily_usage=100.0,
        monthly_usage=1000.0,
        daily_limit=10000.0,
        monthly_limit=50000.0
    )
    
    mock_db_session.query().filter().first.return_value = constraints
    
    result = repository.get_usage(account_id)
    
    assert result == {"daily": 100.0, "monthly": 1000.0}
    mock_logging_service.info.assert_any_call(
        f"Getting usage for account {account_id}",
        {"account_id": account_id}
    )
    mock_logging_service.info.assert_any_call(
        f"Retrieved usage for account {account_id}",
        {"account_id": account_id, "usage": result}
    )

def test_reset_usage_daily(repository, mock_db_session, mock_logging_service):
    account_id = "test_account_1"
    constraints = AccountConstraintsModel(
        account_id=account_id,
        daily_usage=100.0,
        monthly_usage=1000.0
    )
    
    mock_db_session.query().filter().first.return_value = constraints
    
    repository.reset_usage(account_id, "daily")
    
    assert constraints.daily_usage == 0.0
    assert constraints.monthly_usage == 1000.0
    assert mock_db_session.commit.called
    mock_logging_service.info.assert_any_call(
        f"Resetting daily usage for account {account_id}",
        {"account_id": account_id, "period": "daily"}
    )

def test_reset_usage_invalid_period(repository, mock_db_session, mock_logging_service):
    account_id = "test_account_1"
    constraints = AccountConstraintsModel(account_id=account_id)
    
    mock_db_session.query().filter().first.return_value = constraints
    
    with pytest.raises(ValueError, match="Invalid period. Use 'daily' or 'monthly'"):
        repository.reset_usage(account_id, "weekly")
        
    mock_logging_service.error.assert_called_once()

def test_update_usage_daily(repository, mock_db_session, mock_logging_service):
    account_id = "test_account_1"
    constraints = AccountConstraintsModel(
        account_id=account_id,
        daily_usage=100.0,
        monthly_usage=1000.0,
        daily_limit=10000.0
    )
    
    mock_db_session.query().filter().first.return_value = constraints
    
    repository.update_usage(account_id, 50.0, "daily")
    
    assert constraints.daily_usage == 150.0
    assert mock_db_session.commit.called
    mock_logging_service.info.assert_any_call(
        f"Updating daily usage for account {account_id}",
        {"account_id": account_id, "amount": 50.0, "period": "daily"}
    )

def test_update_usage_daily_limit_exceeded(repository, mock_db_session, mock_logging_service):
    account_id = "test_account_1"
    constraints = AccountConstraintsModel(
        account_id=account_id,
        daily_usage=10000.0,
        daily_limit=10000.0
    )
    
    mock_db_session.query().filter().first.return_value = constraints
    
    with pytest.raises(ValueError, match="Daily limit exceeded"):
        repository.update_usage(account_id, 1.0, "daily")
        
    assert mock_db_session.rollback.called
    mock_logging_service.warning.assert_called_once()

def test_get_limits(repository, mock_db_session, mock_logging_service):
    account_id = "test_account_1"
    constraints = AccountConstraintsModel(
        account_id=account_id,
        daily_limit=10000.0,
        monthly_limit=50000.0
    )
    
    mock_db_session.query().filter().first.return_value = constraints
    
    result = repository.get_limits(account_id)
    
    assert result == {"daily": 10000.0, "monthly": 50000.0}
    mock_logging_service.info.assert_any_call(
        f"Getting limits for account {account_id}",
        {"account_id": account_id}
    )

def test_update_limits(repository, mock_db_session, mock_logging_service):
    account_id = "test_account_1"
    constraints = AccountConstraintsModel(
        account_id=account_id,
        daily_limit=10000.0,
        monthly_limit=50000.0
    )
    
    mock_db_session.query().filter().first.return_value = constraints
    
    repository.update_limits(account_id, 20000.0, 100000.0)
    
    assert constraints.daily_limit == 20000.0
    assert constraints.monthly_limit == 100000.0
    assert mock_db_session.commit.called
    mock_logging_service.info.assert_any_call(
        f"Updating limits for account {account_id}",
        {
            "account_id": account_id,
            "daily_limit": 20000.0,
            "monthly_limit": 100000.0
        }
    )

def test_get_or_create_constraints_new(repository, mock_db_session, mock_logging_service):
    account_id = "test_account_1"
    
    mock_db_session.query().filter().first.side_effect = [None, AccountConstraintsModel(account_id=account_id)]
    
    constraints = repository._get_or_create_constraints(account_id)
    
    assert isinstance(constraints, AccountConstraintsModel)
    assert constraints.account_id == account_id
    assert mock_db_session.add.called
    assert mock_db_session.commit.called