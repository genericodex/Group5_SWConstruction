import unittest
from unittest.mock import MagicMock, patch
from sqlalchemy.exc import SQLAlchemyError
from infrastructure.database.transaction_manager import TransactionManager


class TestTransactionManager(unittest.TestCase):
    def setUp(self):
        self.mock_db = MagicMock()
        self.transaction_manager = TransactionManager(self.mock_db)

    def test_successful_transaction(self):
        # Test a successful transaction that should commit
        with self.transaction_manager.transaction():
            # Simulate database operations
            self.mock_db.query.return_value.filter.return_value.first.return_value = "test_result"

        # Verify commit was called
        self.mock_db.commit.assert_called_once()
        # Verify rollback was not called
        self.mock_db.rollback.assert_not_called()

    def test_sqlalchemy_exception_transaction(self):
        # Test a transaction that encounters a SQLAlchemy error
        with self.assertRaises(SQLAlchemyError):
            with self.transaction_manager.transaction():
                # Simulate a database operation that fails by calling query
                self.mock_db.query.side_effect = SQLAlchemyError("Database error")
                self.mock_db.query()  # Trigger the exception

        # Verify commit was not called
        self.mock_db.commit.assert_not_called()
        # Verify rollback was called
        self.mock_db.rollback.assert_called_once()

    def test_general_exception_transaction(self):
        # Test a transaction that encounters a general exception
        with self.assertRaises(Exception):
            with self.transaction_manager.transaction():
                # Simulate a general error
                raise ValueError("Some error")

        # Verify commit was not called
        self.mock_db.commit.assert_not_called()
        # Verify rollback was called
        self.mock_db.rollback.assert_called_once()

    @patch('infrastructure.database.transaction_manager.logger')
    def test_logging_behavior(self, mock_logger):
        # Test logging behavior on success
        with self.transaction_manager.transaction():
            pass

        mock_logger.info.assert_called_with("Transaction committed successfully")

        # Test logging behavior on error
        mock_logger.reset_mock()
        test_error = SQLAlchemyError("Test database error")
        with self.assertRaises(SQLAlchemyError):
            with self.transaction_manager.transaction():
                raise test_error

        mock_logger.error.assert_called_with(f"Transaction rolled back due to error: {str(test_error)}")


if __name__ == '__main__':
    unittest.main()