from domain.transactions import Transaction
import logging


def setup_logging():
    logging.basicConfig(
        filename='transactions.log',
        level=logging.INFO,
        format='%(asctime)s - %(message)s'
    )


def transaction_logger(transaction: Transaction) -> None:
    """Observer that logs transaction details to a file"""
    logging.info(f"Transaction: {transaction.to_dict()}")


def email_notifier(transaction: Transaction) -> None:
    """Observer that handles email notifications for transactions"""
    # This is a placeholder for actual email sending logic
    transaction_type = transaction.get_transaction_type().name
    amount = transaction.get_amount()
    account_id = transaction.account_id

    print(f"Email notification sent for {transaction_type} of ${amount} on account {account_id}")

def sms_notifier(transaction: Transaction) -> None:
    """Observer that handles SMS notifications for transactions"""
    # This is a placeholder for actual SMS sending logic
    transaction_type = transaction.get_transaction_type().name
    amount = transaction.get_amount()

    print(f"SMS notification sent for {transaction_type} of ${amount}")
