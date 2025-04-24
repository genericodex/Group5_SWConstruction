from dataclasses import dataclass
from domain.accounts import Account, AccountType

class CheckingAccountType(AccountType):
    @property
    def name(self) -> str:
        return "CHECKING"

@dataclass
class CheckingAccount(Account):
    def __init__(self, account_id: str, username: str, password: str, initial_balance: float = 0.0):
        super().__init__(
            account_id=account_id,
            account_type=CheckingAccountType(),
            username=username,
            _password_hash="",  # Temporary value; will be set by hash_password
            _balance=initial_balance
        )
        self.hash_password(password)

    def can_withdraw(self, amount: float) -> bool:
        return self.balance() >= amount

    def __repr__(self):
        return (f"CheckingAccount(account_id={self.account_id}, "
                f"balance={self.balance()}, status={self.status.name}, "
                f"creation_date={self.creation_date})")
