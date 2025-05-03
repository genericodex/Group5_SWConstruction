# interest_repository.py

class InterestRepository:
    """A repository that manages retrieval and storage of interest rates."""

    def __init__(self, interest_data_source):
        """
        Initialize interest repository.
        :param interest_data_source: Can be a config file, a database, or an API service.
        """
        self.interest_data_source = interest_data_source

    def get_interest_rate(self, account_type):
        """
        Get interest rate for a specific account type.
        :param account_type: The type of account (e.g., "savings", "current").
        :return: The interest rate as a float.
        """
        rate = self.interest_data_source.get(account_type)
        if rate is None:
            raise ValueError(f"Interest rate for account type '{account_type}' not found.")
        return rate

    def set_interest_rate(self, account_type, rate):
        """
        Set or update interest rate for a specific account type.
        :param account_type: The type of account.
        :param rate: The interest rate to set as a float.
        """
        self.interest_data_source.set(account_type, rate)
