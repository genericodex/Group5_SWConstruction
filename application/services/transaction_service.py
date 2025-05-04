"""
Transaction service in the application layer.
This orchestrates transaction operations using domain entities and repositories.
"""
from datetime import datetime
import time
from typing import Dict, Any, Optional

from application.repositories.account_repository import IAccountRepository
from application.repositories.transaction_repository import ITransactionRepository, ITransactionLimitRepository
from application.services.notification_service import NotificationService

from domain.transaction_limits import TransactionLimits
from domain.transactions import Transaction, DepositTransactionType, WithdrawTransactionType, TransferTransactionType


class TransactionService:
    """Service for handling banking transactions."""

    def __init__(self,
                 transaction_repository: ITransactionRepository,
                 account_repository: IAccountRepository,
                 transaction_limit_repository: ITransactionLimitRepository,
                 notification_service: NotificationService,
                 logging_service):
        """
        Initialize transaction service.

        :param transaction_repository: Repository for transaction operations
        :param account_repository: Repository for account operations
        :param transaction_limit_repository: Repository for transaction limits
        :param notification_service: Service for sending notifications
        :param logging_service: Service for logging operations
        """
        self.transaction_repository = transaction_repository
        self.account_repository = account_repository
        self.transaction_limit_repository = transaction_limit_repository
        self.notification_service = notification_service
        self.logging_service = logging_service

    def _check_transaction_limits(self, account_id: str, amount: float,
                                  transaction_date: Optional[datetime] = None) -> bool:
        """
        Check if transaction is within limits.

        :param account_id: Account identifier
        :param amount: Transaction amount
        :param transaction_date: Optional transaction date
        :return: True if within limits, False otherwise
        """
        # Create transaction limits instance for this account
        limits = TransactionLimits(self.transaction_limit_repository, account_id)

        # Check if transaction is within limits
        date_to_check = transaction_date.date() if transaction_date else None
        return limits.can_process_transaction(amount, date_to_check)

    def _record_transaction_usage(self, account_id: str, amount: float,
                                  transaction_date: Optional[datetime] = None) -> None:
        """
        Record transaction in usage data.

        :param account_id: Account identifier
        :param amount: Transaction amount
        :param transaction_date: Optional transaction date
        """
        # Create transaction limits instance for this account
        limits = TransactionLimits(self.transaction_limit_repository, account_id)

        # Record transaction in usage data
        date_to_record = transaction_date.date() if transaction_date else None
        limits.record_transaction(amount, date_to_record)

    def deposit(self, account_id: str, amount: float, transaction_date: Optional[datetime] = None) -> Transaction:
        """
        Deposit money into an account.

        :param account_id: Account identifier
        :param amount: Deposit amount
        :param transaction_date: Optional transaction date
        :return: Transaction object
        """
        # Log the start of the service call
        start_time = time.time()
        params = {"account_id": account_id, "amount": amount}
        if transaction_date:
            params["transaction_date"] = transaction_date.isoformat()

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

            # Check if transaction is within limits
            if not self._check_transaction_limits(account_id, amount, transaction_date):
                raise ValueError(f"Transaction exceeds limits for account {account_id}")

            # Perform deposit (using transaction_date if provided)
            transaction = account.deposit(amount)
            if transaction_date:
                transaction.timestamp = transaction_date

            # Record transaction in usage data
            self._record_transaction_usage(account_id, amount, transaction_date)

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

            # Send notification if enabled
            try:
                self.notification_service.send_transaction_notification(
                    account_id, "deposit", amount)
            except Exception as notify_error:
                # Log but don't fail the transaction
                self.logging_service.warning(
                    f"Failed to send notification: {str(notify_error)}",
                    {"account_id": account_id}
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

    def withdraw(self, account_id: str, amount: float, transaction_date: Optional[datetime] = None) -> Transaction:
        """
        Withdraw money from an account.

        :param account_id: Account identifier
        :param amount: Withdrawal amount
        :param transaction_date: Optional transaction date
        :return: Transaction object
        """
        # Log the start of the service call
        start_time = time.time()
        params = {"account_id": account_id, "amount": amount}
        if transaction_date:
            params["transaction_date"] = transaction_date.isoformat()

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

            # Check if transaction is within limits
            if not self._check_transaction_limits(account_id, amount, transaction_date):
                raise ValueError(f"Transaction exceeds limits for account {account_id}")

            # Perform withdrawal (using transaction_date if provided)
            transaction = account.withdraw(amount)
            if transaction_date:
                transaction.timestamp = transaction_date

            # Record transaction in usage data
            self._record_transaction_usage(account_id, amount, transaction_date)

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

            # Send notification if enabled
            try:
                self.notification_service.send_transaction_notification(
                    account_id, "withdraw", amount)
            except Exception as notify_error:
                # Log but don't fail the transaction
                self.logging_service.warning(
                    f"Failed to send notification: {str(notify_error)}",
                    {"account_id": account_id}
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

    def transfer(self, source_account_id: str, destination_account_id: str, amount: float,
                 transaction_date: Optional[datetime] = None) -> Dict[str, Transaction]:
        """
        Transfer money between accounts.

        :param source_account_id: Source account identifier
        :param destination_account_id: Destination account identifier
        :param amount: Transfer amount
        :param transaction_date: Optional transaction date
        :return: Dictionary with source and destination transactions
        """
        # Log the start of the service call
        start_time = time.time()
        params = {
            "source_account_id": source_account_id,
            "destination_account_id": destination_account_id,
            "amount": amount
        }
        if transaction_date:
            params["transaction_date"] = transaction_date.isoformat()

        self.logging_service.log_service_call(
            service_name="TransactionService",
            method_name="transfer",
            status="started",
            duration_ms=0,
            params=params
        )

        try:
            # Get accounts from repository
            source_account = self.account_repository.get_by_id(source_account_id)
            destination_account = self.account_repository.get_by_id(destination_account_id)

            if not source_account:
                raise ValueError(f"Source account with ID {source_account_id} not found")
            if not destination_account:
                raise ValueError(f"Destination account with ID {destination_account_id} not found")

            # Check if transaction is within limits for source account
            if not self._check_transaction_limits(source_account_id, amount, transaction_date):
                raise ValueError(f"Transaction exceeds limits for account {source_account_id}")

            # Create a transfer transaction type
            transfer_type = TransferTransactionType()

            # Withdraw from source account
            source_transaction = source_account.withdraw(amount)
            if transaction_date:
                source_transaction.timestamp = transaction_date
            source_transaction.transaction_type = transfer_type
            source_transaction.source_account_id = source_account_id
            source_transaction.destination_account_id = destination_account_id

            # Deposit to destination account
            destination_transaction = destination_account.deposit(amount)
            if transaction_date:
                destination_transaction.timestamp = transaction_date
            destination_transaction.transaction_type = transfer_type
            destination_transaction.source_account_id = source_account_id
            destination_transaction.destination_account_id = destination_account_id

            # Record transaction in usage data
            self._record_transaction_usage(source_account_id, amount, transaction_date)

            # Save transactions to repository
            self.transaction_repository.save(source_transaction)
            self.transaction_repository.save(destination_transaction)

            # Update accounts in repository
            self.account_repository.save(source_account)
            self.account_repository.save(destination_account)

            # Log the transaction details
            self.logging_service.log_transaction(
                transaction_id=source_transaction.transaction_id,
                transaction_type="TRANSFER",
                amount=amount,
                account_id=source_account_id,
                destination_account_id=destination_account_id,
                status="success"
            )

            # Send notification if enabled
            try:
                self.notification_service.send_transaction_notification(
                    source_account_id, "transfer_out", amount, destination_account_id=destination_account_id)
                self.notification_service.send_transaction_notification(
                    destination_account_id, "transfer_in", amount, source_account_id=source_account_id)
            except Exception as notify_error:
                # Log but don't fail the transaction
                self.logging_service.warning(
                    f"Failed to send notification: {str(notify_error)}",
                    {"source_account_id": source_account_id, "destination_account_id": destination_account_id}
                )

            # Log the successful service call
            duration_ms = (time.time() - start_time) * 1000
            self.logging_service.log_service_call(
                service_name="TransactionService",
                method_name="transfer",
                status="success",
                duration_ms=duration_ms,
                params=params,
                result=f"Source Transaction ID: {source_transaction.transaction_id}, Destination Transaction ID: {destination_transaction.transaction_id}"
            )

            return {
                "source": source_transaction,
                "destination": destination_transaction
            }

        except Exception as e:
            # Log the failed service call
            duration_ms = (time.time() - start_time) * 1000
            self.logging_service.log_service_call(
                service_name="TransactionService",
                method_name="transfer",
                status="failed",
                duration_ms=duration_ms,
                params=params,
                error=str(e)
            )
            raise