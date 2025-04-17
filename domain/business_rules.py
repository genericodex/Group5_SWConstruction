from domain.accounts import Account


class BusinessRuleService:
    @staticmethod
    def check_withdraw_allowed(account: Account, amount: float) -> bool:
        return account.can_withdraw(amount)

    @staticmethod
    def validate_deposit_amount(amount: float) -> bool:
        return amount > 0
