import uuid
from application.repositories.account_repository import IAccountRepository
from domain.accounts import CheckingAccount, SavingsAccount


class AccountCreationService:
    def __init__(self, account_repository: IAccountRepository):
        self.account_repository = account_repository

    def create_account(self, account_type: str, initial_deposit: float = 0.0) -> str:
        account_id = str(uuid.uuid4())

        if account_type.lower() == "savings":
            if initial_deposit < SavingsAccount.MINIMUM_BALANCE:
                raise ValueError(f"Savings account requires a minimum deposit of ${SavingsAccount.MINIMUM_BALANCE}")
            account = SavingsAccount(account_id, initial_deposit)
        elif account_type.lower() == "checking":
            account = CheckingAccount(account_id, initial_deposit)
        else:
            raise ValueError("Unknown account type. Choose 'checking' or 'savings'")

        # Save the account to repository
        self.account_repository.save(account)

        return account_id
