import pytest

from domain.accounts import AccountType
from infrastructure.Authentication.login import InMemoryAuthenticationService


@pytest.fixture
def auth_service():
    """
    Fixture to initialize the InMemoryAuthenticationService for each test.
    """
    return InMemoryAuthenticationService()


def test_register_user(auth_service):
    """
    Test user registration.
    """
    account = auth_service.register(
        account_id="123",
        username="user1",
        password="password123",
        account_type=AccountType.SAVINGS
    )
    assert account.account_id == "123"
    assert account.username == "user1"
    assert account.verify_password("password123") is True


def test_register_duplicate_username(auth_service):
    """
    Test that registering a duplicate username raises an error.
    """
    auth_service.register(
        account_id="123",
        username="user1",
        password="password123",
        account_type=AccountType.SAVINGS
    )
    with pytest.raises(ValueError):
        auth_service.register(
            account_id="124",
            username="user1",
            password="password456",
            account_type=AccountType.CHECKING
        )


def test_login_successful(auth_service):
    """
    Test successful login with valid credentials.
    """
    auth_service.register(
        account_id="123",
        username="user1",
        password="password123",
        account_type=AccountType.SAVINGS
    )
    account = auth_service.login(username="user1", password="password123")
    assert account.username == "user1"
    assert account.account_id == "123"


def test_login_invalid_username(auth_service):
    """
    Test login with an invalid username.
    """
    auth_service.register(
        account_id="123",
        username="user1",
        password="password123",
        account_type=AccountType.SAVINGS
    )
    with pytest.raises(ValueError):
        auth_service.login(username="invalid_user", password="password123")


def test_login_invalid_password(auth_service):
    """
    Test login with an invalid password.
    """
    auth_service.register(
        account_id="123",
        username="user1",
        password="password123",
        account_type=AccountType.SAVINGS
    )
    with pytest.raises(ValueError):
        auth_service.login(username="user1", password="wrong_password")
