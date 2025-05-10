import pytest
from unittest.mock import Mock
from datetime import datetime
from domain.accounts import AccountType
from domain.transactions import Transaction, DepositTransactionType, WithdrawTransactionType, TransferTransactionType
from application.services.statement_service import StatementService
from infrastructure.adapters.statement_adapter import StatementAdapter
from domain.savings_account import SavingsAccount
from domain.checking_account import CheckingAccount

def test_generate_statement_happy_path():
    # Setup mocks
    account_repo = Mock()
    transaction_repo = Mock()
    generator = Mock()

    # Sample data
    account_id = "123"
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 1, 31)
    account = SavingsAccount(account_id=account_id, username="testuser", password="testpass", initial_balance=0)
    transactions = [
        Transaction(DepositTransactionType(), 1000, account_id, datetime(2023, 12, 31)),
        Transaction(WithdrawTransactionType(), 200, account_id, datetime(2024, 1, 15)),
        Transaction(DepositTransactionType(), 300, account_id, datetime(2024, 1, 20)),
    ]

    account_repo.get_by_id.return_value = account
    transaction_repo.get_by_account_id.return_value = transactions
    generator.generate.return_value = "Generated PDF"

    # Create service and call method
    service = StatementService(transaction_repo, account_repo, generator)
    result = service.generate_statement(account_id, start_date, end_date, "PDF")

    # Assertions
    assert result == "Generated PDF"
    called_statement = generator.generate.call_args[0][0]
    assert called_statement.account_id == account_id
    assert called_statement.starting_balance == 1000  # Deposit before period
    assert called_statement.ending_balance == 1100    # 1000 - 200 + 300
    assert len(called_statement.transactions) == 2    # Transactions during period
    days = (end_date - start_date).days
    interest = 1100 * (0.025 / 365) * days
    assert called_statement.interest_earned == pytest.approx(interest)
    assert called_statement.total_deposits == 300
    assert called_statement.total_withdrawals == 200

def test_generate_statement_account_not_found():
    account_repo = Mock()
    account_repo.get_by_id.return_value = None
    transaction_repo = Mock()
    generator = Mock()

    service = StatementService(transaction_repo, account_repo, generator)
    with pytest.raises(ValueError, match="Account not found"):
        service.generate_statement("nonexistent", datetime(2024, 1, 1), datetime(2024, 1, 31))

def test_generate_statement_no_transactions():
    account_repo = Mock()
    transaction_repo = Mock()
    generator = Mock()

    account_id = "123"
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 1, 31)
    account = SavingsAccount(account_id=account_id, username="testuser", password="testpass", initial_balance=0)

    account_repo.get_by_id.return_value = account
    transaction_repo.get_by_account_id.return_value = []
    generator.generate.return_value = "Generated PDF"

    service = StatementService(transaction_repo, account_repo, generator)
    result = service.generate_statement(account_id, start_date, end_date, "PDF")

    assert result == "Generated PDF"
    called_statement = generator.generate.call_args[0][0]
    assert called_statement.starting_balance == 0
    assert called_statement.ending_balance == 0
    assert called_statement.interest_earned == 0
    assert len(called_statement.transactions) == 0

def test_generate_statement_transactions_only_before():
    account_repo = Mock()
    transaction_repo = Mock()
    generator = Mock()

    account_id = "123"
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 1, 31)
    account = SavingsAccount(account_id=account_id, username="testuser", password="testpass", initial_balance=0)
    transactions = [
        Transaction(DepositTransactionType(), 500, account_id, datetime(2023, 12, 15)),
        Transaction(WithdrawTransactionType(), 100, account_id, datetime(2023, 12, 20)),
    ]

    account_repo.get_by_id.return_value = account
    transaction_repo.get_by_account_id.return_value = transactions
    generator.generate.return_value = "Generated PDF"

    service = StatementService(transaction_repo, account_repo, generator)
    result = service.generate_statement(account_id, start_date, end_date, "PDF")

    assert result == "Generated PDF"
    called_statement = generator.generate.call_args[0][0]
    assert called_statement.starting_balance == 400  # 500 - 100
    assert called_statement.ending_balance == 400
    assert called_statement.interest_earned == pytest.approx(400 * (0.025 / 365) * 30)
    assert len(called_statement.transactions) == 0

