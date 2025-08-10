"""Session management using Redis."""
import json
import uuid
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import logging

import redis
from redis.exceptions import RedisError
from app.core.config import settings

logger = logging.getLogger(__name__)


class SessionManager:
    """Redis-based session manager."""
    
    def __init__(self, redis_url: str = None, db: int = None, ttl: int = 3600):
        """
        Initialize session manager.
        
        Args:
            redis_url: Redis connection URL
            db: Redis database number
            ttl: Default session TTL in seconds (default: 1 hour)
        """
        self.redis_url = redis_url or settings.REDIS_URL
        self.db = db or settings.REDIS_SESSION_DB
        self.default_ttl = ttl
        self.redis_client = None
        self._connect()
    
    def _connect(self):
        """Connect to Redis."""
        try:
            # Parse URL and set database
            self.redis_client = redis.from_url(
                self.redis_url,
                db=self.db,
                decode_responses=True
            )
            # Test connection
            self.redis_client.ping()
            logger.info(f"Successfully connected to Redis for sessions (db={self.db})")
        except RedisError as e:
            logger.error(f"Failed to connect to Redis for sessions: {e}")
            self.redis_client = None
    
    def is_connected(self) -> bool:
        """Check if Redis is connected."""
        if not self.redis_client:
            return False
        try:
            self.redis_client.ping()
            return True
        except RedisError:
            return False
    
    def create_session(
        self,
        user_id: str,
        data: Dict[str, Any] = None,
        ttl: Optional[int] = None
    ) -> Optional[str]:
        """
        Create a new session.
        
        Args:
            user_id: User ID
            data: Additional session data
            ttl: Session TTL in seconds
            
        Returns:
            Session ID if successful, None otherwise
        """
        if not self.is_connected():
            return None
        
        session_id = str(uuid.uuid4())
        session_key = f"session:{session_id}"
        
        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "last_accessed": datetime.utcnow().isoformat(),
            "data": data or {}
        }
        
        try:
            # Store session
            ttl = ttl or self.default_ttl
            self.redis_client.setex(
                session_key,
                ttl,
                json.dumps(session_data)
            )
            
            # Add to user's session set
            user_sessions_key = f"user_sessions:{user_id}"
            self.redis_client.sadd(user_sessions_key, session_id)
            self.redis_client.expire(user_sessions_key, ttl)
            
            logger.info(f"Created session {session_id} for user {user_id}")
            return session_id
            
        except RedisError as e:
            logger.error(f"Failed to create session: {e}")
            return None
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session data.
        
        Args:
            session_id: Session ID
            
        Returns:
            Session data if found, None otherwise
        """
        if not self.is_connected():
            return None
        
        session_key = f"session:{session_id}"
        
        try:
            data = self.redis_client.get(session_key)
            if data:
                session_data = json.loads(data)
                
                # Update last accessed time
                session_data["last_accessed"] = datetime.utcnow().isoformat()
                self.redis_client.setex(
                    session_key,
                    self.redis_client.ttl(session_key),
                    json.dumps(session_data)
                )
                
                return session_data
            
            return None
            
        except (RedisError, json.JSONDecodeError) as e:
            logger.error(f"Failed to get session: {e}")
            return None
    
    def update_session(
        self,
        session_id: str,
        data: Dict[str, Any],
        extend_ttl: bool = True
    ) -> bool:
        """
        Update session data.
        
        Args:
            session_id: Session ID
            data: Data to update
            extend_ttl: Whether to extend session TTL
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected():
            return False
        
        session_data = self.get_session(session_id)
        if not session_data:
            return False
        
        # Update data
        session_data["data"].update(data)
        session_data["last_accessed"] = datetime.utcnow().isoformat()
        
        session_key = f"session:{session_id}"
        
        try:
            if extend_ttl:
                ttl = self.default_ttl
            else:
                ttl = self.redis_client.ttl(session_key)
                if ttl <= 0:
                    ttl = self.default_ttl
            
            self.redis_client.setex(
                session_key,
                ttl,
                json.dumps(session_data)
            )
            
            return True
            
        except RedisError as e:
            logger.error(f"Failed to update session: {e}")
            return False
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.
        
        Args:
            session_id: Session ID
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected():
            return False
        
        session_data = self.get_session(session_id)
        if not session_data:
            return False
        
        session_key = f"session:{session_id}"
        user_id = session_data.get("user_id")
        
        try:
            # Delete session
            self.redis_client.delete(session_key)
            
            # Remove from user's session set
            if user_id:
                user_sessions_key = f"user_sessions:{user_id}"
                self.redis_client.srem(user_sessions_key, session_id)
            
            logger.info(f"Deleted session {session_id}")
            return True
            
        except RedisError as e:
            logger.error(f"Failed to delete session: {e}")
            return False
    
    def get_user_sessions(self, user_id: str) -> List[str]:
        """
        Get all sessions for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of session IDs
        """
        if not self.is_connected():
            return []
        
        user_sessions_key = f"user_sessions:{user_id}"
        
        try:
            sessions = self.redis_client.smembers(user_sessions_key)
            return list(sessions) if sessions else []
            
        except RedisError as e:
            logger.error(f"Failed to get user sessions: {e}")
            return []
    
    def delete_user_sessions(self, user_id: str) -> int:
        """
        Delete all sessions for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Number of sessions deleted
        """
        if not self.is_connected():
            return 0
        
        sessions = self.get_user_sessions(user_id)
        deleted = 0
        
        for session_id in sessions:
            if self.delete_session(session_id):
                deleted += 1
        
        # Clean up user sessions set
        try:
            user_sessions_key = f"user_sessions:{user_id}"
            self.redis_client.delete(user_sessions_key)
        except RedisError:
            pass
        
        logger.info(f"Deleted {deleted} sessions for user {user_id}")
        return deleted
    
    def extend_session(self, session_id: str, ttl: Optional[int] = None) -> bool:
        """
        Extend session TTL.
        
        Args:
            session_id: Session ID
            ttl: New TTL in seconds
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected():
            return False
        
        session_key = f"session:{session_id}"
        ttl = ttl or self.default_ttl
        
        try:
            return bool(self.redis_client.expire(session_key, ttl))
        except RedisError as e:
            logger.error(f"Failed to extend session: {e}")
            return False
    
    def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired sessions from user session sets.
        
        Returns:
            Number of expired sessions cleaned up
        """
        if not self.is_connected():
            return 0
        
        cleaned = 0
        
        try:
            # Get all user session sets
            cursor = 0
            while True:
                cursor, keys = self.redis_client.scan(
                    cursor,
                    match="user_sessions:*",
                    count=100
                )
                
                for key in keys:
                    # Get all sessions for this user
                    sessions = self.redis_client.smembers(key)
                    
                    for session_id in sessions:
                        # Check if session exists
                        if not self.redis_client.exists(f"session:{session_id}"):
                            self.redis_client.srem(key, session_id)
                            cleaned += 1
                
                if cursor == 0:
                    break
            
            logger.info(f"Cleaned up {cleaned} expired sessions")
            return cleaned
            
        except RedisError as e:
            logger.error(f"Failed to cleanup expired sessions: {e}")
            return cleaned


# Singleton instance
_session_manager: Optional[SessionManager] = None


def get_session_manager() -> SessionManager:
    """Get session manager instance."""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager


# Import List at the end to avoid circular imports
from typing import List
