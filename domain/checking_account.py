from dataclasses import dataclass
from domain.accounts import Account, AccountType


@dataclass
class CheckingAccount(Account):
    def __init__(self, account_id: str, initial_balance: float = 0.0):
        super().__init__(
            account_id=account_id,
            account_type=AccountType.CHECKING,
            _balance=initial_balance
        )

    def can_withdraw(self, amount: float) -> bool:
        return self.balance >= amount

    def __repr__(self):
        return (f"CheckingAccount(account_id={self.account_id}, "
                f"balance={self.balance}, status={self.status}, "
                f"creation_date={self.creation_date})")
