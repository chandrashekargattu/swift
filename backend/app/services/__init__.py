"""Service initialization and dependency injection."""
from typing import Optional
from app.repositories import get_user_repository
from app.services.user import UserService
from app.services.ai_chatbot_lite import ai_chatbot_service

# Service instances (lazy initialization)
_user_service: Optional[UserService] = None


# Dependency injection functions
def get_user_service() -> UserService:
    """Get user service instance."""
    global _user_service
    if _user_service is None:
        _user_service = UserService(get_user_repository())
    return _user_service

# Export services
__all__ = ["get_user_service", "ai_chatbot_service"]
