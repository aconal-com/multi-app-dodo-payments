"""
Credit Management Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from services.database import get_db
from services.credit_service import CreditService
from middleware.auth import get_current_app_name

router = APIRouter(prefix="/credits", tags=["credits"])


# Request/Response Models
class CreditBalanceResponse(BaseModel):
    app_name: str
    user_id: str
    balance: int
    total_purchased: int
    total_used: int
    total_spent: float


class DeductCreditsRequest(BaseModel):
    app_name: str
    user_id: str
    amount: int = Field(..., gt=0)
    description: str = Field(default="Usage")


class TransactionResponse(BaseModel):
    transaction_id: str
    type: str
    amount: int
    balance_before: int
    balance_after: int
    description: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


@router.get("/{app_name}/{user_id}", response_model=CreditBalanceResponse)
async def get_user_credits(
    app_name: str,
    user_id: str,
    db: Session = Depends(get_db),
    authenticated_app: str = Depends(get_current_app_name)
):
    """Get user's credit balance"""
    if app_name != authenticated_app:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    credit_service = CreditService(db)
    user_credits = credit_service.get_or_create_user_credits(app_name, user_id)
    
    return CreditBalanceResponse(
        app_name=app_name,
        user_id=user_id,
        balance=user_credits.credit_balance,
        total_purchased=user_credits.total_credits_purchased,
        total_used=user_credits.total_credits_used,
        total_spent=float(user_credits.total_spent)
    )


@router.post("/deduct")
async def deduct_credits(
    request: DeductCreditsRequest,
    db: Session = Depends(get_db),
    authenticated_app: str = Depends(get_current_app_name)
):
    """
    Deduct credits from user account
    
    Called by app when user uses a feature that costs credits
    """
    if request.app_name != authenticated_app:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    credit_service = CreditService(db)
    
    try:
        result = credit_service.deduct_credits(
            app_name=request.app_name,
            user_id=request.user_id,
            amount=request.amount,
            description=request.description
        )
        
        return {
            "success": True,
            "transaction_id": result["transaction_id"],
            "balance_after": result["balance_after"],
            "amount_deducted": request.amount
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{app_name}/{user_id}/transactions", response_model=List[TransactionResponse])
async def get_transaction_history(
    app_name: str,
    user_id: str,
    limit: int = 20,
    db: Session = Depends(get_db),
    authenticated_app: str = Depends(get_current_app_name)
):
    """Get user's credit transaction history"""
    if app_name != authenticated_app:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    credit_service = CreditService(db)
    transactions = credit_service.get_transaction_history(app_name, user_id, limit)
    
    return [
        TransactionResponse(
            transaction_id=t.transaction_id,
            type=t.type.value,
            amount=t.amount,
            balance_before=t.balance_before,
            balance_after=t.balance_after,
            description=t.description,
            created_at=t.created_at
        )
        for t in transactions
    ]

