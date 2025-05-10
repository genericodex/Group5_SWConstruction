import unittest
from io import BytesIO
from unittest.mock import patch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, Spacer

from infrastructure.generators.pdf_generator import PDFStatementGenerator


class TestPDFStatementGenerator(unittest.TestCase):
    def setUp(self):
        self.generator = PDFStatementGenerator()
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

    def test_generate_pdf_returns_bytes(self):
        result = self.generator.generate(self.sample_data)
        self.assertIsInstance(result, bytes)
        self.assertGreater(len(result), 0)

    def test_generate_pdf_contains_correct_account_info(self):
        with patch('infrastructure.generators.pdf_generator.SimpleDocTemplate') as mock_doc:
            try:
                self.generator.generate(self.sample_data)
                mock_doc.assert_called_once()
                args, kwargs = mock_doc.call_args
                self.assertEqual(kwargs['pagesize'], (612, 792))  # letter size
            except Exception as e:
                self.fail(f"Unexpected exception during generate: {str(e)}")

    def test_generate_pdf_handles_empty_transactions(self):
        empty_data = {
            "account_id": "123456789",
            "start_date": "2023-01-01",
            "end_date": "2023-01-31",
            "interest": 0.00,
            "transactions": []
        }
        result = self.generator.generate(empty_data)
        self.assertIsInstance(result, bytes)
        self.assertGreater(len(result), 0)

    def test_generate_pdf_formats_amounts_correctly(self):
        with patch('reportlab.platypus.SimpleDocTemplate.build') as mock_build:
            self.generator.generate(self.sample_data)
            mock_build.assert_called_once()
            story = mock_build.call_args[0][0]

            # Extract transaction table data
            transaction_table = None
            for item in story:
                if isinstance(item, Table) and item._cellvalues[0] == ["Date", "Type", "Amount", "Description"]:
                    transaction_table = item
                    break
            self.assertIsNotNone(transaction_table, "Transaction table not found")

            # Check transaction amounts
            table_data = transaction_table._cellvalues
            amounts = [row[2] for row in table_data[1:]]  # Skip header row
            self.assertIn("$1000.00", amounts)
            self.assertIn("$200.50", amounts)

            # Check summary table for interest
            summary_table = None
            for item in story:
                if isinstance(item, Table) and item._cellvalues[0][0] == "Interest Earned:":
                    summary_table = item
                    break
            self.assertIsNotNone(summary_table, "Summary table not found")
            self.assertEqual(summary_table._cellvalues[0][1], "$15.75")

    def test_generate_pdf_includes_all_required_elements(self):
        with patch('reportlab.platypus.SimpleDocTemplate.build') as mock_build:
            self.generator.generate(self.sample_data)
            mock_build.assert_called_once()
            story = mock_build.call_args[0][0]

            # Check for presence of key elements
            element_types = [type(item).__name__ for item in story]
            self.assertIn('Paragraph', element_types)  # Title and Summary
            self.assertIn('Table', element_types)  # Account info, transactions, summary
            self.assertIn('Spacer', element_types)  # Spacing between sections


if __name__ == '__main__':
    unittest.main()