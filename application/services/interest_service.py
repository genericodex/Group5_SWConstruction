from application.repositories.account_repository import IAccountRepository
from domain.interest_repository import IInterestRepository

from domain.savings_account import SavingsAccount
from domain.interest import DynamicInterestStrategy
from datetime import datetime
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

            # Default period if not provided
            if not start_date or not end_date:
                # Define the period for interest calculation (e.g., previous month)
                start_date = datetime(2025, 4, 1)  # April 1, 2025
                end_date = datetime(2025, 4, 30)  # April 30, 2025

            interest = 0.0

            if account:
                if isinstance(account, SavingsAccount):
                    # Get dynamic interest strategy with current rates
                    account_type = account.get_account_type()
                    # Create dynamic strategy with current rates from repository
                    strategy = DynamicInterestStrategy(self.interest_repository, account_type)
                    # Use the strategy to calculate interest
                    interest = strategy.calculate_interest(account.get_balance(), start_date, end_date)
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