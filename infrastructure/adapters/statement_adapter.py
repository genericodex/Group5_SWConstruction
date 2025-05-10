
from abc import ABC, abstractmethod
from domain.monthly_statement import MonthlyStatement
from typing import List
import csv
from io import StringIO, BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet

# Define the statement generator interface
class IStatementGenerator(ABC):
    @abstractmethod
    def generate(self, statement: MonthlyStatement, format_type: str) -> str:
        """Generate a statement in the specified format."""
        pass

# Implement the adapter
class StatementAdapter(IStatementGenerator):
    def generate(self, statement: MonthlyStatement, format_type: str) -> str:
        if format_type.upper() == "PDF":
            return self._generate_pdf(statement)
        elif format_type.upper() == "CSV":
            return self._generate_csv(statement)
        else:
            raise ValueError(f"Unsupported format type: {format_type}")

    def _generate_pdf(self, statement: MonthlyStatement) -> bytes:
        """Generate a PDF statement using ReportLab."""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Title
        story.append(Paragraph("Monthly Bank Statement", styles['Title']))
        story.append(Spacer(1, 12))

        # Account Info
        account_info = [
            ["Account ID:", statement.account_id],
            ["Statement Period:", statement.statement_period],
            ["Start Date:", statement.start_date.strftime("%Y-%m-%d")],
            ["End Date:", statement.end_date.strftime("%Y-%m-%d")]
        ]
        story.append(Table(account_info))
        story.append(Spacer(1, 12))

        # Transactions
        transactions = [["Date", "Type", "Amount", "Description"]]
        for t in statement.transactions:
            transactions.append([
                t.timestamp.strftime("%Y-%m-%d"),
                t.transaction_type.name,
                f"${t.amount:.2f}",
                t.description or ""
            ])
        story.append(Table(transactions))
        story.append(Spacer(1, 12))

        # Summary
        summary_info = [
            ["Starting Balance:", f"${statement.starting_balance:.2f}"],
            ["Ending Balance:", f"${statement.ending_balance:.2f}"],
            ["Interest Earned:", f"${statement.interest_earned:.2f}"]
        ]
        story.append(Table(summary_info))

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    def _generate_csv(self, statement: MonthlyStatement) -> str:
        """Generate a CSV statement using the csv module."""
        output = StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow(["Monthly Bank Statement"])
        writer.writerow(["Account ID:", statement.account_id])
        writer.writerow(["Statement Period:", statement.statement_period])
        writer.writerow(["Start Date:", statement.start_date.strftime("%Y-%m-%d")])
        writer.writerow(["End Date:", statement.end_date.strftime("%Y-%m-%d")])
        writer.writerow([])

        # Transactions
        writer.writerow(["Date", "Type", "Amount", "Description"])
        for t in statement.transactions:
            writer.writerow([
                t.timestamp.strftime("%Y-%m-%d"),
                t.transaction_type.name,
                f"{t.amount:.2f}",
                t.description or ""
            ])
        writer.writerow([])

        # Summary
        writer.writerow(["Starting Balance:", f"{statement.starting_balance:.2f}"])
        writer.writerow(["Ending Balance:", f"{statement.ending_balance:.2f}"])
        writer.writerow(["Interest Earned:", f"{statement.interest_earned:.2f}"])

        return output.getvalue()