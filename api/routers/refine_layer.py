from fastapi import APIRouter, Depends

from api.dependencies import get_refine_account_service
from application.services.refine_account_service import RefineAccountService
from domain.accounts import Account

router = APIRouter()


@router.post("/refined-accounts")
def create_refined_account(
        account_data: Account,
        refine_service: RefineAccountService = Depends(get_refine_account_service)
):
    account_id = refine_service.create_account_with_validation(account_data)
    return {"message": f"Account {account_id} created successfully"}


@router.post("/transfer-refined")
def transfer_funds(
        from_account: str,
        to_account: str,
        amount: float,
        refine_service: RefineAccountService = Depends(get_refine_account_service)
):
    transfer_id = refine_service.transfer_funds_refined(from_account, to_account, amount)
    return {"message": f"Fund transfer {transfer_id} completed successfully"}
