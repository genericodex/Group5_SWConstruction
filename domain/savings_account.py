from dataclasses import dataclass
from domain.accounts import Account, AccountType

class SavingsAccountType(AccountType):
    @property
    def name(self) -> str:
        return "SAVINGS"

@dataclass
class SavingsAccount(Account):
    MINIMUM_BALANCE = 100.00

    def __init__(self, account_id: str, initial_balance: float = 0.0):
        super().__init__(
            account_id=account_id,
            account_type=SavingsAccountType(),
            _balance=initial_balance
        )

    def can_withdraw(self, amount: float) -> bool:
        return (self.balance - amount) >= self.MINIMUM_BALANCE

    def __repr__(self):
        return (f"SavingsAccount(account_id={self.account_id}, "
                f"balance={self.balance}, status={self.status}, "
                f"creation_date={self.creation_date})")
