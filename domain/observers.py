from domain.transactions import Transaction
import logging

def setup_logging():
    logging.basicConfig(
        filename='transactions.log',
        level=logging.INFO,
        format='%(asctime)s - %(message)s'
    )

def transaction_logger(transaction: Transaction) -> None:
    logging.info(f"Transaction: {transaction.to_dict()}")

def email_notifier(transaction: Transaction) -> None:
    # Placeholder for email notification logic
    print(f"Email notification sent for transaction: {transaction.transaction_id}")

def sms_notifier(transaction: Transaction) -> None:
    # Placeholder for SMS notification logic
    print(f"SMS notification sent for transaction: {transaction.transaction_id}")
