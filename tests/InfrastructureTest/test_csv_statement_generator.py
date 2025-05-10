import unittest
from io import StringIO
from unittest.mock import patch

from infrastructure.generators.csv_generator import CSVStatementGenerator


class TestCSVStatementGenerator(unittest.TestCase):
    def setUp(self):
        self.generator = CSVStatementGenerator()
        self.sample_data = {
            "account_id": "123456789",
            "start_date": "2023-01-01",
            "end_date": "2023-01-31",
            "interest": 15.75,
            "transactions": [
                {
                    "timestamp": "2023-01-02",
                    "transaction_type": "DEPOSIT",
                    "amount": 1000.00,
                    "description": "Salary"
                },
                {
                    "timestamp": "2023-01-03",
                    "transaction_type": "WITHDRAWAL",
                    "amount": 200.50,
                    "description": "ATM"
                }
            ]
        }

    def test_generate_csv_returns_string(self):
        result = self.generator.generate(self.sample_data)
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)

    def test_generate_csv_contains_correct_account_info(self):
        result = self.generator.generate(self.sample_data)
        self.assertIn("Account ID:,123456789", result)
        self.assertIn("Statement Period:,2023-01-01 to 2023-01-31", result)

    def test_generate_csv_handles_empty_transactions(self):
        empty_data = {
            "account_id": "123456789",
            "start_date": "2023-01-01",
            "end_date": "2023-01-31",
            "interest": 0.00,
            "transactions": []
        }
        result = self.generator.generate(empty_data)
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)
        self.assertIn("Date,Type,Amount,Description", result)

    def test_generate_csv_formats_amounts_correctly(self):
        result = self.generator.generate(self.sample_data)
        self.assertIn("1000.00", result)
        self.assertIn("200.50", result)
        self.assertIn("15.75", result)

    def test_generate_csv_includes_all_required_elements(self):
        result = self.generator.generate(self.sample_data)
        lines = result.split('\n')
        self.assertIn("Bank Statement", lines[0])
        self.assertIn("Date,Type,Amount,Description", result)
        self.assertIn("Interest Earned:,15.75", result)
        self.assertEqual(lines.count(''), 1)  # Check for empty lines between sections

    def test_generate_csv_with_patch(self):
        with patch('csv.writer') as mock_writer:
            self.generator.generate(self.sample_data)
            self.assertTrue(mock_writer.called)
            mock_writer.return_value.writerow.assert_any_call(["Bank Statement"])
            mock_writer.return_value.writerow.assert_any_call(["Date", "Type", "Amount", "Description"])
            mock_writer.return_value.writerow.assert_any_call(["Interest Earned:", "15.75"])


if __name__ == '__main__':
    unittest.main()