from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import FileResponse
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel
from Group5_SWConstruction.application.services.interest_service import InterestService
from Group5_SWConstruction.application.services.limit_enforcement_service import LimitEnforcementService
from Group5_SWConstruction.application.services.statement_service import StatementService

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
    interest_service: InterestService = Depends(InterestService)
):
    try:
        # Parse calculation date if provided
        calculation_date = None
        if request.calculationDate:
            calculation_date = datetime.strptime(request.calculationDate, "%Y-%m-%d")

        # Apply interest
        interest = interest_service.apply_interest_to_account(account_id, end_date=calculation_date)

        # Fetch updated account to get balance (assuming account has a balance attribute)
        account = interest_service.account_repository.get_by_id(account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")

        return {
            "account_id": account_id,
            "interest_applied": interest,
            "updated_balance": account.balance if hasattr(account, "balance") else 0.0
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to calculate interest: {str(e)}")

# 2. Transaction Limits Endpoints
# Update Limits
@router.patch("/accounts/{account_id}/limits")
async def update_limits(
    account_id: str,
    request: UpdateLimitsRequest,
    limit_service: LimitEnforcementService = Depends(LimitEnforcementService)
):
    try:
        limit_service.update_account_limits(account_id, request.dailyLimit, request.monthlyLimit)
        return {"message": "Limits updated successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update limits: {str(e)}")

# Retrieve Limits
@router.get("/accounts/{account_id}/limits", response_model=LimitsResponse)
async def get_limits(
    account_id: str,
    limit_service: LimitEnforcementService = Depends(LimitEnforcementService)
):
    try:
        limits = limit_service.constraints_repository.get_limits(account_id)
        usage = limit_service.constraints_repository.get_usage(account_id)
        return {
            "daily_limit": limits["daily"],
            "monthly_limit": limits["monthly"],
            "daily_usage": usage["daily"],
            "monthly_usage": usage["monthly"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve limits: {str(e)}")

# 3. Monthly Statement Endpoint
@router.get("/accounts/{account_id}/statement")
async def generate_statement(
    account_id: str,
    year: int = Query(..., description="Year of the statement"),
    month: int = Query(..., description="Month of the statement (1-12)"),
    format: str = Query("pdf", description="Format of the statement (pdf or csv)"),
    statement_service: StatementService = Depends(StatementService)
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

        # Return the file as a downloadable response
        return FileResponse(
            path=file_path,
            filename=f"statement_{account_id}_{year}_{month:02d}.{format.lower()}",
            media_type="application/pdf" if format_type == "PDF" else "text/csv"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate statement: {str(e)}")
