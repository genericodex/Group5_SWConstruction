import uuid
from application.repositories.account_repository import IAccountRepository
from domain.checking_account import CheckingAccount
from domain.savings_account import SavingsAccount
from application.services.notification_service import NotificationService
import time

class AccountCreationService:
    def __init__(self, account_repository: IAccountRepository, notification_service: NotificationService, logging_service):
        self.account_repository = account_repository
        self.notification_service = notification_service
        self.logging_service = logging_service  # Add LoggingService dependency

    def create_account(self, account_type: str, username: str, password: str,
                      initial_deposit: float = 0.0, account_tier: str = "default") -> str:
        # Log the start of the service call
        start_time = time.time()
        params = {
            "account_type": account_type,
            "username": username,
            "initial_deposit": initial_deposit,
            "account_tier": account_tier
        }
        self.logging_service.log_service_call(
            service_name="AccountCreationService",
            method_name="create_account",
            status="started",
            duration_ms=0,
            params=params
        )

        try:
            account_id = str(uuid.uuid4())

            if account_type.lower() == "savings":
                if initial_deposit < SavingsAccount.MINIMUM_BALANCE:
                    raise ValueError(f"Savings account requires a minimum deposit of ${SavingsAccount.MINIMUM_BALANCE}")
                account = SavingsAccount(account_id, username, password, initial_deposit)
                # Premium tier for savings accounts with high initial deposit
                if initial_deposit >= 1000:
                    account_tier = "premium"
            elif account_type.lower() == "checking":
                account = CheckingAccount(account_id, username, password, initial_deposit)
                # Standard tier for checking accounts
                if account_tier == "default":
                    account_tier = "standard"
            else:
                raise ValueError("Unknown account type. Choose 'checking' or 'savings'")

            # Register notification observers based on account tier
            self.notification_service.register_account_observers(account, account_tier)

            # Save the account to repository
            self.account_repository.save(account)

            # Log the account creation details
            self.logging_service.info(
                message=f"Account created successfully",
                context={
                    "account_id": account_id,
                    "account_type": account_type,
                    "username": username,
                    "initial_deposit": initial_deposit,
                    "account_tier": account_tier
                }
            )

            # Log the successful service call
            duration_ms = (time.time() - start_time) * 1000
            self.logging_service.log_service_call(
                service_name="AccountCreationService",
                method_name="create_account",
                status="success",
                duration_ms=duration_ms,
                params=params,
                result=f"Account ID: {account_id}"
            )

            return account_id

        except Exception as e:
            # Log the failed service call
            duration_ms = (time.time() - start_time) * 1000
            self.logging_service.log_service_call(
                service_name="AccountCreationService",
                method_name="create_account",
                status="failed",
                duration_ms=duration_ms,
                params=params,
                error=str(e)
            )
            raise