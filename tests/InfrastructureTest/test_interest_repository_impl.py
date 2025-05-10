import unittest
from unittest.mock import Mock

from infrastructure.interest.interest_repository_impl import InterestRepositoryImpl


class TestInterestRepositoryImpl(unittest.TestCase):
    def setUp(self):
        # Create mocks for dependencies
        self.data_source = Mock()
        self.logging_service = Mock()
        self.repository = InterestRepositoryImpl(self.data_source, self.logging_service)

    def test_get_interest_rate_from_data_source(self):
        # Test getting rate from data source
        self.data_source.get.return_value = 0.025
        rate = self.repository.get_interest_rate("savings")
        self.assertEqual(rate, 0.025)
        self.data_source.get.assert_called_once_with("savings")
        self.logging_service.debug.assert_called_once_with(
            "Retrieved interest rate for savings",
            {"account_type": "savings", "rate": 0.025}
        )

    def test_get_interest_rate_from_cache(self):
        # Test getting rate from cache
        self.repository._cache["savings"] = 0.025
        rate = self.repository.get_interest_rate("savings")
        self.assertEqual(rate, 0.025)
        self.data_source.get.assert_not_called()
        self.logging_service.debug.assert_not_called()

    def test_get_interest_rate_not_found(self):
        # Test handling of non-existent rate
        self.data_source.get.return_value = None
        with self.assertRaises(ValueError) as context:
            self.repository.get_interest_rate("premium")
        self.assertEqual(str(context.exception), "Interest rate for account type 'premium' not found.")
        self.data_source.get.assert_called_once_with("premium")
        self.logging_service.error.assert_called_once_with(
            "Interest rate for account type 'premium' not found."
        )

    def test_set_interest_rate_valid(self):
        # Test setting a valid rate
        self.repository.set_interest_rate("checking", 0.01)
        self.data_source.set.assert_called_once_with("checking", 0.01)
        self.assertEqual(self.repository._cache["checking"], 0.01)
        self.logging_service.info.assert_called_once_with(
            "Updated interest rate for checking",
            {"account_type": "checking", "new_rate": 0.01}
        )

    def test_set_interest_rate_negative(self):
        # Test setting a negative rate
        with self.assertRaises(ValueError) as context:
            self.repository.set_interest_rate("savings", -0.01)
        self.assertEqual(str(context.exception), "Interest rate cannot be negative: -0.01")
        self.data_source.set.assert_not_called()
        self.logging_service.error.assert_called_once_with("Interest rate cannot be negative: -0.01")
        self.assertNotIn("savings", self.repository._cache)

    def test_clear_cache(self):
        # Test clearing the cache
        self.repository._cache["savings"] = 0.025
        self.repository.clear_cache()
        self.assertEqual(self.repository._cache, {})
        self.logging_service.debug.assert_called_once_with("Interest rate cache cleared")

    def test_no_logging_service(self):
        # Test behavior without logging service
        repository = InterestRepositoryImpl(self.data_source, None)
        self.data_source.get.return_value = 0.025
        rate = repository.get_interest_rate("savings")
        self.assertEqual(rate, 0.025)
        self.data_source.get.assert_called_once_with("savings")
        # No logging calls should occur
        self.logging_service.debug.assert_not_called()


if __name__ == '__main__':
    unittest.main()