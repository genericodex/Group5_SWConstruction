# This file should be saved as:
# infrastructure/factories/repository_factory.py

from application.repositories.account_repository import IAccountRepository
from application.repositories.transaction_repository import ITransactionRepository
from infrastructure.repositories.FileTransactionRepository import FileTransactionRepository
from infrastructure.repositories.file_account_repository import FileAccountRepository
from infrastructure.storage.file_storage_service import FileStorageService


class RepositoryFactory:
    """Factory for creating repository instances"""

    _instance = None

    @classmethod
    def get_instance(cls):
        """Singleton pattern implementation"""
        if cls._instance is None:
            cls._instance = RepositoryFactory()
        return cls._instance

    def __init__(self, data_directory: str = "data"):
        self.storage_service = FileStorageService(data_directory)
        self._account_repository = None
        self._transaction_repository = None

    def get_account_repository(self) -> IAccountRepository:
        """Get or create a new account repository"""
        if self._account_repository is None:
            self._account_repository = FileAccountRepository(
                storage_dir=self.storage_service.get_storage_dir("accounts")
            )
        return self._account_repository

    def get_transaction_repository(self) -> ITransactionRepository:
        """Get or create a new transaction repository"""
        if self._transaction_repository is None:
            self._transaction_repository = FileTransactionRepository(
                storage_dir=self.storage_service.get_storage_dir("transactions")
            )
        return self._transaction_repository