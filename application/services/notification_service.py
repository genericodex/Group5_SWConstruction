from typing import List, Callable, Dict, Optional
from domain.transactions import Transaction
from domain.accounts import Account
from domain.observers import transaction_logger, setup_logging
from infrastructure.Notifications.notification_adapters import EmailNotificationAdapter, SMSNotificationAdapter


class NotificationService:
    """
    Application service responsible for handling transaction notifications
    and dispatching events (SMS, email) when transactions are completed.
    """

    def __init__(self, email_adapter: Optional[EmailNotificationAdapter] = None,
                 sms_adapter: Optional[SMSNotificationAdapter] = None):
        # Set up logging for transactions
        setup_logging()
        self.email_adapter = email_adapter
        self.sms_adapter = sms_adapter

        # Templates for different transaction types
        self.email_templates = {
            "DEPOSIT": {
                "subject": "Deposit Notification",
                "content": "Dear customer, a deposit of ${amount} has been made to your account {account_id}."
            },
            "WITHDRAW": {
                "subject": "Withdrawal Notification",
                "content": "Dear customer, a withdrawal of ${amount} has been made from your account {account_id}."
            },
            "TRANSFER": {
                "subject": "Transfer Notification",
                "content": "Dear customer, a transfer of ${amount} has been made from your account {source_account_id} to account {destination_account_id}."
            }
        }

        self.sms_templates = {
            "DEPOSIT": {
                "subject": "Deposit Alert",
                "content": "Deposit of ${amount} to account {account_id} completed."
            },
            "WITHDRAW": {
                "subject": "Withdrawal Alert",
                "content": "Withdrawal of ${amount} from account {account_id} completed."
            },
            "TRANSFER": {
                "subject": "Transfer Alert",
                "content": "Transfer of ${amount} from account {source_account_id} to {destination_account_id} completed."
            }
        }

        # Define notification strategies using the adapters
        self._notification_strategies: Dict[str, List[Callable]] = {
            "default": [transaction_logger],
            "premium": [transaction_logger, self._email_notifier, self._sms_notifier],
            "standard": [transaction_logger, self._email_notifier]
        }

    def _email_notifier(self, transaction: Transaction) -> None:
        """Internal email notifier using the adapter"""
        if not self.email_adapter or not hasattr(transaction, 'account'):
            return

        recipient_email = transaction.account.email  # Assuming Account has an email attribute
        transaction_type = transaction.transaction_type.name
        template = self.email_templates.get(transaction_type)

        if not template:
            return

        subject = template["subject"]
        content = template["content"].format(
            amount=transaction.amount,
            account_id=transaction.account_id,
            source_account_id=transaction.source_account_id,
            destination_account_id=transaction.destination_account_id
        )

        self.email_adapter.send(recipient_email, subject, content)

    def _sms_notifier(self, transaction: Transaction) -> None:
        """Internal SMS notifier using the adapter"""
        if not self.sms_adapter or not hasattr(transaction, 'account'):
            return

        recipient_phone = transaction.account.phone  # Assuming Account has a phone attribute
        transaction_type = transaction.transaction_type.name
        template = self.sms_templates.get(transaction_type)

        if not template:
            return

        subject = template["subject"]
        content = template["content"].format(
            amount=transaction.amount,
            account_id=transaction.account_id,
            source_account_id=transaction.source_account_id,
            destination_account_id=transaction.destination_account_id
        )

        self.sms_adapter.send(recipient_phone, subject, content)

    def register_account_observers(self, account: Account, account_tier: str = "default") -> None:
        """
        Register the appropriate notification observers based on account tier.
        """
        strategies = self._notification_strategies.get(account_tier.lower(),
                                                       self._notification_strategies["default"])
        for observer in strategies:
            account.add_observer(observer)

    def notify_transaction(self, transaction: Transaction) -> None:
        """
        Manually trigger notifications for a transaction.
        """
        for observer in self._notification_strategies["default"]:
            observer(transaction)

    def add_custom_notification_strategy(self, tier: str, strategy: Callable) -> None:
        """
        Add a custom notification strategy to a specific account tier.
        """
        if tier not in self._notification_strategies:
            self._notification_strategies[tier] = [transaction_logger]
        self._notification_strategies[tier].append(strategy)