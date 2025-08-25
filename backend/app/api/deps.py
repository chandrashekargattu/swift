from typing import Optional
from datetime import datetime
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from app.core.config import settings
from app.core.database import users_collection
from app.models.user import UserModel
from app.schemas.user import TokenData
from bson import ObjectId


security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserModel:
    """Get current authenticated user."""
    token = credentials.credentials
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        user_id: str = payload.get("user_id")
        if email is None or user_id is None:
            raise credentials_exception
        token_data = TokenData(email=email, user_id=user_id)
    except JWTError:
        raise credentials_exception
    
    # Get user from database
    user_dict = await users_collection().find_one({"_id": ObjectId(token_data.user_id)})
    if user_dict is None:
        raise credentials_exception
    
    user = UserModel(**user_dict)
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return user


async def get_current_active_user(current_user: UserModel = Depends(get_current_user)) -> UserModel:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))) -> Optional[UserModel]:
    """Get current user if authenticated, otherwise return None."""
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        user_id: str = payload.get("user_id")
        
        if not email or not user_id:
            return None
            
        # Get user from database
        user_dict = await users_collection().find_one({"_id": ObjectId(user_id)})
        if not user_dict:
            return None
            
        user = UserModel(**user_dict)
        if not user.is_active:
            return None
            
        return user
    except (JWTError, Exception):
        return None


async def get_current_admin_user(current_user: UserModel = Depends(get_current_user)) -> UserModel:
    """Get current admin user."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


async def get_current_driver(current_user: UserModel = Depends(get_current_user)) -> UserModel:
    """Get current driver user."""
    if current_user.role != "driver":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a driver account"
        )
    return current_user


class RateLimiter:
    """Rate limiter dependency."""
    def __init__(self, calls: int = 10, period: int = 60):
        self.calls = calls
        self.period = period
        self.cache = {}
    
    async def __call__(self, user: UserModel = Depends(get_current_user)):
        # Simple in-memory rate limiting (in production, use Redis)
        key = str(user.id)
        now = datetime.utcnow()
        
        if key not in self.cache:
            self.cache[key] = []
        
        # Remove old entries
        self.cache[key] = [
            timestamp for timestamp in self.cache[key]
            if (now - timestamp).total_seconds() < self.period
        ]
        
        if len(self.cache[key]) >= self.calls:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded"
            )
        
        self.cache[key].append(now)
        return user
