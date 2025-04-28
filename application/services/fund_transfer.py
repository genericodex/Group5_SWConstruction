from typing import Optional
from application.repositories.account_repository import IAccountRepository
from application.repositories.transaction_repository import ITransactionRepository
from application.services.notification_service import NotificationService
from domain.accounts import Account
from application.exceptions.exceptions import AccountNotFoundError, InvalidTransferError
import time

class FundTransferService:
    def __init__(self,
                 account_repository: IAccountRepository,
                 transaction_repository: ITransactionRepository,
                 notification_service: NotificationService,
                 logging_service):
        self.account_repository = account_repository
        self.transaction_repository = transaction_repository
        self.notification_service = notification_service
        self.logging_service = logging_service

    def transfer_funds(self, from_account_id: str, to_account_id: str, amount: float) -> str:
        start_time = time.time()
        params = {"from_account_id": from_account_id, "to_account_id": to_account_id, "amount": amount}
        self.logging_service.log_service_call(
            service_name="FundTransferService",
            method_name="transfer_funds",
            status="started",
            duration_ms=0,
            params=params
        )

        try:
            # Retrieve source and target accounts
            from_account: Optional[Account] = self.account_repository.get_by_id(from_account_id)
            to_account: Optional[Account] = self.account_repository.get_by_id(to_account_id)

            if not from_account:
                raise AccountNotFoundError(f"Source account '{from_account_id}' not found.")
            if not to_account:
                raise AccountNotFoundError(f"Target account '{to_account_id}' not found.")

            # Perform the transfer using the domain layer
            try:
                transaction = from_account.transfer(amount, to_account)
            except ValueError as e:
                raise InvalidTransferError(str(e)) from e

            # Persist changes
            self.account_repository.save(from_account)
            self.account_repository.save(to_account)
            self.transaction_repository.save(transaction)

            # Log the transaction details
            self.logging_service.log_transaction(
                transaction_id=transaction.transaction_id,
                transaction_type="TRANSFER",
                amount=amount,
                account_id=from_account_id,
                status="success",
                details={"to_account_id": to_account_id}
            )

            # Log the successful service call
            duration_ms = (time.time() - start_time) * 1000
            self.logging_service.log_service_call(
                service_name="FundTransferService",
                method_name="transfer_funds",
                status="success",
                duration_ms=duration_ms,
                params=params,
                result=f"Transaction ID: {transaction.transaction_id}"
            )

            return transaction.transaction_id

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.logging_service.log_service_call(
                service_name="FundTransferService",
                method_name="transfer_funds",
                status="failed",
                duration_ms=duration_ms,
                params=params,
                error=str(e)
            )
            raise