import unittest
from unittest.mock import patch
from datetime import datetime
from domain.monthly_statement import MonthlyStatement
from domain.transactions import Transaction, TransactionType

from io import BytesIO
import csv
import PyPDF2

from infrastructure.adapters.statement_adapter import StatementAdapter


class TestStatementAdapter(unittest.TestCase):
    def setUp(self):
        # Create a sample transaction
        self.transaction = Transaction(
            transaction_id="T123",
            timestamp=datetime(2025, 5, 1),
            transaction_type=TransactionType.DEPOSIT,
            amount=1000.50,
            source_account_id="A123",
            destination_account_id=None,
            description="Salary"
        )

        # Create a sample monthly statement
        self.statement = MonthlyStatement(
            account_id="A123",
            statement_period="May 2025",
            start_date=datetime(2025, 5, 1),
            end_date=datetime(2025, 5, 31),
            starting_balance=5000.00,
            ending_balance=6000.50,
            interest_earned=0.50,
            transactions=[self.transaction]
        )

        self.adapter = StatementAdapter()

    def test_generate_csv_contains_expected_data(self):
        # Generate CSV
        csv_output = self.adapter.generate(self.statement, "CSV")

        # Parse CSV output
        reader = csv.reader(csv_output.splitlines())
        rows = list(reader)

        # Verify header information
        self.assertEqual(rows[0], ["Monthly Bank Statement"])
        self.assertEqual(rows[1], ["Account ID:", "A123"])
        self.assertEqual(rows[2], ["Statement Period:", "May 2025"])
        self.assertEqual(rows[3], ["Start Date:", "2025-05-01"])
        self.assertEqual(rows[4], ["End Date:", "2025-05-31"])

        # Verify transaction data
        self.assertEqual(rows[6], ["Date", "Type", "Amount", "Description"])
        self.assertEqual(rows[7], ["2025-05-01", "DEPOSIT", "1000.50", "Salary"])

        # Verify summary
        self.assertEqual(rows[9], ["Starting Balance:", "5000.00"])
        self.assertEqual(rows[10], ["Ending Balance:", "6000.50"])
        self.assertEqual(rows[11], ["Interest Earned:", "0.50"])

    def test_generate_pdf_contains_expected_data(self):
        # Generate PDF
        pdf_output = self.adapter.generate(self.statement, "PDF")

        # Read PDF content
        pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_output))
        page = pdf_reader.pages[0]
        text = page.extract_text()

        # Verify key content in PDF
        self.assertIn("Monthly Bank Statement", text)
        self.assertIn("Account ID: A123", text)
        self.assertIn("Statement Period: May 2025", text)
        self.assertIn("Start Date: 2025-05-01", text)
        self.assertIn("End Date: 2025-05-31", text)
        self.assertIn("2025-05-01 DEPOSIT $1000.50 Salary", text)
        self.assertIn("Starting Balance: $5000.00", text)
        self.assertIn("Ending Balance: $6000.50", text)
        self.assertIn("Interest Earned: $0.50", text)

    def test_generate_unsupported_format_raises_valueerror(self):
        with self.assertRaises(ValueError) as context:
            self.adapter.generate(self.statement, "TXT")
        self.assertEqual(str(context.exception), "Unsupported format type: TXT")

    def test_generate_csv_empty_transactions(self):
        # Create statement with no transactions
        empty_statement = MonthlyStatement(
            account_id="A123",
            statement_period="May 2025",
            start_date=datetime(2025, 5, 1),
            end_date=datetime(2025, 5, 31),
            starting_balance=5000.00,
            ending_balance=5000.00,
            interest_earned=0.00,
            transactions=[]
        )

        csv_output = self.adapter.generate(empty_statement, "CSV")
        reader = csv.reader(csv_output.splitlines())
        rows = list(reader)

        # Verify transaction section is empty (only header)
        self.assertEqual(rows[6], ["Date", "Type", "Amount", "Description"])
        self.assertEqual(rows[7], [])  # Empty row after header
        self.assertEqual(rows[8], ["Starting Balance:", "5000.00"])

    def test_generate_pdf_empty_transactions(self):
        # Create statement with no transactions
        empty_statement = MonthlyStatement(
            account_id="A123",
            statement_period="May 2025",
            start_date=datetime(2025, 5, 1),
            end_date=datetime(2025, 5, 31),
            starting_balance=5000.00,
            ending_balance=5000.00,
            interest_earned=0.00,
            transactions=[]
        )

        pdf_output = self.adapter.generate(empty_statement, "PDF")
        pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_output))
        page = pdf_reader.pages[0]
        text = page.extract_text()

        # Verify transaction section only has header
        self.assertIn("Date Type Amount Description", text)
        self.assertIn("Starting Balance: $5000.00", text)
        self.assertNotIn("DEPOSIT", text)  # No transaction types present


if __name__ == '__main__':
    unittest.main()