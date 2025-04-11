import uuid
from domain.accounts import CheckingAccount, SavingsAccount

class AccountCreationService:
    def create_account(self, account_type: str, initial_deposit: float = 0.0):
        account_id = str(uuid.uuid4())

        if account_type.lower() == "savings":
            if initial_deposit < SavingsAccount.MINIMUM_BALANCE:
                raise ValueError(f"Savings account requires a minimum deposit of ${SavingsAccount.MINIMUM_BALANCE}")
            return SavingsAccount(account_id, initial_deposit)

        elif account_type.lower() == "checking":
            return CheckingAccount(account_id, initial_deposit)

        else:
            raise ValueError("Unknown account type. Choose 'checking' or 'savings'")
