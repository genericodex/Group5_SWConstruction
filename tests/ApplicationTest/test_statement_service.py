import pytest
from unittest.mock import Mock
from datetime import datetime
from domain.accounts import Account, AccountType
from domain.transactions import Transaction, DepositTransactionType, WithdrawTransactionType
from application.services.statement_service import StatementService


# Mock classes for Account and AccountType since they are not fully provided
class MockAccountType:
    def __init__(self, name):
        self.name = name


class MockAccount:
    def __init__(self, account_id, account_type):
        self.account_id = account_id
        self.account_type = account_type


def test_generate_statement_pdf_happy_path():
    # Arrange
    account_id = "123"
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 1, 31)
    account = MockAccount(account_id, MockAccountType("SAVINGS"))
    txn1 = Transaction(DepositTransactionType(), 100.0, account_id, datetime(2023, 1, 5))
    txn2 = Transaction(WithdrawTransactionType(), 50.0, account_id, datetime(2023, 1, 10))
    transactions = [txn1, txn2]

    transaction_repo = Mock()
    transaction_repo.get_by_account_id.return_value = transactions
    account_repo = Mock()
    account_repo.get_by_id.return_value = account
    generator = Mock()
    generator.generate_pdf.return_value = "PDF generated"

    service = StatementService(transaction_repo, account_repo, generator)

    # Act
    result = service.generate_statement(account_id, start_date, end_date, "PDF")

    # Assert
    assert result == "PDF generated"
    balance = 100.0 - 50.0  # 50.0
    days = (end_date - start_date).days  # 30
    interest = 50.0 * (0.025 / 365) * 30  # Savings rate
    expected_statement_data = {
        "account_id": account_id,
        "transactions": [t.to_dict() for t in transactions],
        "interest": interest,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat()
    }
    generator.generate_pdf.assert_called_once_with(expected_statement_data)


def test_generate_statement_csv_happy_path():
    # Arrange
    account_id = "123"
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 1, 31)
    account = MockAccount(account_id, MockAccountType("SAVINGS"))
    txn1 = Transaction(DepositTransactionType(), 100.0, account_id, datetime(2023, 1, 5))
    transactions = [txn1]

    transaction_repo = Mock()
    transaction_repo.get_by_account_id.return_value = transactions
    account_repo = Mock()
    account_repo.get_by_id.return_value = account
    generator = Mock()
    generator.generate_csv.return_value = "CSV generated"

    service = StatementService(transaction_repo, account_repo, generator)

    # Act
    result = service.generate_statement(account_id, start_date, end_date, "CSV")

    # Assert
    assert result == "CSV generated"
    balance = 100.0
    days = (end_date - start_date).days
    interest = balance * (0.025 / 365) * days
    expected_statement_data = {
        "account_id": account_id,
        "transactions": [t.to_dict() for t in transactions],
        "interest": interest,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat()
    }
    generator.generate_csv.assert_called_once_with(expected_statement_data)


def test_generate_statement_account_not_found():
    # Arrange
    account_id = "123"
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 1, 31)
    account_repo = Mock()
    account_repo.get_by_id.return_value = None
    transaction_repo = Mock()
    generator = Mock()
    service = StatementService(transaction_repo, account_repo, generator)

    # Act & Assert
    with pytest.raises(ValueError, match="Account not found"):
        service.generate_statement(account_id, start_date, end_date, "PDF")


def test_generate_statement_no_transactions():
    # Arrange
    account_id = "123"
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 1, 31)
    account = MockAccount(account_id, MockAccountType("SAVINGS"))
    transaction_repo = Mock()
    transaction_repo.get_by_account_id.return_value = []
    account_repo = Mock()
    account_repo.get_by_id.return_value = account
    generator = Mock()
    generator.generate_pdf.return_value = "PDF generated"
    service = StatementService(transaction_repo, account_repo, generator)

    # Act
    result = service.generate_statement(account_id, start_date, end_date, "PDF")

    # Assert
    assert result == "PDF generated"
    expected_statement_data = {
        "account_id": account_id,
        "transactions": [],
        "interest": 0.0,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat()
    }
    generator.generate_pdf.assert_called_once_with(expected_statement_data)


