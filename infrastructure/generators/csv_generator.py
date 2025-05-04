# infrastructure/generators/csv_statement_generator.py
import csv
from io import StringIO
from typing import Dict

from application.repositories.statement_generator import IStatementGenerator


class CSVStatementGenerator(IStatementGenerator):
    def generate_csv(self, statement_data: Dict) -> str:
        output = StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow(["Bank Statement"])
        writer.writerow([])

        # Account Information
        writer.writerow(["Account ID:", statement_data["account_id"]])
        writer.writerow(["Statement Period:",
                         f"{statement_data['start_date']} to {statement_data['end_date']}"])
        writer.writerow([])

        # Transactions Header
        writer.writerow(["Date", "Type", "Amount", "Description"])

        # Transactions
        for t in statement_data["transactions"]:
            writer.writerow([
                t["timestamp"],
                t["transaction_type"],
                f"{t['amount']:.2f}",
                t.get("description", "")
            ])

        writer.writerow([])

        # Summary
        writer.writerow(["Interest Earned:", f"{statement_data['interest']:.2f}"])

        return output.getvalue()