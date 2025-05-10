import unittest
from unittest.mock import Mock, patch
import json
import os
from application.services.logging_service import LoggingService
from application.services.interest_service import InterestService
from infrastructure.interest.dependency_injection import configure_dependencies
from infrastructure.interest.interest_repository_impl import InterestRepositoryImpl
from infrastructure.interest.interest_data_source import FileInterestDataSource, ApiInterestDataSource, \
    ConfigInterestDataSource
from infrastructure.repositories.account_repository import AccountRepository


class TestDependencyInjection(unittest.TestCase):
    def setUp(self):
        self.config = {
            "logging.level": "INFO",
            "interest.data_source.type": "file",
            "interest.data_source.file_path": "test_interest_rates.json",
            "database.connection": "sqlite:///test.db"
        }
        self.test_file_path = "test_interest_rates.json"

    def tearDown(self):
        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)

    @patch('infrastructure.interest.dependency_injection.AccountRepository')
    def test_configure_dependencies_file_datasource(self, mock_account_repository):
        mock_account_repository.return_value = Mock()
        services = configure_dependencies(self.config)

        self.assertIsInstance(services["logging_service"], LoggingService)
        self.assertIsInstance(services["account_repository"], Mock)
        self.assertIsInstance(services["interest_repository"], InterestRepositoryImpl)
        self.assertIsInstance(services["interest_service"], InterestService)
        self.assertIsInstance(services["interest_repository"].interest_data_source, FileInterestDataSource)

    @patch('infrastructure.interest.dependency_injection.AccountRepository')
    def test_configure_dependencies_api_datasource(self, mock_account_repository):
        mock_account_repository.return_value = Mock()
        config = self.config.copy()
        config["interest.data_source.type"] = "api"
        config["interest.data_source.api_client"] = Mock()

        services = configure_dependencies(config)

        self.assertIsInstance(services["interest_repository"].interest_data_source, ApiInterestDataSource)

    @patch('infrastructure.interest.dependency_injection.AccountRepository')
    def test_configure_dependencies_config_datasource(self, mock_account_repository):
        mock_account_repository.return_value = Mock()
        config = self.config.copy()
        config["interest.data_source.type"] = "config"

        services = configure_dependencies(config)

        self.assertIsInstance(services["interest_repository"].interest_data_source, ConfigInterestDataSource)

    def test_configure_dependencies_invalid_datasource(self):
        config = self.config.copy()
        config["interest.data_source.type"] = "invalid"

        with self.assertRaises(ValueError) as context:
            configure_dependencies(config)
        self.assertEqual(str(context.exception), "Unknown interest data source type: invalid")


class TestInterestRepositoryImpl(unittest.TestCase):
    def setUp(self):
        self.mock_data_source = Mock()
        self.mock_logging_service = Mock()
        self.repository = InterestRepositoryImpl(self.mock_data_source, self.mock_logging_service)

    def test_get_interest_rate_from_cache(self):
        self.repository._cache["savings"] = 0.025
        rate = self.repository.get_interest_rate("savings")

        self.assertEqual(rate, 0.025)
        self.mock_data_source.get.assert_not_called()

    def test_get_interest_rate_from_datasource(self):
        self.mock_data_source.get.return_value = 0.025
        rate = self.repository.get_interest_rate("savings")

        self.assertEqual(rate, 0.025)
        self.mock_data_source.get.assert_called_once_with("savings")
        self.assertEqual(self.repository._cache["savings"], 0.025)
        self.mock_logging_service.debug.assert_called()

    def test_get_interest_rate_not_found(self):
        self.mock_data_source.get.return_value = None

        with self.assertRaises(ValueError) as context:
            self.repository.get_interest_rate("savings")
        self.assertEqual(str(context.exception), "Interest rate for account type 'savings' not found.")
        self.mock_logging_service.error.assert_called()

    def test_set_interest_rate_valid(self):
        self.repository.set_interest_rate("savings", 0.03)

        self.mock_data_source.set.assert_called_once_with("savings", 0.03)
        self.assertEqual(self.repository._cache["savings"], 0.03)
        self.mock_logging_service.info.assert_called()

    def test_set_interest_rate_negative(self):
        with self.assertRaises(ValueError) as context:
            self.repository.set_interest_rate("savings", -0.01)
        self.assertEqual(str(context.exception), "Interest rate cannot be negative: -0.01")
        self.mock_logging_service.error.assert_called()

    def test_clear_cache(self):
        self.repository._cache["savings"] = 0.025
        self.repository.clear_cache()

        self.assertEqual(len(self.repository._cache), 0)
        self.mock_logging_service.debug.assert_called()


class TestFileInterestDataSource(unittest.TestCase):
    def setUp(self):
        self.file_path = "test_interest_rates.json"
        self.data_source = FileInterestDataSource(self.file_path)

    def tearDown(self):
        if os.path.exists(self.file_path):
            os.remove(self.file_path)

    def test_ensure_file_exists(self):
        if os.path.exists(self.file_path):
            os.remove(self.file_path)

        self.data_source._ensure_file_exists()

        self.assertTrue(os.path.exists(self.file_path))
        with open(self.file_path, 'r') as file:
            data = json.load(file)
            self.assertEqual(data, {"savings": 0.025, "checking": 0.001})

    def test_get_interest_rate(self):
        with open(self.file_path, 'w') as file:
            json.dump({"savings": 0.03}, file)

        rate = self.data_source.get("savings")
        self.assertEqual(rate, 0.03)

    def test_get_interest_rate_not_found(self):
        with open(self.file_path, 'w') as file:
            json.dump({"savings": 0.03}, file)

        rate = self.data_source.get("checking")
        self.assertIsNone(rate)

    def test_set_interest_rate(self):
        self.data_source.set("savings", 0.04)

        with open(self.file_path, 'r') as file:
            data = json.load(file)
            self.assertEqual(data["savings"], 0.04)


class TestApiInterestDataSource(unittest.TestCase):
    def setUp(self):
        self.mock_api_client = Mock()
        self.data_source = ApiInterestDataSource(self.mock_api_client)

    def test_get_interest_rate(self):
        self.mock_api_client.get_interest_rate.return_value = {"rate": 0.025}

        rate = self.data_source.get("savings")
        self.assertEqual(rate, 0.025)
        self.mock_api_client.get_interest_rate.assert_called_once_with("savings")

    def test_get_interest_rate_none(self):
        self.mock_api_client.get_interest_rate.return_value = None

        rate = self.data_source.get("savings")
        self.assertIsNone(rate)

    def test_set_interest_rate(self):
        self.data_source.set("savings", 0.03)

        self.mock_api_client.set_interest_rate.assert_called_once_with("savings", 0.03)


class TestConfigInterestDataSource(unittest.TestCase):
    def setUp(self):
        self.mock_config = Mock()
        self.data_source = ConfigInterestDataSource(self.mock_config)

    def test_get_interest_rate(self):
        self.mock_config.get.return_value = 0.025

        rate = self.data_source.get("savings")
        self.assertEqual(rate, 0.025)
        self.mock_config.get.assert_called_once_with("interest.rates.savings")

    def test_set_interest_rate(self):
        self.data_source.set("savings", 0.03)

        self.mock_config.set.assert_called_once_with("interest.rates.savings", 0.03)


if __name__ == '__main__':
    unittest.main()