def test_generate_statement_checking_account():
    # Arrange
    account_id = "123"
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 1, 31)
    account = MockAccount(account_id, MockAccountType("CHECKING"))
    txn1 = Transaction(DepositTransactionType(), 200.0, account_id, datetime(2023, 1, 5))
    transactions = [txn1]

    transaction_repo = Mock()
    transaction_repo.get_by_account_id.return_value = transactions
    account_repo = Mock()
    account_repo.get_by_id.return_value = account
    generator = Mock()
    generator.generate_pdf.return_value = "PDF generated"

    service = StatementService(transaction_repo, account_repo, generator)

    # Act
    result = service.generate_statement(account_id, start_date, end_date, "PDF")

    # Assert
    assert result == "PDF generated"
    balance = 200.0
    days = (end_date - start_date).days
    interest = balance * (0.001 / 365) * days  # Checking rate
    expected_statement_data = {
        "account_id": account_id,
        "transactions": [t.to_dict() for t in transactions],
        "interest": interest,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat()
    }
    generator.generate_pdf.assert_called_once_with(expected_statement_data)


def test_generate_statement_unsupported_format():
    # Arrange
    account_id = "123"
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 1, 31)
    account = MockAccount(account_id, MockAccountType("SAVINGS"))
    transaction_repo = Mock()
    transaction_repo.get_by_account_id.return_value = []  # Fix: Set to return an empty list
    account_repo = Mock()
    account_repo.get_by_id.return_value = account
    generator = Mock()
    service = StatementService(transaction_repo, account_repo, generator)

    # Act & Assert
    with pytest.raises(ValueError, match="Unsupported format type"):
        service.generate_statement(account_id, start_date, end_date, "XML")


def test_generate_statement_same_start_end_date():
    # Arrange
    account_id = "123"
    start_date = datetime(2023, 1, 5)
    end_date = datetime(2023, 1, 5)
    account = MockAccount(account_id, MockAccountType("SAVINGS"))
    txn1 = Transaction(DepositTransactionType(), 100.0, account_id, datetime(2023, 1, 5))
    transactions = [txn1]

    transaction_repo = Mock()
    transaction_repo.get_by_account_id.return_value = transactions
    account_repo = Mock()
    account_repo.get_by_id.return_value = account
    generator = Mock()
    generator.generate_pdf.return_value = "PDF generated"

    service = StatementService(transaction_repo, account_repo, generator)

    # Act
    result = service.generate_statement(account_id, start_date, end_date, "PDF")

    # Assert
    assert result == "PDF generated"
    balance = 100.0
    days = 0  # Same day
    interest = balance * (0.025 / 365) * days  # 0 interest
    expected_statement_data = {
        "account_id": account_id,
        "transactions": [t.to_dict() for t in transactions],
        "interest": interest,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat()
    }
    generator.generate_pdf.assert_called_once_with(expected_statement_data)


def test_generate_statement_transactions_outside_range():
    # Arrange
    account_id = "123"
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 1, 31)
    account = MockAccount(account_id, MockAccountType("SAVINGS"))
    txn1 = Transaction(DepositTransactionType(), 100.0, account_id, datetime(2023, 2, 1))  # Outside range
    transactions = [txn1]

    transaction_repo = Mock()
    transaction_repo.get_by_account_id.return_value = transactions
    account_repo = Mock()
    account_repo.get_by_id.return_value = account
    generator = Mock()
    generator.generate_pdf.return_value = "PDF generated"

    service = StatementService(transaction_repo, account_repo, generator)

    # Act
    result = service.generate_statement(account_id, start_date, end_date, "PDF")

    # Assert
    assert result == "PDF generated"
    expected_statement_data = {
        "account_id": account_id,
        "transactions": [],  # No transactions in range
        "interest": 0.0,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat()
    }
    generator.generate_pdf.assert_called_once_with(expected_statement_data)