from application.repositories.transaction_repository import ITransactionRepository
import time

class LimitEnforcementService:
    def __init__(self, transaction_repository: ITransactionRepository, logging_service):
        self.transaction_repository = transaction_repository
        self.logging_service = logging_service

    def check_limit(self, account_id: str, transaction_amount: float) -> bool:
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
            # Example limits (these could be fetched from domain or config)
            daily_limit = 10000.0
            monthly_limit = 50000.0
            usage = self.transaction_repository.get_usage(account_id)  # Assume this returns dict with daily/monthly totals
            if usage["daily"] + transaction_amount > daily_limit or usage["monthly"] + transaction_amount > monthly_limit:
                raise ValueError("Transaction exceeds daily or monthly limit")
            duration_ms = (time.time() - start_time) * 1000
            self.logging_service.log_service_call(
                service_name="LimitEnforcementService",
                method_name="check_limit",
                status="success",
                duration_ms=duration_ms,
                params=params
            )
            return True
        except Exception as e:
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
            self.transaction_repository.reset_usage(account_id, "daily")  # Assume this method exists
            duration_ms = (time.time() - start_time) * 1000
            self.logging_service.log_service_call(
                service_name="LimitEnforcementService",
                method_name="reset_limits_daily",
                status="success",
                duration_ms=duration_ms,
                params=params
            )
        except Exception as e:
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
            self.transaction_repository.reset_usage(account_id, "monthly")  # Assume this method exists
            duration_ms = (time.time() - start_time) * 1000
            self.logging_service.log_service_call(
                service_name="LimitEnforcementService",
                method_name="reset_limits_monthly",
                status="success",
                duration_ms=duration_ms,
                params=params
            )
        except Exception as e:
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