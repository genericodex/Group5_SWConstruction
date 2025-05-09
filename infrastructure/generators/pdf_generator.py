from io import BytesIO
from typing import Dict

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

from infrastructure.adapters.statement_adapter import IStatementGenerator


class PDFStatementGenerator(IStatementGenerator):
    def generate(self, statement_data: Dict) -> bytes:
        return self.generate_pdf(statement_data)

    def generate_pdf(self, statement_data: Dict) -> bytes:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Title
        story.append(Paragraph("Bank Statement", styles['Title']))
        story.append(Spacer(1, 12))

        # Account Information
        account_info = [
            ["Account ID:", statement_data["account_id"]],
            ["Statement Period:", f"{statement_data['start_date']} to {statement_data['end_date']}"]
        ]
        account_table = Table(account_info, colWidths=[150, 300])
        account_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(account_table)
        story.append(Spacer(1, 12))

        # Transactions
        transactions = [["Date", "Type", "Amount", "Description"]]
        # Sort transactions by timestamp in ascending order
        sorted_transactions = sorted(statement_data["transactions"], key=lambda t: t["timestamp"])
        for t in sorted_transactions:
            transactions.append([
                t["timestamp"],
                t["transaction_type"],
                f"${t['amount']:.2f}",
                t.get("description", "")
            ])

        trans_table = Table(transactions, colWidths=[100, 80, 80, 240])
        trans_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ]))
        story.append(trans_table)
        story.append(Spacer(1, 12))

        # Summary
        story.append(Paragraph("Summary", styles['Heading2']))
        story.append(Spacer(1, 6))

        summary_info = [
            ["Interest Earned:", f"${statement_data['interest']:.2f}"]
        ]
        summary_table = Table(summary_info, colWidths=[150, 300])
        summary_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
        ]))
        story.append(summary_table)

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()