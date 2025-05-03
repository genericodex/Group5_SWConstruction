from application.repositories.account_repository import IAccountRepository
from domain.savings_account import SavingsAccount
from datetime import datetime
import time

class InterestService:
    def __init__(self, account_repository: IAccountRepository, logging_service):
        self.account_repository = account_repository
        self.logging_service = logging_service

    def apply_interest_to_account(self, account_id: str) -> None:
        start_time = time.time()
        params = {"account_id": account_id}
        self.logging_service.log_service_call(
            service_name="InterestService",
            method_name="apply_interest_to_account",
            status="started",
            duration_ms=0,
            params=params
        )
        try:
            account = self.account_repository.get_by_id(account_id)
            if account and isinstance(account, SavingsAccount):
                # Define the period for interest calculation (e.g., previous month)
                start_date = datetime(2025, 4, 1)  # April 1, 2025
                end_date = datetime(2025, 4, 30)   # April 30, 2025
                interest = account.calculate_period_interest(start_date, end_date)
                account.deposit(interest)
                self.account_repository.save(account)
                self.logging_service.info(
                    message="Interest applied successfully",
                    context={"account_id": account_id, "interest": interest}
                )
            duration_ms = (time.time() - start_time) * 1000
            self.logging_service.log_service_call(
                service_name="InterestService",
                method_name="apply_interest_to_account",
                status="success",
                duration_ms=duration_ms,
                params=params
            )
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.logging_service.log_service_call(
                service_name="InterestService",
                method_name="apply_interest_to_account",
                status="failed",
                duration_ms=duration_ms,
                params=params,
                error=str(e)
            )
            raise

    def apply_interest_batch(self, account_ids: list[str]) -> None:
        start_time = time.time()
        params = {"account_ids": account_ids}
        self.logging_service.log_service_call(
            service_name="InterestService",
            method_name="apply_interest_batch",
            status="started",
            duration_ms=0,
            params=params
        )
        try:
            for account_id in account_ids:
                self.apply_interest_to_account(account_id)
            duration_ms = (time.time() - start_time) * 1000
            self.logging_service.log_service_call(
                service_name="InterestService",
                method_name="apply_interest_batch",
                status="success",
                duration_ms=duration_ms,
                params=params
            )
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.logging_service.log_service_call(
                service_name="InterestService",
                method_name="apply_interest_batch",
                status="failed",
                duration_ms=duration_ms,
                params=params,
                error=str(e)
            )
            raise