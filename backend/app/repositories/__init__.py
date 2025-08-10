"""Repository initialization and dependency injection."""
from typing import Optional
from app.core.database import users_collection, bookings_collection, cabs_collection
from app.repositories.user import UserRepository

# Repository instances (lazy initialization)
_user_repository: Optional[UserRepository] = None


# Dependency injection functions
def get_user_repository() -> UserRepository:
    """Get user repository instance."""
    global _user_repository
    if _user_repository is None:
        _user_repository = UserRepository(users_collection())
    return _user_repository
