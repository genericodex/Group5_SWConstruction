# application/services/limit_enforcement_service.py
import time
from typing import Dict, Any, Optional
from application.repositories.accountConstraint_repository import IAccountConstraintsRepository


class LimitEnforcementService:
    """Service responsible for enforcing daily and monthly transaction limits.

    This service can be:
    1. Tied into deposit/withdraw flows
    2. A separate "interceptor" that checks usage before allowing transactions to proceed
    """

    def __init__(self, constraints_repository: IAccountConstraintsRepository, logging_service):
        """Initialize the LimitEnforcementService.

        Args:
            constraints_repository: Repository for managing account constraints
            logging_service: Service for logging operations and performance metrics
        """
        self.constraints_repository = constraints_repository
        self.logging_service = logging_service

    def check_limit(self, account_id: str, transaction_amount: float) -> bool:
        """Check if a transaction exceeds daily or monthly limits and update usage.

        Args:
            account_id: The account identifier
            transaction_amount: Amount of the transaction to check

        Returns:
            bool: True if transaction is within limits

        Raises:
            ValueError: If transaction exceeds daily or monthly limit
        """
        start_time = time.time()
        params = {"account_id": account_id, "transaction_amount": transaction_amount}

        self.logging_service.log_service_call(
            service_name="LimitEnforcementService",
            method_name="check_limit",
            status="started",
            duration_ms=0,
            params=params
        )

        try:
            # Get limits and usage for the account
            limits = self.constraints_repository.get_limits(account_id)
            daily_limit = limits["daily"]
            monthly_limit = limits["monthly"]

            usage = self.constraints_repository.get_usage(account_id)
            daily_usage = usage["daily"]
            monthly_usage = usage["monthly"]

            # Check if transaction would exceed limits
            if daily_usage + transaction_amount > daily_limit:
                error_message = f"Transaction exceeds daily limit: {daily_usage + transaction_amount} > {daily_limit}"
                raise ValueError(error_message)

            if monthly_usage + transaction_amount > monthly_limit:
                error_message = f"Transaction exceeds monthly limit: {monthly_usage + transaction_amount} > {monthly_limit}"
                raise ValueError(error_message)

            # Update usage after successful limit check
            self.constraints_repository.update_usage(account_id, transaction_amount, "daily")
            self.constraints_repository.update_usage(account_id, transaction_amount, "monthly")

            # Calculate remaining limits for logging context
            remaining_daily = daily_limit - (daily_usage + transaction_amount)
            remaining_monthly = monthly_limit - (monthly_usage + transaction_amount)

            # Log success with context
            duration_ms = (time.time() - start_time) * 1000
            self.logging_service.log_service_call(
                service_name="LimitEnforcementService",
                method_name="check_limit",
                status="success",
                duration_ms=duration_ms,
                params=params,
                result={
                    "transaction_allowed": True,
                    "remaining_daily_limit": remaining_daily,
                    "remaining_monthly_limit": remaining_monthly
                }
            )

            return True

        except Exception as e:
            # Log failure
            duration_ms = (time.time() - start_time) * 1000
            self.logging_service.log_service_call(
                service_name="LimitEnforcementService",
                method_name="check_limit",
                status="failed",
                duration_ms=duration_ms,
                params=params,
                error=str(e)
            )
            raise

    def reset_limits_daily(self, account_id: str) -> None:
        """Reset daily usage for an account.

        Typically used in scheduled jobs that run daily at midnight.

        Args:
            account_id: The account identifier

        Raises:
            Exception: If reset operation fails
        """
        start_time = time.time()
        params = {"account_id": account_id}

        self.logging_service.log_service_call(
            service_name="LimitEnforcementService",
            method_name="reset_limits_daily",
            status="started",
            duration_ms=0,
            params=params
        )

        try:
            # Reset daily usage
            self.constraints_repository.reset_usage(account_id, "daily")

            # Log success
            duration_ms = (time.time() - start_time) * 1000
            self.logging_service.log_service_call(
                service_name="LimitEnforcementService",
                method_name="reset_limits_daily",
                status="success",
                duration_ms=duration_ms,
                params=params,
                result={"daily_usage_reset": True}
            )

        except Exception as e:
            # Log failure
            duration_ms = (time.time() - start_time) * 1000
            self.logging_service.log_service_call(
                service_name="LimitEnforcementService",
                method_name="reset_limits_daily",
                status="failed",
                duration_ms=duration_ms,
                params=params,
                error=str(e)
            )
            raise

    def reset_limits_monthly(self, account_id: str) -> None:
        """Reset monthly usage for an account.

        Typically used in scheduled jobs that run on the first day of each month.

        Args:
            account_id: The account identifier

        Raises:
            Exception: If reset operation fails
        """
        start_time = time.time()
        params = {"account_id": account_id}

        self.logging_service.log_service_call(
            service_name="LimitEnforcementService",
            method_name="reset_limits_monthly",
            status="started",
            duration_ms=0,
            params=params
        )

        try:
            # Reset monthly usage
            self.constraints_repository.reset_usage(account_id, "monthly")

            # Log success
            duration_ms = (time.time() - start_time) * 1000
            self.logging_service.log_service_call(
                service_name="LimitEnforcementService",
                method_name="reset_limits_monthly",
                status="success",
                duration_ms=duration_ms,
                params=params,
                result={"monthly_usage_reset": True}
            )

        except Exception as e:
            # Log failure
            duration_ms = (time.time() - start_time) * 1000
            self.logging_service.log_service_call(
                service_name="LimitEnforcementService",
                method_name="reset_limits_monthly",
                status="failed",
                duration_ms=duration_ms,
                params=params,
                error=str(e)
            )
            raise

    def update_account_limits(self, account_id: str, daily_limit: float, monthly_limit: float) -> None:
        """Update the daily and monthly limits for an account.

        Args:
            account_id: The account identifier
            daily_limit: New daily limit value
            monthly_limit: New monthly limit value

        Raises:
            ValueError: If constraints not found or values are invalid
            Exception: If update operation fails
        """
        start_time = time.time()
        params = {
            "account_id": account_id,
            "daily_limit": daily_limit,
            "monthly_limit": monthly_limit
        }

        self.logging_service.log_service_call(
            service_name="LimitEnforcementService",
            method_name="update_account_limits",
            status="started",
            duration_ms=0,
            params=params
        )

        try:
            # Validate limit values
            if daily_limit <= 0 or monthly_limit <= 0:
                raise ValueError("Limits must be positive values")

            if daily_limit > monthly_limit:
                raise ValueError("Daily limit cannot exceed monthly limit")

            # Update limits in repository
            self.constraints_repository.update_limits(account_id, daily_limit, monthly_limit)

            # Log success
            duration_ms = (time.time() - start_time) * 1000
            self.logging_service.log_service_call(
                service_name="LimitEnforcementService",
                method_name="update_account_limits",
                status="success",
                duration_ms=duration_ms,
                params=params,
                result={
                    "limits_updated": True,
                    "new_daily_limit": daily_limit,
                    "new_monthly_limit": monthly_limit
                }
            )

        except Exception as e:
            # Log failure
            duration_ms = (time.time() - start_time) * 1000
            self.logging_service.log_service_call(
                service_name="LimitEnforcementService",
                method_name="update_account_limits",
                status="failed",
                duration_ms=duration_ms,
                params=params,
                error=str(e)
            )
            raise