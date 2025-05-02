import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional
import os
import traceback


class LoggingService:
    """
    Service for logging application events and transactions with
    consistent formatting and additional context information.
    """

    def __init__(self, app_name: str = "BankingSystem", log_level: int = logging.INFO):
        self.app_name = app_name
        self.logger = self._setup_logger(log_level)

    def _setup_logger(self, log_level: int) -> logging.Logger:
        """Setup and configure the logger"""
        # Create logger
        logger = logging.getLogger(self.app_name)
        logger.setLevel(log_level)

        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)

        # Create file handler
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        file_handler = logging.FileHandler(
            f"{log_dir}/{self.app_name}_{datetime.now().strftime('%Y%m%d')}.log"
        )
        file_handler.setLevel(log_level)

        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # Add formatter to handlers
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        # Add handlers to logger
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

        return logger

    def _format_log_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Format log message with context information"""
        if context:
            try:
                context_str = json.dumps(context)
                return f"{message} | Context: {context_str}"
            except Exception:
                return message
        return message

    def info(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Log an info message"""
        self.logger.info(self._format_log_message(message, context))

    def warning(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """Log a warning message"""
        self.logger.warning(self._format_log_message(message, context))

    def error(self, message: str, context: Optional[Dict[str, Any]] = None, exc_info: bool = False) -> None:
        """Log an error message"""
        if exc_info:
            context = context or {}
            context["traceback"] = traceback.format_exc()
        self.logger.error(self._format_log_message(message, context))

    def critical(self, message: str, context: Optional[Dict[str, Any]] = None, exc_info: bool = False) -> None:
        """Log a critical message"""
        if exc_info:
            context = context or {}
            context["traceback"] = traceback.format_exc()
        self.logger.critical(self._format_log_message(message, context))

    def log_transaction(self, transaction_id: str, transaction_type: str, amount: float,
                        account_id: str, status: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Log transaction information"""
        context = {
            "transaction_id": transaction_id,
            "transaction_type": transaction_type,
            "amount": amount,
            "account_id": account_id,
            "status": status
        }

        if details:
            context.update(details)

        self.info(f"Transaction {transaction_id} ({transaction_type}) completed with status {status}", context)

    def log_service_call(self, service_name: str, method_name: str,
                         status: str, duration_ms: float,
                         params: Optional[Dict[str, Any]] = None,
                         result: Optional[Any] = None,
                         error: Optional[str] = None) -> None:
        """Log service call information"""
        context = {
            "service": service_name,
            "method": method_name,
            "status": status,
            "duration_ms": duration_ms
        }

        if params:
            # Filter out sensitive information
            filtered_params = {k: "***" if k in ["password", "token", "key"] else v
                               for k, v in params.items()}
            context["params"] = filtered_params

        if result and status == "success":
            context["result_summary"] = str(result)[:100]

        if error:
            context["error"] = error

        log_message = f"Service call {service_name}.{method_name} {status} ({duration_ms}ms)"

        if status == "success":
            self.info(log_message, context)
        else:
            self.error(log_message, context)