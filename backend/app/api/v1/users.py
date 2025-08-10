from fastapi import APIRouter, Depends, HTTPException, status
from app.api.deps import get_current_active_user
from app.core.database import users_collection, bookings_collection
from app.models.user import UserModel
from app.schemas.user import UserResponse, UserUpdate, ChangePassword
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: UserModel = Depends(get_current_active_user)
):
    """Get current user profile."""
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        full_name=current_user.full_name,
        phone_number=current_user.phone_number,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        role=current_user.role,
        created_at=current_user.created_at,
        total_bookings=current_user.total_bookings
    )


@router.put("/me", response_model=UserResponse)
async def update_user_profile(
    user_update: UserUpdate,
    current_user: UserModel = Depends(get_current_active_user)
):
    """Update current user profile."""
    # Prepare update data
    update_data = user_update.dict(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data to update"
        )
    
    update_data["updated_at"] = datetime.utcnow()
    
    # Update user
    await users_collection().update_one(
        {"_id": current_user.id},
        {"$set": update_data}
    )
    
    # Get updated user
    user_dict = await users_collection().find_one({"_id": current_user.id})
    updated_user = UserModel(**user_dict)
    
    return UserResponse(
        id=str(updated_user.id),
        email=updated_user.email,
        full_name=updated_user.full_name,
        phone_number=updated_user.phone_number,
        is_active=updated_user.is_active,
        is_verified=updated_user.is_verified,
        role=updated_user.role,
        created_at=updated_user.created_at,
        total_bookings=updated_user.total_bookings
    )


@router.get("/me/stats")
async def get_user_stats(
    current_user: UserModel = Depends(get_current_active_user)
):
    """Get user statistics."""
    # Get booking stats
    total_bookings = await bookings_collection().count_documents({"user_id": current_user.id})
    completed_bookings = await bookings_collection().count_documents({
        "user_id": current_user.id,
        "status": "completed"
    })
    cancelled_bookings = await bookings_collection().count_documents({
        "user_id": current_user.id,
        "status": "cancelled"
    })
    
    # Get total spent
    pipeline = [
        {"$match": {"user_id": current_user.id, "status": "completed"}},
        {"$group": {"_id": None, "total_spent": {"$sum": "$final_fare"}}}
    ]
    
    result = await bookings_collection().aggregate(pipeline).to_list(1)
    total_spent = result[0]["total_spent"] if result else 0
    
    # Get favorite routes
    pipeline = [
        {"$match": {"user_id": current_user.id}},
        {"$group": {
            "_id": {
                "from": "$pickup_location.city",
                "to": "$drop_location.city"
            },
            "count": {"$sum": 1}
        }},
        {"$sort": {"count": -1}},
        {"$limit": 5}
    ]
    
    favorite_routes = await bookings_collection().aggregate(pipeline).to_list(5)
    
    return {
        "total_bookings": total_bookings,
        "completed_bookings": completed_bookings,
        "cancelled_bookings": cancelled_bookings,
        "total_spent": total_spent,
        "favorite_routes": [
            {
                "from": route["_id"]["from"],
                "to": route["_id"]["to"],
                "trips": route["count"]
            }
            for route in favorite_routes
        ],
        "member_since": current_user.created_at
    }


@router.delete("/me")
async def delete_user_account(
    current_user: UserModel = Depends(get_current_active_user)
):
    """Delete user account (soft delete)."""
    # Soft delete - just deactivate the account
    await users_collection().update_one(
        {"_id": current_user.id},
        {
            "$set": {
                "is_active": False,
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    return {"message": "Account deactivated successfully"}


@router.post("/change-password")
async def change_password(
    password_data: ChangePassword,
    current_user: UserModel = Depends(get_current_active_user)
):
    """Change user password."""
    from app.core.security import verify_password, get_password_hash
    
    # Verify current password
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect"
        )
    
    # Check if new password is different from current
    if verify_password(password_data.new_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password"
        )
    
    # Update password
    hashed_password = get_password_hash(password_data.new_password)
    await users_collection().update_one(
        {"_id": current_user.id},
        {
            "$set": {
                "hashed_password": hashed_password,
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    logger.info(f"Password changed for user {current_user.email}")
    
    return {"message": "Password changed successfully"}
