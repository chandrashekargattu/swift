from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from app.core.config import settings
from app.core.database import users_collection
from app.core.security import (
    create_access_token,
    verify_password,
    get_password_hash,
    generate_reset_token
)
from app.schemas.user import (
    UserCreate,
    UserResponse,
    UserLogin,
    Token,
    PasswordReset,
    PasswordResetConfirm
)
from app.models.user import UserModel
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate):
    """Register a new user."""
    # Check if user already exists
    existing_user = await users_collection().find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    user_dict = user_data.dict()
    user_dict["password_hash"] = get_password_hash(user_dict.pop("password"))
    user_dict["role"] = "customer"
    
    # Insert user
    result = await users_collection().insert_one(user_dict)
    user_dict["_id"] = result.inserted_id
    
    user = UserModel(**user_dict)
    
    # Return user response
    return UserResponse(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        phone_number=user.phone_number,
        is_active=user.is_active,
        is_verified=user.is_verified,
        role=user.role,
        created_at=user.created_at,
        total_bookings=user.total_bookings
    )


@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin):
    """Login user and return access token."""
    # Find user
    user_dict = await users_collection().find_one({"email": user_credentials.email})
    if not user_dict:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    user = UserModel(**user_dict)
    
    # Verify password
    if not verify_password(user_credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Update last login
    await users_collection().update_one(
        {"_id": user.id},
        {"$set": {"last_login": datetime.utcnow()}}
    )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "user_id": str(user.id)},
        expires_delta=access_token_expires
    )
    
    return Token(access_token=access_token)


@router.post("/password-reset")
async def request_password_reset(reset_data: PasswordReset):
    """Request password reset token."""
    # Find user
    user_dict = await users_collection().find_one({"email": reset_data.email})
    if not user_dict:
        # Don't reveal if email exists
        return {"message": "If the email exists, a reset link has been sent"}
    
    user = UserModel(**user_dict)
    
    # Generate reset token
    reset_token = generate_reset_token()
    
    # Store reset token (in production, use Redis with expiration)
    await users_collection().update_one(
        {"_id": user.id},
        {"$set": {
            "reset_token": reset_token,
            "reset_token_created": datetime.utcnow()
        }}
    )
    
    # TODO: Send email with reset token
    logger.info(f"Password reset token for {user.email}: {reset_token}")
    
    return {"message": "If the email exists, a reset link has been sent"}


@router.post("/password-reset/confirm")
async def confirm_password_reset(reset_confirm: PasswordResetConfirm):
    """Confirm password reset with token."""
    # Find user with reset token
    user_dict = await users_collection().find_one({"reset_token": reset_confirm.token})
    if not user_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    user = UserModel(**user_dict)
    
    # Check token expiration (24 hours)
    if "reset_token_created" in user_dict:
        token_age = datetime.utcnow() - user_dict["reset_token_created"]
        if token_age.total_seconds() > 86400:  # 24 hours
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reset token has expired"
            )
    
    # Update password
    new_password_hash = get_password_hash(reset_confirm.new_password)
    await users_collection().update_one(
        {"_id": user.id},
        {
            "$set": {"password_hash": new_password_hash},
            "$unset": {"reset_token": "", "reset_token_created": ""}
        }
    )
    
    return {"message": "Password successfully reset"}
