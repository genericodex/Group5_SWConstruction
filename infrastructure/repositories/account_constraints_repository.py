from typing import Dict
from sqlalchemy.orm import Session
from infrastructure.database.models import AccountConstraintsModel
from application.repositories.accountConstraint_repository import IAccountConstraintsRepository


class AccountConstraintsRepository(IAccountConstraintsRepository):
    """Implementation of IAccountConstraintsRepository using SQLAlchemy ORM"""

    def __init__(self, db: Session, logging_service):
        """Initialize the repository

        Args:
            db: SQLAlchemy database session
            logging_service: Service for logging operations
        """
        self.db = db
        self.logging_service = logging_service

    def create_constraints(self, account_id: str) -> None:
        """Create default constraints for a new account

        Args:
            account_id: The account identifier
        """
        self.logging_service.info(
            f"Creating default constraints for account {account_id}",
            {"account_id": account_id}
        )

        constraints = AccountConstraintsModel(
            account_id=account_id,
            daily_usage=0.0,
            monthly_usage=0.0,
            daily_limit=10000.0,
            monthly_limit=50000.0
        )

        self.db.add(constraints)
        self.db.commit()

        self.logging_service.info(
            f"Default constraints created for account {account_id}",
            {"account_id": account_id}
        )

    def get_usage(self, account_id: str) -> Dict[str, float]:
        """Get current daily and monthly usage for an account

        Args:
            account_id: The account identifier

        Returns:
            Dict with daily and monthly usage values
        """
        self.logging_service.info(
            f"Getting usage for account {account_id}",
            {"account_id": account_id}
        )

        constraints = self._get_or_create_constraints(account_id)
        result = {"daily": constraints.daily_usage, "monthly": constraints.monthly_usage}

        self.logging_service.info(
            f"Retrieved usage for account {account_id}",
            {"account_id": account_id, "usage": result}
        )

        return result

    def reset_usage(self, account_id: str, period: str) -> None:
        """Reset usage for a specific period

        Args:
            account_id: The account identifier
            period: Either "daily" or "monthly"

        Raises:
            ValueError: If period is invalid or constraints not found
        """
        self.logging_service.info(
            f"Resetting {period} usage for account {account_id}",
            {"account_id": account_id, "period": period}
        )

        constraints = self.db.query(AccountConstraintsModel).filter(
            AccountConstraintsModel.account_id == account_id
        ).first()

        if not constraints:
            error_msg = f"No constraints found for account ID {account_id}"
            self.logging_service.error(error_msg, {"account_id": account_id})
            raise ValueError(error_msg)

        if period == "daily":
            constraints.daily_usage = 0.0
        elif period == "monthly":
            constraints.monthly_usage = 0.0
        else:
            error_msg = "Invalid period. Use 'daily' or 'monthly'"
            self.logging_service.error(
                error_msg,
                {"account_id": account_id, "period": period}
            )
            raise ValueError(error_msg)

        self.db.commit()

        self.logging_service.info(
            f"Successfully reset {period} usage for account {account_id}",
            {"account_id": account_id, "period": period}
        )

    def update_usage(self, account_id: str, amount: float, period: str) -> None:
        """Update usage for a specific period

        Args:
            account_id: The account identifier
            amount: Amount to add to current usage
            period: Either "daily" or "monthly"

        Raises:
            ValueError: If period is invalid, constraints not found, or limit exceeded
        """
        self.logging_service.info(
            f"Updating {period} usage for account {account_id}",
            {"account_id": account_id, "amount": amount, "period": period}
        )

        constraints = self.db.query(AccountConstraintsModel).filter(
            AccountConstraintsModel.account_id == account_id
        ).first()

        if not constraints:
            error_msg = f"No constraints found for account ID {account_id}"
            self.logging_service.error(error_msg, {"account_id": account_id})
            raise ValueError(error_msg)

        if period == "daily":
            new_usage = constraints.daily_usage + amount
            constraints.daily_usage = new_usage

            if new_usage > constraints.daily_limit:
                error_msg = f"Daily limit exceeded: {new_usage} > {constraints.daily_limit}"
                self.logging_service.warning(
                    error_msg,
                    {
                        "account_id": account_id,
                        "daily_usage": new_usage,
                        "daily_limit": constraints.daily_limit
                    }
                )
                self.db.rollback()  # Rollback the transaction
                raise ValueError(error_msg)

        elif period == "monthly":
            new_usage = constraints.monthly_usage + amount
            constraints.monthly_usage = new_usage

            if new_usage > constraints.monthly_limit:
                error_msg = f"Monthly limit exceeded: {new_usage} > {constraints.monthly_limit}"
                self.logging_service.warning(
                    error_msg,
                    {
                        "account_id": account_id,
                        "monthly_usage": new_usage,
                        "monthly_limit": constraints.monthly_limit
                    }
                )
                self.db.rollback()  # Rollback the transaction
                raise ValueError(error_msg)

        else:
            error_msg = "Invalid period. Use 'daily' or 'monthly'"
            self.logging_service.error(
                error_msg,
                {"account_id": account_id, "period": period}
            )
            raise ValueError(error_msg)

        self.db.commit()

        self.logging_service.info(
            f"Successfully updated {period} usage for account {account_id}",
            {
                "account_id": account_id,
                "period": period,
                "new_usage": new_usage,
                f"{period}_limit": constraints.daily_limit if period == "daily" else constraints.monthly_limit,
                "remaining": (constraints.daily_limit - new_usage) if period == "daily" else (
                            constraints.monthly_limit - new_usage)
            }
        )

    def get_limits(self, account_id: str) -> Dict[str, float]:
        """Get account limits

        Args:
            account_id: The account identifier

        Returns:
            Dict with daily and monthly limits
        """
        self.logging_service.info(
            f"Getting limits for account {account_id}",
            {"account_id": account_id}
        )

        constraints = self._get_or_create_constraints(account_id)
        result = {"daily": constraints.daily_limit, "monthly": constraints.monthly_limit}

        self.logging_service.info(
            f"Retrieved limits for account {account_id}",
            {"account_id": account_id, "limits": result}
        )

        return result

    def update_limits(self, account_id: str, daily_limit: float, monthly_limit: float) -> None:
        """Update account limits

        Args:
            account_id: The account identifier
            daily_limit: New daily limit
            monthly_limit: New monthly limit

        Raises:
            ValueError: If constraints not found
        """
        self.logging_service.info(
            f"Updating limits for account {account_id}",
            {
                "account_id": account_id,
                "daily_limit": daily_limit,
                "monthly_limit": monthly_limit
            }
        )

        constraints = self.db.query(AccountConstraintsModel).filter(
            AccountConstraintsModel.account_id == account_id
        ).first()

        if not constraints:
            error_msg = f"No constraints found for account ID {account_id}"
            self.logging_service.error(error_msg, {"account_id": account_id})
            raise ValueError(error_msg)

        # Store old values for logging
        old_daily_limit = constraints.daily_limit
        old_monthly_limit = constraints.monthly_limit

        # Update values
        constraints.daily_limit = daily_limit
        constraints.monthly_limit = monthly_limit

        self.db.commit()

        self.logging_service.info(
            f"Successfully updated limits for account {account_id}",
            {
                "account_id": account_id,
                "old_daily_limit": old_daily_limit,
                "new_daily_limit": daily_limit,
                "old_monthly_limit": old_monthly_limit,
                "new_monthly_limit": monthly_limit
            }
        )

    def _get_or_create_constraints(self, account_id: str) -> AccountConstraintsModel:
        """Helper method to get constraints or create if not exists

        Args:
            account_id: The account identifier

        Returns:
            AccountConstraintsModel instance
        """
        constraints = self.db.query(AccountConstraintsModel).filter(
            AccountConstraintsModel.account_id == account_id
        ).first()

        if not constraints:
            self.create_constraints(account_id)
            constraints = self.db.query(AccountConstraintsModel).filter(
                AccountConstraintsModel.account_id == account_id
            ).first()

        return constraints