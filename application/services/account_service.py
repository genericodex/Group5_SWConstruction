import uuid
from application.repositories.account_repository import IAccountRepository
from domain.checking_account import CheckingAccount
from domain.savings_account import SavingsAccount
from application.services.notification_service import NotificationService


class AccountCreationService:
    def __init__(self, account_repository: IAccountRepository, notification_service: NotificationService):
        self.account_repository = account_repository
        self.notification_service = notification_service

    def create_account(self, account_type: str, username: str, password: str,
                      initial_deposit: float = 0.0, account_tier: str = "default") -> str:
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

        return account_id