from application.repositories.account_repository import IAccountRepository
from application.repositories.transaction_repository import ITransactionRepository
from application.services.notification_service import NotificationService
from domain.transactions import Transaction
import time

class TransactionService:
    def __init__(self,
                 transaction_repository: ITransactionRepository,
                 account_repository: IAccountRepository,
                 notification_service: NotificationService,
                 logging_service):  # Add LoggingService dependency
        self.transaction_repository = transaction_repository
        self.account_repository = account_repository
        self.notification_service = notification_service
        self.logging_service = logging_service  # Initialize LoggingService

    def deposit(self, account_id: str, amount: float) -> Transaction:
        # Log the start of the service call
        start_time = time.time()
        params = {"account_id": account_id, "amount": amount}
        self.logging_service.log_service_call(
            service_name="TransactionService",
            method_name="deposit",
            status="started",
            duration_ms=0,
            params=params
        )

        try:
            # Get account from repository
            account = self.account_repository.get_by_id(account_id)
            if not account:
                raise ValueError(f"Account with ID {account_id} not found")

            # Perform deposit
            transaction = account.deposit(amount)

            # Save transaction to repository
            self.transaction_repository.save(transaction)

            # Update account in repository
            self.account_repository.save(account)

            # Log the transaction details
            self.logging_service.log_transaction(
                transaction_id=transaction.transaction_id,
                transaction_type="DEPOSIT",
                amount=amount,
                account_id=account_id,
                status="success"
            )

            # Log the successful service call
            duration_ms = (time.time() - start_time) * 1000
            self.logging_service.log_service_call(
                service_name="TransactionService",
                method_name="deposit",
                status="success",
                duration_ms=duration_ms,
                params=params,
                result=f"Transaction ID: {transaction.transaction_id}"
            )

            return transaction

        except Exception as e:
            # Log the failed service call
            duration_ms = (time.time() - start_time) * 1000
            self.logging_service.log_service_call(
                service_name="TransactionService",
                method_name="deposit",
                status="failed",
                duration_ms=duration_ms,
                params=params,
                error=str(e)
            )
            raise

    def withdraw(self, account_id: str, amount: float) -> Transaction:
        # Log the start of the service call
        start_time = time.time()
        params = {"account_id": account_id, "amount": amount}
        self.logging_service.log_service_call(
            service_name="TransactionService",
            method_name="withdraw",
            status="started",
            duration_ms=0,
            params=params
        )

        try:
            # Get account from repository
            account = self.account_repository.get_by_id(account_id)
            if not account:
                raise ValueError(f"Account with ID {account_id} not found")

            # Perform withdrawal
            transaction = account.withdraw(amount)

            # Save transaction to repository
            self.transaction_repository.save(transaction)

            # Update account in repository
            self.account_repository.save(account)

            # Log the transaction details
            self.logging_service.log_transaction(
                transaction_id=transaction.transaction_id,
                transaction_type="WITHDRAW",
                amount=amount,
                account_id=account_id,
                status="success"
            )

            # Log the successful service call
            duration_ms = (time.time() - start_time) * 1000
            self.logging_service.log_service_call(
                service_name="TransactionService",
                method_name="withdraw",
                status="success",
                duration_ms=duration_ms,
                params=params,
                result=f"Transaction ID: {transaction.transaction_id}"
            )

            return transaction

        except Exception as e:
            # Log the failed service call
            duration_ms = (time.time() - start_time) * 1000
            self.logging_service.log_service_call(
                service_name="TransactionService",
                method_name="withdraw",
                status="failed",
                duration_ms=duration_ms,
                params=params,
                error=str(e)
            )
            raise