from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from bson import ObjectId
from app.repositories.base import BaseRepository
from app.models.user import UserModel
from app.core.security import get_password_hash
from app.core.cache import cached, invalidate_cache, get_cache_manager
import logging

logger = logging.getLogger(__name__)


class UserRepository(BaseRepository[UserModel]):
    """Repository for user-related database operations."""
    
    async def create_user(self, user_data: Dict[str, Any]) -> UserModel:
        """Create a new user with hashed password."""
        try:
            # Hash the password before storing
            if 'password' in user_data:
                user_data['hashed_password'] = get_password_hash(user_data['password'])
                del user_data['password']
            
            # Set default values
            user_data.setdefault('is_active', True)
            user_data.setdefault('is_verified', False)
            user_data.setdefault('role', 'customer')
            user_data.setdefault('total_bookings', 0)
            user_data.setdefault('failed_login_attempts', 0)
            
            # Create the user
            user_dict = await self.create(user_data)
            return UserModel(**user_dict)
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise
    
    @cached(ttl=300, key_prefix="user_email")  # Cache for 5 minutes
    async def find_by_email(self, email: str) -> Optional[UserModel]:
        """Find a user by email address."""
        try:
            user_dict = await self.find_one({"email": email.lower()})
            return UserModel(**user_dict) if user_dict else None
        except Exception as e:
            logger.error(f"Error finding user by email {email}: {e}")
            raise
    
    async def find_by_phone(self, phone_number: str) -> Optional[UserModel]:
        """Find a user by phone number."""
        try:
            user_dict = await self.find_one({"phone_number": phone_number})
            return UserModel(**user_dict) if user_dict else None
        except Exception as e:
            logger.error(f"Error finding user by phone {phone_number}: {e}")
            raise
    
    async def find_active_users(self, skip: int = 0, limit: int = 100) -> List[UserModel]:
        """Find all active users."""
        try:
            users = await self.find_many(
                {"is_active": True},
                skip=skip,
                limit=limit,
                sort=[("created_at", -1)]
            )
            return [UserModel(**user) for user in users]
        except Exception as e:
            logger.error(f"Error finding active users: {e}")
            raise
    
    async def update_last_login(self, user_id: str) -> Optional[UserModel]:
        """Update user's last login timestamp."""
        try:
            updated_user = await self.update_by_id(
                user_id,
                {
                    "last_login": datetime.utcnow(),
                    "failed_login_attempts": 0
                }
            )
            return UserModel(**updated_user) if updated_user else None
        except Exception as e:
            logger.error(f"Error updating last login for user {user_id}: {e}")
            raise
    
    async def increment_failed_login_attempts(self, email: str) -> None:
        """Increment failed login attempts for a user."""
        try:
            await self.collection.update_one(
                {"email": email.lower()},
                {
                    "$inc": {"failed_login_attempts": 1},
                    "$set": {"last_failed_login": datetime.utcnow()}
                }
            )
        except Exception as e:
            logger.error(f"Error incrementing failed login attempts for {email}: {e}")
            raise
    
    async def is_user_locked(self, email: str, lockout_duration: int = 15) -> bool:
        """Check if user is locked due to failed login attempts."""
        try:
            user = await self.find_by_email(email)
            if not user:
                return False
            
            # Check if user has exceeded max attempts
            if user.failed_login_attempts >= 5:
                # Check if lockout period has passed
                if user.last_failed_login:
                    lockout_expires = user.last_failed_login + timedelta(minutes=lockout_duration)
                    if datetime.utcnow() < lockout_expires:
                        return True
                    else:
                        # Reset failed attempts if lockout period has passed
                        await self.update_by_id(
                            str(user.id),
                            {"failed_login_attempts": 0}
                        )
            
            return False
        except Exception as e:
            logger.error(f"Error checking user lock status for {email}: {e}")
            raise
    
    async def verify_user(self, user_id: str) -> Optional[UserModel]:
        """Mark a user as verified."""
        try:
            updated_user = await self.update_by_id(
                user_id,
                {
                    "is_verified": True,
                    "verified_at": datetime.utcnow()
                }
            )
            return UserModel(**updated_user) if updated_user else None
        except Exception as e:
            logger.error(f"Error verifying user {user_id}: {e}")
            raise
    
    async def deactivate_user(self, user_id: str) -> Optional[UserModel]:
        """Deactivate a user account."""
        try:
            updated_user = await self.update_by_id(
                user_id,
                {
                    "is_active": False,
                    "deactivated_at": datetime.utcnow()
                }
            )
            return UserModel(**updated_user) if updated_user else None
        except Exception as e:
            logger.error(f"Error deactivating user {user_id}: {e}")
            raise
    
    async def search_users(
        self,
        query: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[UserModel]:
        """Search users by name, email, or phone."""
        try:
            filter = {
                "$or": [
                    {"full_name": {"$regex": query, "$options": "i"}},
                    {"email": {"$regex": query, "$options": "i"}},
                    {"phone_number": {"$regex": query, "$options": "i"}}
                ]
            }
            
            users = await self.find_many(filter, skip=skip, limit=limit)
            return [UserModel(**user) for user in users]
        except Exception as e:
            logger.error(f"Error searching users with query {query}: {e}")
            raise
    
    async def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Get user statistics."""
        try:
            pipeline = [
                {"$match": {"_id": ObjectId(user_id)}},
                {
                    "$lookup": {
                        "from": "bookings",
                        "localField": "_id",
                        "foreignField": "user_id",
                        "as": "bookings"
                    }
                },
                {
                    "$project": {
                        "total_bookings": {"$size": "$bookings"},
                        "completed_bookings": {
                            "$size": {
                                "$filter": {
                                    "input": "$bookings",
                                    "cond": {"$eq": ["$$this.status", "completed"]}
                                }
                            }
                        },
                        "cancelled_bookings": {
                            "$size": {
                                "$filter": {
                                    "input": "$bookings",
                                    "cond": {"$eq": ["$$this.status", "cancelled"]}
                                }
                            }
                        },
                        "total_spent": {
                            "$sum": {
                                "$filter": {
                                    "input": "$bookings.final_fare",
                                    "cond": {"$eq": ["$$this.status", "completed"]}
                                }
                            }
                        }
                    }
                }
            ]
            
            results = await self.aggregate(pipeline)
            return results[0] if results else {
                "total_bookings": 0,
                "completed_bookings": 0,
                "cancelled_bookings": 0,
                "total_spent": 0
            }
        except Exception as e:
            logger.error(f"Error getting user stats for {user_id}: {e}")
            raise
