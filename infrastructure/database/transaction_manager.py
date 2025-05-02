from sqlalchemy.orm import Session
from contextlib import contextmanager
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)


class TransactionManager:
    """
    Handles database transaction management to ensure atomicity for operations
    that affect multiple records, like fund transfers between accounts.
    """

    def __init__(self, db: Session):
        self.db = db

    @contextmanager
    def transaction(self):
        """
        Context manager that provides transaction control with automatic
        commit on success and rollback on exception.

        Usage:
            with transaction_manager.transaction():
                # Perform multiple database operations atomically
                # All operations will be committed if no exception occurs
                # All operations will be rolled back if an exception occurs
        """
        try:
            # The transaction is already started by SQLAlchemy when the session is created
            yield self.db
            self.db.commit()
            logger.info("Transaction committed successfully")
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Transaction rolled back due to error: {str(e)}")
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Transaction rolled back due to unexpected error: {str(e)}")
            raise