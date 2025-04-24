class AccountNotFoundError(Exception):
    """Raised when an account is not found."""
    pass

class InvalidTransferError(Exception):
    """Raised when a transfer is invalid (e.g., insufficient funds, invalid amount)."""
    pass