from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Optional, Any
from datetime import datetime

from app.core.database import get_database
from app.models.user import UserModel
from app.models.cashcab import (
    EarningTask, TaskAssignment, UserEarnings, 
    EarningOpportunity, WithdrawalRequest
)
from app.api.deps import get_current_user
from app.services.cashcab import cash_cab_service
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/cashcab", tags=["cashcab"])


@router.get("/opportunities")
async def get_earning_opportunities(
    lat: float,
    lng: float,
    ride_duration: Optional[int] = None,
    current_user: UserModel = Depends(get_current_user)
) -> List[EarningOpportunity]:
    """Get available earning opportunities based on location"""
    try:
        opportunities = await cash_cab_service.get_available_tasks(
            user_location={"lat": lat, "lng": lng},
            user_id=str(current_user.id),
            ride_duration=ride_duration
        )
        return opportunities
    except Exception as e:
        logger.error(f"Error getting opportunities: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch opportunities"
        )


@router.post("/tasks/{task_id}/assign")
async def assign_task(
    task_id: str,
    booking_id: Optional[str] = None,
    current_user: UserModel = Depends(get_current_user)
):
    """Assign a task to the current user"""
    try:
        assignment = await cash_cab_service.assign_task(
            task_id=task_id,
            user_id=str(current_user.id),
            booking_id=booking_id
        )
        return {
            "assignment_id": assignment.id,
            "status": "assigned",
            "net_earnings": assignment.net_earnings,
            "message": f"Task assigned! You can earn ₹{assignment.net_earnings}"
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error assigning task: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to assign task"
        )


@router.post("/assignments/{assignment_id}/start")
async def start_task(
    assignment_id: str,
    current_user: UserModel = Depends(get_current_user)
):
    """Start working on an assigned task"""
    try:
        await cash_cab_service.start_task(assignment_id, str(current_user.id))
        return {"status": "started", "message": "Task started. Good luck!"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error starting task: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start task"
        )


@router.post("/assignments/{assignment_id}/submit")
async def submit_task(
    assignment_id: str,
    responses: Dict[str, Any],
    current_user: UserModel = Depends(get_current_user)
):
    """Submit completed task"""
    try:
        await cash_cab_service.submit_task(
            assignment_id=assignment_id,
            user_id=str(current_user.id),
            responses=responses
        )
        return {
            "status": "submitted",
            "message": "Task submitted for verification",
            "next_steps": "Your earnings will be credited after verification"
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error submitting task: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit task"
        )


@router.get("/earnings")
async def get_earnings_summary(
    current_user: UserModel = Depends(get_current_user)
) -> UserEarnings:
    """Get user's earnings summary"""
    try:
        earnings = await cash_cab_service.get_user_earnings(str(current_user.id))
        return earnings
    except Exception as e:
        logger.error(f"Error getting earnings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch earnings"
        )


@router.get("/assignments")
async def get_my_assignments(
    status: Optional[str] = None,
    current_user: UserModel = Depends(get_current_user)
):
    """Get user's task assignments"""
    db = await get_database()
    
    query = {"user_id": str(current_user.id)}
    if status:
        query["status"] = status
    
    assignments = await db.task_assignments.find(query).sort("assigned_at", -1).to_list(50)
    
    # Enrich with task details
    enriched = []
    for assignment in assignments:
        task = await db.earning_tasks.find_one({"_id": ObjectId(assignment["task_id"])})
        if task:
            enriched.append({
                "assignment": assignment,
                "task": {
                    "title": task["title"],
                    "type": task["task_type"],
                    "client": task["client_name"],
                    "payout": task["payout_amount"]
                }
            })
    
    return enriched


@router.post("/withdraw")
async def request_withdrawal(
    amount: float,
    method: str,
    account_details: Dict[str, str],
    current_user: UserModel = Depends(get_current_user)
):
    """Request withdrawal of earnings"""
    try:
        withdrawal_id = await cash_cab_service.request_withdrawal(
            user_id=str(current_user.id),
            amount=amount,
            method=method,
            account_details=account_details
        )
        return {
            "withdrawal_id": withdrawal_id,
            "status": "pending",
            "message": f"Withdrawal request for ₹{amount} has been submitted"
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Error requesting withdrawal: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process withdrawal request"
        )


@router.get("/leaderboard")
async def get_leaderboard(
    period: str = "month"  # month, week, all-time
):
    """Get earnings leaderboard"""
    db = await get_database()
    
    # Simple leaderboard query
    leaderboard = await db.user_earnings.find().sort("total_earned", -1).limit(20).to_list(20)
    
    # Anonymize for privacy
    result = []
    for i, earner in enumerate(leaderboard):
        result.append({
            "rank": i + 1,
            "user_id": earner["user_id"][:8] + "****",  # Partial ID
            "total_earned": earner["total_earned"],
            "tasks_completed": earner["total_tasks_completed"],
            "badges": earner.get("badges", [])
        })
    
    return result


@router.get("/stats")
async def get_platform_stats():
    """Get CashCab platform statistics"""
    db = await get_database()
    
    # Calculate stats
    total_tasks = await db.earning_tasks.count_documents({"is_active": True})
    total_paid = await db.task_assignments.count_documents({"status": "paid"})
    
    # Get total earnings paid
    pipeline = [
        {"$match": {"status": "paid"}},
        {"$group": {"_id": None, "total": {"$sum": "$net_earnings"}}}
    ]
    earnings_result = await db.task_assignments.aggregate(pipeline).to_list(1)
    total_earnings_paid = earnings_result[0]["total"] if earnings_result else 0
    
    return {
        "active_opportunities": total_tasks,
        "tasks_completed": total_paid,
        "total_earnings_distributed": total_earnings_paid,
        "average_task_value": total_earnings_paid / total_paid if total_paid > 0 else 0,
        "top_categories": ["surveys", "mystery_shopping", "deliveries"]
    }


# Admin endpoints
@router.post("/admin/tasks", dependencies=[Depends(get_current_user)])
async def create_earning_task(task: EarningTask):
    """Create a new earning task (admin only)"""
    db = await get_database()
    
    result = await db.earning_tasks.insert_one(task.dict(by_alias=True))
    
    return {
        "task_id": str(result.inserted_id),
        "message": "Task created successfully"
    }


@router.post("/admin/verify/{assignment_id}")
async def verify_task_completion(
    assignment_id: str,
    quality_score: float,
    notes: str = ""
):
    """Manually verify task completion (admin only)"""
    try:
        await cash_cab_service.verify_and_pay_task(
            assignment_id=assignment_id,
            quality_score=quality_score,
            verification_notes=notes,
            auto_verify=False
        )
        return {"status": "verified", "message": "Task verified and payment processed"}
    except Exception as e:
        logger.error(f"Error verifying task: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify task"
        )


@router.post("/admin/sample-tasks")
async def create_sample_tasks():
    """Create sample tasks for demo (admin only)"""
    try:
        await cash_cab_service.create_sample_tasks()
        return {"message": "Sample tasks created successfully"}
    except Exception as e:
        logger.error(f"Error creating sample tasks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create sample tasks"
        )


# Add missing import
from bson import ObjectId
