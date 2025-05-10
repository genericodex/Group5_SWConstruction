import unittest
import os
import json
import tempfile
from unittest.mock import Mock

from infrastructure.interest.interest_data_source import FileInterestDataSource, ApiInterestDataSource, \
    ConfigInterestDataSource


class TestFileInterestDataSource(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for test files
        self.temp_dir = tempfile.mkdtemp()
        self.file_path = os.path.join(self.temp_dir, 'rates.json')
        self.data_source = FileInterestDataSource(self.file_path)

    def tearDown(self):
        # Clean up temporary directory
        if os.path.exists(self.temp_dir):
            for root, dirs, files in os.walk(self.temp_dir, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(self.temp_dir)

    def test_ensure_file_exists(self):
        # Test that file is created with default values
        self.assertTrue(os.path.exists(self.file_path))
        with open(self.file_path, 'r') as f:
            data = json.load(f)
            self.assertEqual(data, {"savings": 0.025, "checking": 0.001})

    def test_get_existing_rate(self):
        # Test getting an existing rate
        rate = self.data_source.get("savings")
        self.assertEqual(rate, 0.025)

    def test_get_nonexistent_rate(self):
        # Test getting a nonexistent rate
        rate = self.data_source.get("premium")
        self.assertIsNone(rate)

    def test_set_and_get_rate(self):
        # Test setting and getting a rate
        self.data_source.set("premium", 0.05)
        rate = self.data_source.get("premium")
        self.assertEqual(rate, 0.05)

    def test_corrupted_file_handling(self):
        # Test handling of corrupted file
        with open(self.file_path, 'w') as f:
            f.write("invalid json")
        rate = self.data_source.get("savings")
        self.assertEqual(rate, 0.025)  # Should recreate file with defaults


class TestApiInterestDataSource(unittest.TestCase):
    def setUp(self):
        # Create mock API client
        self.api_client = Mock()
        self.data_source = ApiInterestDataSource(self.api_client)

    def test_get_rate_success(self):
        # Test successful rate retrieval
        self.api_client.get_interest_rate.return_value = {'rate': 0.03}
        rate = self.data_source.get("savings")
        self.assertEqual(rate, 0.03)
        self.api_client.get_interest_rate.assert_called_once_with("savings")

    def test_get_rate_failure(self):
        # Test failed rate retrieval
        self.api_client.get_interest_rate.return_value = None
        rate = self.data_source.get("savings")
        self.assertIsNone(rate)
        self.api_client.get_interest_rate.assert_called_once_with("savings")

    def test_set_rate(self):
        # Test setting rate
        self.data_source.set("checking", 0.01)
        self.api_client.set_interest_rate.assert_called_once_with("checking", 0.01)


class TestConfigInterestDataSource(unittest.TestCase):
    def setUp(self):
        # Create mock config
        self.config = Mock()
        self.data_source = ConfigInterestDataSource(self.config)

    def test_get_rate(self):
        # Test getting rate from config
        self.config.get.return_value = 0.015
        rate = self.data_source.get("savings")
        self.assertEqual(rate, 0.015)
        self.config.get.assert_called_once_with("interest.rates.savings")

    def test_get_nonexistent_rate(self):
        # Test getting nonexistent rate
        self.config.get.return_value = None
        rate = self.data_source.get("premium")
        self.assertIsNone(rate)
        self.config.get.assert_called_once_with("interest.rates.premium")

    def test_set_rate(self):
        # Test setting rate in config
        self.data_source.set("checking", 0.005)
        self.config.set.assert_called_once_with("interest.rates.checking", 0.005)


if __name__ == '__main__':
    unittest.main()