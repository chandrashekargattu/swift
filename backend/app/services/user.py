from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from app.repositories.user import UserRepository
from app.models.user import UserModel
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.core.security import verify_password, create_access_token
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class UserService:
    """Service layer for user business logic."""
    
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    async def create_user(self, user_data: UserCreate) -> UserResponse:
        """Create a new user."""
        try:
            # Check if user already exists
            existing_user = await self.user_repository.find_by_email(user_data.email)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="User with this email already exists"
                )
            
            # Check if phone number is already registered
            existing_phone = await self.user_repository.find_by_phone(user_data.phone_number)
            if existing_phone:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="User with this phone number already exists"
                )
            
            # Create the user
            user_dict = user_data.dict()
            user = await self.user_repository.create_user(user_dict)
            
            # Convert to response model
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
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )
    
    async def authenticate_user(self, email: str, password: str) -> Optional[UserModel]:
        """Authenticate a user."""
        try:
            # Check if user is locked
            if await self.user_repository.is_user_locked(email):
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Account locked due to too many failed login attempts. Please try again later."
                )
            
            # Find user by email
            user = await self.user_repository.find_by_email(email)
            if not user:
                # Increment failed attempts even if user doesn't exist (security)
                await self.user_repository.increment_failed_login_attempts(email)
                return None
            
            # Verify password
            if not verify_password(password, user.hashed_password):
                await self.user_repository.increment_failed_login_attempts(email)
                return None
            
            # Check if user is active
            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User account is deactivated"
                )
            
            # Update last login
            await self.user_repository.update_last_login(str(user.id))
            
            return user
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            return None
    
    async def get_user_by_id(self, user_id: str) -> UserResponse:
        """Get a user by ID."""
        try:
            user_dict = await self.user_repository.find_by_id(user_id)
            if not user_dict:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            user = UserModel(**user_dict)
            
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
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get user"
            )
    
    async def update_user(self, user_id: str, user_update: UserUpdate) -> UserResponse:
        """Update a user."""
        try:
            # Check if user exists
            existing_user = await self.user_repository.find_by_id(user_id)
            if not existing_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Check if email is being updated and already exists
            if user_update.email and user_update.email != existing_user['email']:
                email_exists = await self.user_repository.find_by_email(user_update.email)
                if email_exists:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Email already in use"
                    )
            
            # Check if phone is being updated and already exists
            if user_update.phone_number and user_update.phone_number != existing_user['phone_number']:
                phone_exists = await self.user_repository.find_by_phone(user_update.phone_number)
                if phone_exists:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Phone number already in use"
                    )
            
            # Update the user
            update_data = user_update.dict(exclude_unset=True)
            updated_user = await self.user_repository.update_by_id(user_id, update_data)
            
            if not updated_user:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to update user"
                )
            
            user = UserModel(**updated_user)
            
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
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update user"
            )
    
    async def deactivate_user(self, user_id: str) -> bool:
        """Deactivate a user."""
        try:
            user = await self.user_repository.deactivate_user(user_id)
            return user is not None
        except Exception as e:
            logger.error(f"Error deactivating user {user_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to deactivate user"
            )
    
    async def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Get user statistics."""
        try:
            stats = await self.user_repository.get_user_stats(user_id)
            
            # Get user info
            user_dict = await self.user_repository.find_by_id(user_id)
            if not user_dict:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            user = UserModel(**user_dict)
            
            return {
                **stats,
                "member_since": user.created_at,
                "is_verified": user.is_verified,
                "last_login": user.last_login
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting user stats for {user_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get user statistics"
            )
    
    async def search_users(
        self,
        query: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[UserResponse]:
        """Search users."""
        try:
            users = await self.user_repository.search_users(query, skip, limit)
            
            return [
                UserResponse(
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
                for user in users
            ]
        except Exception as e:
            logger.error(f"Error searching users: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to search users"
            )
    
    async def verify_user(self, user_id: str) -> UserResponse:
        """Verify a user."""
        try:
            user = await self.user_repository.verify_user(user_id)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
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
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error verifying user {user_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to verify user"
            )
