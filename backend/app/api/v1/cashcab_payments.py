from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from datetime import datetime

from app.models.user import UserModel
from app.api.dependencies.auth import get_current_user
from app.services.cashcab import cash_cab_service
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


class PaymentCalculationRequest(BaseModel):
    task_id: str
    quality_score: float = Field(..., ge=0, le=100)
    completion_time: int = Field(..., gt=0)


class WithdrawalRequest(BaseModel):
    amount: float = Field(..., gt=0)
    method: str = Field(..., pattern="^(upi|bank_transfer|wallet)$")
    account_details: Dict[str, str]


class PaymentMethodRequest(BaseModel):
    method_type: str  # upi, bank_account, wallet
    details: Dict[str, str]


class EarningsResponse(BaseModel):
    current_balance: float
    total_earned: float
    lifetime_withdrawn: float
    pending_withdrawals: float
    available_for_withdrawal: float
    monthly_earnings: Dict[str, float]
    recent_transactions: List[Dict[str, Any]]


@router.get("/earnings", response_model=EarningsResponse)
async def get_earnings_summary(
    current_user: UserModel = Depends(get_current_user)
):
    """Get detailed earnings summary for the user"""
    try:
        earnings = await cash_cab_service.get_user_earnings(current_user.id)
        
        # Get pending withdrawals
        pending = await cash_cab_service.get_pending_withdrawals(current_user.id)
        pending_amount = sum(w.get("amount", 0) for w in pending)
        
        # Get recent transactions
        transactions = await cash_cab_service.get_recent_transactions(
            current_user.id, 
            limit=10
        )
        
        return EarningsResponse(
            current_balance=earnings.current_balance,
            total_earned=earnings.total_earned,
            lifetime_withdrawn=earnings.lifetime_withdrawn,
            pending_withdrawals=pending_amount,
            available_for_withdrawal=earnings.current_balance - pending_amount,
            monthly_earnings=earnings.monthly_earnings,
            recent_transactions=transactions
        )
    except Exception as e:
        logger.error(f"Error fetching earnings for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch earnings summary"
        )


@router.post("/calculate-payment")
async def calculate_payment(
    request: PaymentCalculationRequest,
    current_user: UserModel = Depends(get_current_user)
):
    """Calculate payment for a completed task with bonuses"""
    try:
        # Get payment service instance
        payment_service = cash_cab_service
        
        # Calculate earnings
        calculation = await payment_service.calculate_earnings(
            task_id=request.task_id,
            user_id=current_user.id,
            quality_score=request.quality_score,
            completion_time=request.completion_time
        )
        
        return {
            "base_payout": calculation["base_payout"],
            "bonuses": calculation["bonuses"],
            "gross_amount": calculation["gross_amount"],
            "platform_fee": calculation["platform_fee"],
            "net_earnings": calculation["net_earnings"],
            "breakdown": calculation["breakdown"]
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Payment calculation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate payment"
        )


@router.post("/withdraw")
async def request_withdrawal(
    request: WithdrawalRequest,
    current_user: UserModel = Depends(get_current_user)
):
    """Request withdrawal of available balance"""
    try:
        # Validate withdrawal amount
        earnings = await cash_cab_service.get_user_earnings(current_user.id)
        
        if request.amount > earnings.current_balance:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient balance. Available: ₹{earnings.current_balance}"
            )
        
        if request.amount < 100 and request.method != "upi":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Minimum withdrawal amount is ₹100 for bank transfers"
            )
        
        # Create withdrawal request
        withdrawal_id = await cash_cab_service.request_withdrawal(
            user_id=current_user.id,
            amount=request.amount,
            method=request.method,
            account_details=request.account_details
        )
        
        return {
            "withdrawal_id": withdrawal_id,
            "amount": request.amount,
            "method": request.method,
            "status": "processing",
            "estimated_time": "2-4 hours" if request.method == "bank_transfer" else "Instant",
            "message": "Withdrawal request submitted successfully"
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Withdrawal request error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process withdrawal request"
        )


@router.get("/withdrawal-history")
async def get_withdrawal_history(
    limit: int = 20,
    offset: int = 0,
    current_user: UserModel = Depends(get_current_user)
):
    """Get withdrawal history for the user"""
    try:
        withdrawals = await cash_cab_service.get_withdrawal_history(
            user_id=current_user.id,
            limit=limit,
            offset=offset
        )
        
        return {
            "withdrawals": withdrawals,
            "total": len(withdrawals),
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error(f"Error fetching withdrawal history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch withdrawal history"
        )


@router.post("/payment-methods")
async def add_payment_method(
    request: PaymentMethodRequest,
    current_user: UserModel = Depends(get_current_user)
):
    """Add or update payment method"""
    try:
        # Validate payment method details
        if request.method_type == "bank_account":
            required = ["account_number", "ifsc_code", "account_holder_name"]
            if not all(k in request.details for k in required):
                raise ValueError("Missing required bank account details")
        elif request.method_type == "upi":
            if "upi_id" not in request.details:
                raise ValueError("UPI ID is required")
        
        # Save payment method
        method_id = await cash_cab_service.save_payment_method(
            user_id=current_user.id,
            method_type=request.method_type,
            details=request.details
        )
        
        return {
            "method_id": method_id,
            "method_type": request.method_type,
            "status": "active",
            "message": "Payment method added successfully"
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error adding payment method: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add payment method"
        )


@router.get("/payment-methods")
async def get_payment_methods(
    current_user: UserModel = Depends(get_current_user)
):
    """Get saved payment methods"""
    try:
        methods = await cash_cab_service.get_payment_methods(current_user.id)
        
        # Mask sensitive data
        for method in methods:
            if method["method_type"] == "bank_account":
                acc_num = method["details"].get("account_number", "")
                if len(acc_num) > 4:
                    method["details"]["account_number"] = f"****{acc_num[-4:]}"
            elif method["method_type"] == "upi":
                upi_id = method["details"].get("upi_id", "")
                if "@" in upi_id:
                    parts = upi_id.split("@")
                    if len(parts[0]) > 3:
                        method["details"]["upi_id"] = f"{parts[0][:3]}***@{parts[1]}"
        
        return {"payment_methods": methods}
    except Exception as e:
        logger.error(f"Error fetching payment methods: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch payment methods"
        )


@router.get("/tax-statement/{year}")
async def get_tax_statement(
    year: int,
    current_user: UserModel = Depends(get_current_user)
):
    """Generate tax statement for the specified year"""
    try:
        if year < 2024 or year > datetime.now().year:
            raise ValueError("Invalid year")
        
        statement = await cash_cab_service.generate_tax_statement(
            user_id=current_user.id,
            year=year
        )
        
        return {
            "year": year,
            "total_earnings": statement["total_earnings"],
            "platform_fees": statement["platform_fees"],
            "net_earnings": statement["net_earnings"],
            "tds_deducted": statement.get("tds", 0),
            "monthly_breakdown": statement["monthly_breakdown"],
            "generated_at": datetime.now().isoformat()
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error generating tax statement: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate tax statement"
        )
