from dataclasses import dataclass
from domain.interest import SavingsInterestStrategy
from domain.accounts import Account, AccountType

class SavingsAccountType(AccountType):
    @property
    def name(self) -> str:
        return "SAVINGS"

@dataclass
class SavingsAccount(Account):
    """A savings account with a minimum balance requirement."""
    MINIMUM_BALANCE = 100.00

    def __init__(self, account_id: str, username: str, password: str, initial_balance: float = 0.0):
        super().__init__(
            account_id=account_id,
            account_type=SavingsAccountType(),
            username=username,
            _password_hash="",  # Temporary value; will be set by hash_password
            _balance=initial_balance
        )
        self.hash_password(password)
        self.set_interest_strategy(SavingsInterestStrategy())

    def can_withdraw(self, amount: float) -> bool:
        """Check if withdrawal is allowed while maintaining minimum balance."""
        return (self.balance() - amount) >= self.MINIMUM_BALANCE

    def __repr__(self) -> str:
        """Return a string representation of the savings account."""
        return (f"SavingsAccount(account_id={self.account_id}, "
                f"balance={self.balance()}, status={self.status.name}, "
                f"creation_date={self.creation_date})")