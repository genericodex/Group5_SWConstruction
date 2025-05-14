from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import FileResponse
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel

from api.dependencies import get_interest_service, get_logging_service, get_limit_enforcement_service, \
    get_statement_service
from application.services.interest_service import InterestService
from application.services.limit_enforcement_service import LimitEnforcementService
from application.services.statement_service import StatementService
from application.services.logging_service import LoggingService

router = APIRouter()

# Request and Response Models
class InterestCalculateRequest(BaseModel):
    calculationDate: Optional[str] = None

class InterestResponse(BaseModel):
    account_id: str
    interest_applied: float
    updated_balance: float

class UpdateLimitsRequest(BaseModel):
    dailyLimit: float
    monthlyLimit: float

class LimitsResponse(BaseModel):
    daily_limit: float
    monthly_limit: float
    daily_usage: float
    monthly_usage: float

# 1. Interest Calculation Endpoint
@router.post("/accounts/{account_id}/interest/calculate", response_model=InterestResponse)
async def calculate_interest(
    account_id: str,
    request: InterestCalculateRequest,
    interest_service: InterestService = Depends(get_interest_service),
    logging_service: LoggingService = Depends(get_logging_service)
):
    try:
        # Parse calculation date if provided
        calculation_date = None
        if request.calculationDate:
            calculation_date = datetime.strptime(request.calculationDate, "%Y-%m-%d")

        # Apply interest via service
        interest = interest_service.apply_interest_to_account(account_id, end_date=calculation_date)

        # Fetch updated account details via service
        account = interest_service.account_repository.get_by_id(account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")

        # Log the interest calculation
        logging_service.info(
            f"Interest calculated for account {account_id}",
            {"account_id": account_id, "interest_applied": interest, "updated_balance": account._balance}
        )

        return {
            "account_id": account_id,
            "interest_applied": interest,
            "updated_balance": account._balance if hasattr(account, "_balance") else 0.0
        }
    except HTTPException as he:
        raise he  # Propagate HTTPException unchanged
    except ValueError as e:
        logging_service.error(f"Failed to calculate interest: {str(e)}", {"account_id": account_id})
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logging_service.error(f"Unexpected error during interest calculation: {str(e)}", {"account_id": account_id})
        raise HTTPException(status_code=500, detail=f"Failed to calculate interest: {str(e)}")

# 2. Transaction Limits Endpoints
# Update Limits
@router.patch("/accounts/{account_id}/limits")
async def update_limits(
    account_id: str,
    request: UpdateLimitsRequest,
    limit_service: LimitEnforcementService = Depends(get_limit_enforcement_service),
    logging_service: LoggingService = Depends(get_logging_service)
):
    try:
        limit_service.update_account_limits(account_id, request.dailyLimit, request.monthlyLimit)
        logging_service.info(
            f"Updated limits for account {account_id}",
            {"account_id": account_id, "daily_limit": request.dailyLimit, "monthly_limit": request.monthlyLimit}
        )
        return {"message": "Limits updated successfully"}
    except ValueError as e:
        logging_service.error(f"Failed to update limits: {str(e)}", {"account_id": account_id})
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logging_service.error(f"Unexpected error updating limits: {str(e)}", {"account_id": account_id})
        raise HTTPException(status_code=500, detail=f"Failed to update limits: {str(e)}")

# Retrieve Limits
@router.get("/accounts/{account_id}/limits", response_model=LimitsResponse)
async def get_limits(
    account_id: str,
    limit_service: LimitEnforcementService = Depends(get_limit_enforcement_service),
    logging_service: LoggingService = Depends(get_logging_service)
):
    try:
        limits = limit_service.constraints_repository.get_limits(account_id)
        usage = limit_service.constraints_repository.get_usage(account_id)
        response = {
            "daily_limit": limits["daily"],
            "monthly_limit": limits["monthly"],
            "daily_usage": usage["daily"],
            "monthly_usage": usage["monthly"]
        }
        logging_service.info(
            f"Retrieved limits for account {account_id}",
            {"account_id": account_id, "limits": response}
        )
        return response
    except Exception as e:
        logging_service.error(f"Failed to retrieve limits: {str(e)}", {"account_id": account_id})
        raise HTTPException(status_code=500, detail=f"Failed to retrieve limits: {str(e)}")

# 3. Monthly Statement Endpoint
@router.get("/accounts/{account_id}/statement")
async def generate_statement(
    account_id: str,
    year: int = Query(..., description="Year of the statement"),
    month: int = Query(..., description="Month of the statement (1-12)"),
    format: str = Query("pdf", description="Format of the statement (pdf or csv)"),
    statement_service: StatementService = Depends(get_statement_service),
    logging_service: LoggingService = Depends(get_logging_service)
):
    try:
        # Validate month
        if month < 1 or month > 12:
            raise HTTPException(status_code=400, detail="Month must be between 1 and 12")

        # Calculate start and end dates for the statement period
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(days=1)

        # Generate statement
        format_type = format.upper()
        if format_type not in ["PDF", "CSV"]:
            raise HTTPException(status_code=400, detail="Format must be 'pdf' or 'csv'")

        file_path = statement_service.generate_statement(account_id, start_date, end_date, format_type)
        logging_service.info(
            f"Generated statement for account {account_id}",
            {"account_id": account_id, "year": year, "month": month, "format": format}
        )

        # Return the file as a downloadable response
        return FileResponse(
            path=file_path,
            filename=f"statement_{account_id}_{year}_{month:02d}.{format.lower()}",
            media_type="application/pdf" if format_type == "PDF" else "text/csv"
        )
    except HTTPException as he:
        raise he  # Propagate HTTPException unchanged
    except ValueError as e:
        logging_service.error(f"Failed to generate statement: {str(e)}", {"account_id": account_id})
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logging_service.error(f"Unexpected error generating statement: {str(e)}", {"account_id": account_id})
        raise HTTPException(status_code=500, detail=f"Failed to generate statement: {str(e)}")