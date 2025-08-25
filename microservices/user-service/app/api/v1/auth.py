"""
Authentication API endpoints
"""
import logging
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.core.config import settings
from app.core.database import get_db_session
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token
)
from app.models.user import User, RefreshToken, PasswordResetToken, EmailVerificationToken
from app.schemas.auth import (
    Token,
    TokenData,
    UserRegister,
    UserLogin,
    PasswordReset,
    PasswordResetRequest,
    EmailVerification
)
from app.schemas.user import UserResponse
from app.services.email import EmailService
from app.core.events import EventPublisher, UserEvent

logger = logging.getLogger(__name__)
router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")
email_service = EmailService()

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db_session)
) -> User:
    """
    Get current authenticated user
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = decode_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception
    
    # Get user from database
    result = await db.execute(
        select(User).where(User.id == user_id, User.is_active == True)
    )
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    return user

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Register a new user
    """
    # Check if user already exists
    result = await db.execute(
        select(User).where(
            (User.email == user_data.email) |
            (User.username == user_data.username) if user_data.username else False
        )
    )
    
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or username already exists"
        )
    
    # Create new user
    user = User(
        email=user_data.email,
        username=user_data.username,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        password_hash=get_password_hash(user_data.password),
        phone=user_data.phone
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    # Send verification email
    verification_token = await create_email_verification_token(user, db)
    await email_service.send_verification_email(user.email, verification_token)
    
    # Publish user created event
    await EventPublisher.publish_user_event(
        UserEvent(
            event_type="USER_CREATED",
            user_id=str(user.id),
            data=user.to_dict()
        )
    )
    
    logger.info(f"New user registered: {user.email}")
    return UserResponse.from_orm(user)

@router.post("/token", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Login with username/email and password
    """
    # Find user by email or username
    result = await db.execute(
        select(User).where(
            (User.email == form_data.username) |
            (User.username == form_data.username)
        )
    )
    user = result.scalar_one_or_none()
    
    # Verify user and password
    if not user or not verify_password(form_data.password, user.password_hash):
        # Increment failed login attempts
        if user:
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= 5:
                user.locked_until = datetime.utcnow() + timedelta(minutes=15)
            await db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    # Check if account is locked
    if user.locked_until and user.locked_until > datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="Account temporarily locked due to multiple failed login attempts"
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )
    
    # Reset failed login attempts
    user.failed_login_attempts = 0
    user.locked_until = None
    user.last_login_at = datetime.utcnow()
    
    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token_str = create_refresh_token()
    
    # Save refresh token
    refresh_token = RefreshToken(
        user_id=user.id,
        token=refresh_token_str,
        expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    db.add(refresh_token)
    await db.commit()
    
    # Publish login event
    await EventPublisher.publish_user_event(
        UserEvent(
            event_type="USER_LOGIN",
            user_id=str(user.id),
            data={"timestamp": datetime.utcnow().isoformat()}
        )
    )
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token_str,
        token_type="bearer"
    )

@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Refresh access token using refresh token
    """
    # Find refresh token
    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token == refresh_token)
    )
    token_obj = result.scalar_one_or_none()
    
    if not token_obj or not token_obj.is_valid():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    # Get user
    result = await db.execute(
        select(User).where(User.id == token_obj.user_id, User.is_active == True)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Revoke old refresh token
    token_obj.revoked_at = datetime.utcnow()
    
    # Create new tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    new_refresh_token_str = create_refresh_token()
    
    # Save new refresh token
    new_refresh_token = RefreshToken(
        user_id=user.id,
        token=new_refresh_token_str,
        expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    db.add(new_refresh_token)
    await db.commit()
    
    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token_str,
        token_type="bearer"
    )

@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Logout current user (revoke all refresh tokens)
    """
    # Revoke all user's refresh tokens
    await db.execute(
        update(RefreshToken)
        .where(RefreshToken.user_id == current_user.id, RefreshToken.revoked_at == None)
        .values(revoked_at=datetime.utcnow())
    )
    await db.commit()
    
    # Publish logout event
    await EventPublisher.publish_user_event(
        UserEvent(
            event_type="USER_LOGOUT",
            user_id=str(current_user.id),
            data={"timestamp": datetime.utcnow().isoformat()}
        )
    )
    
    return {"message": "Successfully logged out"}

@router.post("/password-reset-request")
async def request_password_reset(
    request: PasswordResetRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Request password reset token
    """
    # Find user by email
    result = await db.execute(
        select(User).where(User.email == request.email)
    )
    user = result.scalar_one_or_none()
    
    if user:
        # Create reset token
        reset_token = PasswordResetToken(
            user_id=user.id,
            token=create_refresh_token(),  # Reuse token generation
            expires_at=datetime.utcnow() + timedelta(hours=1)
        )
        db.add(reset_token)
        await db.commit()
        
        # Send reset email
        await email_service.send_password_reset_email(user.email, reset_token.token)
        
        logger.info(f"Password reset requested for: {user.email}")
    
    # Always return success to prevent email enumeration
    return {"message": "If the email exists, a password reset link has been sent"}

@router.post("/password-reset")
async def reset_password(
    reset_data: PasswordReset,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Reset password using token
    """
    # Find reset token
    result = await db.execute(
        select(PasswordResetToken).where(PasswordResetToken.token == reset_data.token)
    )
    token_obj = result.scalar_one_or_none()
    
    if not token_obj or not token_obj.is_valid():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Get user
    result = await db.execute(
        select(User).where(User.id == token_obj.user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update password
    user.password_hash = get_password_hash(reset_data.new_password)
    token_obj.used_at = datetime.utcnow()
    
    # Revoke all refresh tokens for security
    await db.execute(
        update(RefreshToken)
        .where(RefreshToken.user_id == user.id)
        .values(revoked_at=datetime.utcnow())
    )
    
    await db.commit()
    
    # Publish password changed event
    await EventPublisher.publish_user_event(
        UserEvent(
            event_type="PASSWORD_CHANGED",
            user_id=str(user.id),
            data={"timestamp": datetime.utcnow().isoformat()}
        )
    )
    
    return {"message": "Password reset successfully"}

@router.post("/verify-email")
async def verify_email(
    verification: EmailVerification,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Verify email address
    """
    # Find verification token
    result = await db.execute(
        select(EmailVerificationToken).where(EmailVerificationToken.token == verification.token)
    )
    token_obj = result.scalar_one_or_none()
    
    if not token_obj or not token_obj.is_valid():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )
    
    # Update user
    result = await db.execute(
        select(User).where(User.id == token_obj.user_id)
    )
    user = result.scalar_one_or_none()
    
    if user:
        user.is_email_verified = True
        token_obj.verified_at = datetime.utcnow()
        await db.commit()
        
        # Publish email verified event
        await EventPublisher.publish_user_event(
            UserEvent(
                event_type="EMAIL_VERIFIED",
                user_id=str(user.id),
                data={"email": user.email}
            )
        )
    
    return {"message": "Email verified successfully"}

async def create_email_verification_token(user: User, db: AsyncSession) -> str:
    """
    Create email verification token
    """
    token = EmailVerificationToken(
        user_id=user.id,
        email=user.email,
        token=create_refresh_token(),
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    db.add(token)
    await db.commit()
    return token.token
