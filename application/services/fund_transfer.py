from typing import Optional
from application.repositories.account_repository import IAccountRepository
from application.repositories.transaction_repository import ITransactionRepository
from application.services.notification_service import NotificationService
from domain.accounts import Account
from application.exceptions.exceptions import AccountNotFoundError, InvalidTransferError

class FundTransferService:
    def __init__(self,
                 account_repository: IAccountRepository,
                 transaction_repository: ITransactionRepository,
                 notification_service: NotificationService):
        self.account_repository = account_repository
        self.transaction_repository = transaction_repository
        self.notification_service = notification_service

    def transfer_funds(self, from_account_id: str, to_account_id: str, amount: float) -> str:
        """
        Transfer funds from one account to another.

        :param from_account_id: The ID of the source account.
        :param to_account_id: The ID of the target account.
        :param amount: Amount of funds to transfer.
        :return: A transfer transaction ID for reference.
        :raises AccountNotFoundError: If an account is not found.
        :raises InvalidTransferError: If the transfer is invalid (e.g., insufficient funds).
        """
        # Retrieve source and target accounts
        from_account: Optional[Account] = self.account_repository.get_by_id(from_account_id)
        to_account: Optional[Account] = self.account_repository.get_by_id(to_account_id)

        if not from_account:
            raise AccountNotFoundError(f"Source account '{from_account_id}' not found.")
        if not to_account:
            raise AccountNotFoundError(f"Target account '{to_account_id}' not found.")

        try:
            # Perform the transfer using the domain layer
            transaction = from_account.transfer(amount, to_account)
        except ValueError as e:
            raise InvalidTransferError(str(e))

        # Persist changes
        self.account_repository.save(from_account)
        self.account_repository.save(to_account)
        self.transaction_repository.save(transaction)

        # If for some reason notification wasn't triggered via observers,
        # we can manually trigger it here
        # self.notification_service.notify_transaction(transaction)

        return transaction.transaction_id