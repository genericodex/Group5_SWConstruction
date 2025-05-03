"""
Dependency injection configuration for the banking application.
This file shows how to wire up the different layers following clean architecture.
"""




from application.services.logging_service import LoggingService
from infrastructure.interest.interest_repository_impl import InterestRepositoryImpl
from infrastructure.interest.interest_data_source import FileInterestDataSource, ApiInterestDataSource, \
    ConfigInterestDataSource
from application.services.interest_service import InterestService
from infrastructure.repositories.account_repository import AccountRepository


def configure_dependencies(config):
    """
    Configure application dependencies.

    :param config: Application configuration
    :return: Dictionary of configured services
    """
    # Create logging service
    logging_service = LoggingService(config.get("logging.level", "INFO"))

    # Configure data sources
    interest_data_source_type = config.get("interest.data_source.type", "file")

    if interest_data_source_type == "file":
        file_path = config.get("interest.data_source.file_path", "data/interest_rates.json")
        interest_data_source = FileInterestDataSource(file_path)
    elif interest_data_source_type == "api":
        api_client = config.get("interest.data_source.api_client")
        interest_data_source = ApiInterestDataSource(api_client)
    elif interest_data_source_type == "config":
        interest_data_source = ConfigInterestDataSource(config)
    else:
        raise ValueError(f"Unknown interest data source type: {interest_data_source_type}")

    # Create repositories
    account_repository = AccountRepository(
        db_connection=config.get("database.connection"),
        logging_service=logging_service
    )

    interest_repository = InterestRepositoryImpl(
        interest_data_source=interest_data_source,
        logging_service=logging_service
    )

    # Create services
    interest_service = InterestService(
        account_repository=account_repository,
        interest_repository=interest_repository,
        logging_service=logging_service
    )

    # Return the configured services
    return {
        "logging_service": logging_service,
        "account_repository": account_repository,
        "interest_repository": interest_repository,
        "interest_service": interest_service
    }


def example_usage():
    """Example usage of the dependency injection"""
    # Sample config
    config = {
        "logging.level": "INFO",
        "interest.data_source.type": "file",
        "interest.data_source.file_path": "data/interest_rates.json",
        "database.connection": "sqlite:///banking.db"
    }

    # Configure dependencies
    services = configure_dependencies(config)

    # Use the interest service
    interest_service = services["interest_service"]

    # Apply interest to a single account
    interest_service.apply_interest_to_account("1234")

    # Apply interest to multiple accounts
    interest_service.apply_interest_batch(["1234", "5678"])