def test_generate_statement_checking_account():
    account_repo = Mock()
    transaction_repo = Mock()
    generator = Mock()

    account_id = "456"
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 1, 31)
    account = CheckingAccount(account_id=account_id, username="testuser", password="testpass", initial_balance=0)
    transactions = [
        Transaction(DepositTransactionType(), 1000, account_id, datetime(2024, 1, 10)),
    ]

    account_repo.get_by_id.return_value = account
    transaction_repo.get_by_account_id.return_value = transactions
    generator.generate.return_value = "Generated PDF"

    service = StatementService(transaction_repo, account_repo, generator)
    result = service.generate_statement(account_id, start_date, end_date, "PDF")

    assert result == "Generated PDF"
    called_statement = generator.generate.call_args[0][0]
    assert called_statement.starting_balance == 0
    assert called_statement.ending_balance == 1000
    interest = 1000 * (0.001 / 365) * 30
    assert called_statement.interest_earned == pytest.approx(interest)

def test_generate_statement_csv_format():
    account_repo = Mock()
    transaction_repo = Mock()
    generator = Mock()

    account_id = "123"
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 1, 31)
    account = SavingsAccount(account_id=account_id, username="testuser", password="testpass", initial_balance=0)

    account_repo.get_by_id.return_value = account
    transaction_repo.get_by_account_id.return_value = []
    generator.generate.return_value = "Generated CSV"

    service = StatementService(transaction_repo, account_repo, generator)
    result = service.generate_statement(account_id, start_date, end_date, "CSV")

    assert result == "Generated CSV"
    called_statement = generator.generate.call_args[0][0]
    generator.generate.assert_called_with(called_statement, "CSV")

def test_generate_statement_unsupported_format():
    account_repo = Mock()
    transaction_repo = Mock()
    generator = StatementAdapter()  # Real adapter to test exception

    account_id = "123"
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 1, 31)
    account = SavingsAccount(account_id=account_id, username="testuser", password="testpass", initial_balance=0)

    account_repo.get_by_id.return_value = account
    transaction_repo.get_by_account_id.return_value = []

    service = StatementService(transaction_repo, account_repo, generator)
    with pytest.raises(ValueError, match="Unsupported format type: TXT"):
        service.generate_statement(account_id, start_date, end_date, "TXT")

def test_generate_statement_with_transfers():
    account_repo = Mock()
    transaction_repo = Mock()
    generator = Mock()

    account_id = "123"
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 1, 31)
    account = SavingsAccount(account_id=account_id, username="testuser", password="testpass", initial_balance=0)
    transactions = [
        Transaction(DepositTransactionType(), 1000, account_id, datetime(2023, 12, 31)),
        Transaction(WithdrawTransactionType(), 200, account_id, datetime(2024, 1, 15)),
        Transaction(DepositTransactionType(), 300, account_id, datetime(2024, 1, 20)),
        Transaction(TransferTransactionType(), 100, account_id, datetime(2024, 1, 25), source_account_id="other", destination_account_id=account_id),
        Transaction(TransferTransactionType(), 50, account_id, datetime(2024, 1, 26), source_account_id=account_id, destination_account_id="other"),
    ]

    account_repo.get_by_id.return_value = account
    transaction_repo.get_by_account_id.return_value = transactions
    generator.generate.return_value = "Generated PDF"

    service = StatementService(transaction_repo, account_repo, generator)
    result = service.generate_statement(account_id, start_date, end_date, "PDF")

    assert result == "Generated PDF"
    called_statement = generator.generate.call_args[0][0]
    assert called_statement.starting_balance == 1000
    assert called_statement.ending_balance == 1100  # Transfers not affecting balance in current impl
    assert len(called_statement.transactions) == 4
    assert called_statement.total_deposits == 300
    assert called_statement.total_withdrawals == 200
    assert called_statement.total_transfers_in == 100
    assert called_statement.total_transfers_out == 50