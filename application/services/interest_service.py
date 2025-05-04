from application.repositories.account_repository import IAccountRepository
from application.repositories.interest_repository import IInterestRepository
from domain.savings_account import SavingsAccount
from datetime import datetime, timedelta
import time
from typing import List, Optional

class InterestService:
    def __init__(self,
                 account_repository: IAccountRepository,
                 interest_repository: IInterestRepository,
                 logging_service):
        """
        Initialize InterestService.

        :param account_repository: Repository for account operations
        :param interest_repository: Repository for interest rate operations
        :param logging_service: Service for logging operations
        """
        self.account_repository = account_repository
        self.interest_repository = interest_repository
        self.logging_service = logging_service

    def apply_interest_to_account(self, account_id: str, start_date: Optional[datetime] = None,
                                  end_date: Optional[datetime] = None) -> float:
        """
        Apply interest to a single account.

        :param account_id: ID of the account to apply interest to
        :param start_date: Optional start date for interest calculation
        :param end_date: Optional end date for interest calculation
        :return: The amount of interest applied
        """
        start_time = time.time()
        params = {"account_id": account_id}
        if start_date:
            params["start_date"] = start_date.isoformat()
        if end_date:
            params["end_date"] = end_date.isoformat()

        self.logging_service.log_service_call(
            service_name="InterestService",
            method_name="apply_interest_to_account",
            status="started",
            duration_ms=0,
            params=params
        )

        try:
            account = self.account_repository.get_by_id(account_id)

            # Default period if not provided (previous month)
            if not start_date or not end_date:
                today = datetime.now()
                # First day of the previous month
                first_day_of_current_month = today.replace(day=1)
                last_day_of_previous_month = first_day_of_current_month - timedelta(days=1)
                start_date = last_day_of_previous_month.replace(day=1)
                end_date = last_day_of_previous_month

            interest = 0.0

            if account:
                if account.interest_strategy:
                    # Use the account's existing interest strategy to calculate interest
                    interest = account.calculate_period_interest(start_date, end_date)
                    # Deposit the interest
                    account.deposit(interest)
                    # Save the updated account
                    self.account_repository.save(account)

                    self.logging_service.info(
                        message="Interest applied successfully",
                        context={"account_id": account_id, "interest": interest}
                    )
                else:
                    self.logging_service.info(
                        message="Account is not eligible for interest",
                        context={"account_id": account_id, "account_type": type(account).__name__}
                    )
            else:
                self.logging_service.warning(
                    message="Account not found",
                    context={"account_id": account_id}
                )

            duration_ms = (time.time() - start_time) * 1000
            self.logging_service.log_service_call(
                service_name="InterestService",
                method_name="apply_interest_to_account",
                status="success",
                duration_ms=duration_ms,
                params=params
            )

            return interest

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

    def apply_interest_batch(self, account_ids: List[str], start_date: Optional[datetime] = None,
                             end_date: Optional[datetime] = None) -> dict:
        """
        Apply interest to multiple accounts.

        :param account_ids: List of account IDs to apply interest to
        :param start_date: Optional start date for interest calculation
        :param end_date: Optional end date for interest calculation
        :return: Dictionary with account IDs and applied interest amounts
        """
        start_time = time.time()
        params = {"account_ids": account_ids}
        if start_date:
            params["start_date"] = start_date.isoformat()
        if end_date:
            params["end_date"] = end_date.isoformat()

        self.logging_service.log_service_call(
            service_name="InterestService",
            method_name="apply_interest_batch",
            status="started",
            duration_ms=0,
            params=params
        )

        try:
            results = {}
            errors = []

            for account_id in account_ids:
                try:
                    interest = self.apply_interest_to_account(account_id, start_date, end_date)
                    results[account_id] = interest
                except Exception as e:
                    errors.append({"account_id": account_id, "error": str(e)})
                    self.logging_service.error(
                        message=f"Error applying interest to account {account_id}",
                        context={"account_id": account_id, "error": str(e)}
                    )

            duration_ms = (time.time() - start_time) * 1000
            status = "success" if not errors else "partial_success"

            log_context = {
                "total_accounts": len(account_ids),
                "successful": len(results),
                "failed": len(errors)
            }

            if errors:
                log_context["errors"] = errors

            self.logging_service.log_service_call(
                service_name="InterestService",
                method_name="apply_interest_batch",
                status=status,
                duration_ms=duration_ms,
                params=params,
                context=log_context
            )

            return results

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