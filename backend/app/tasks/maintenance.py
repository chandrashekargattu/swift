"""Maintenance tasks for Celery."""
import logging
from datetime import datetime, timedelta
from typing import Dict

from app.core.celery_app import celery_app
from app.core.session import get_session_manager
from app.core.cache import get_cache_manager
from app.core.database import get_database

logger = logging.getLogger(__name__)


@celery_app.task(name="cleanup_expired_sessions")
def cleanup_expired_sessions() -> Dict[str, any]:
    """
    Clean up expired sessions from Redis.
    
    Returns:
        Dict with cleanup statistics
    """
    try:
        session_manager = get_session_manager()
        cleaned_count = session_manager.cleanup_expired_sessions()
        
        logger.info(f"Cleaned up {cleaned_count} expired sessions")
        
        return {
            "status": "success",
            "cleaned_sessions": cleaned_count,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up sessions: {e}")
        return {
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@celery_app.task(name="clear_old_cache")
def clear_old_cache(pattern: str = "*", older_than_hours: int = 24) -> Dict[str, any]:
    """
    Clear old cache entries.
    
    Args:
        pattern: Cache key pattern to match
        older_than_hours: Clear entries older than this many hours
        
    Returns:
        Dict with cleanup statistics
    """
    try:
        cache_manager = get_cache_manager()
        
        # Clear cache matching pattern
        cleared_count = cache_manager.clear_pattern(f"cache:{pattern}")
        
        logger.info(f"Cleared {cleared_count} cache entries matching pattern: {pattern}")
        
        return {
            "status": "success",
            "cleared_entries": cleared_count,
            "pattern": pattern,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        return {
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@celery_app.task(name="cleanup_old_bookings")
async def cleanup_old_bookings(days_old: int = 365) -> Dict[str, any]:
    """
    Archive or delete old bookings.
    
    Args:
        days_old: Archive bookings older than this many days
        
    Returns:
        Dict with cleanup statistics
    """
    try:
        db = get_database()
        bookings_collection = db.bookings
        
        # Calculate cutoff date
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        # Find old completed/cancelled bookings
        old_bookings = await bookings_collection.count_documents({
            "created_at": {"$lt": cutoff_date},
            "status": {"$in": ["completed", "cancelled"]}
        })
        
        # Archive to a separate collection
        if old_bookings > 0:
            archived_collection = db.archived_bookings
            
            # Copy old bookings to archive
            async for booking in bookings_collection.find({
                "created_at": {"$lt": cutoff_date},
                "status": {"$in": ["completed", "cancelled"]}
            }):
                booking["archived_at"] = datetime.utcnow()
                await archived_collection.insert_one(booking)
            
            # Delete from main collection
            result = await bookings_collection.delete_many({
                "created_at": {"$lt": cutoff_date},
                "status": {"$in": ["completed", "cancelled"]}
            })
            
            archived_count = result.deleted_count
        else:
            archived_count = 0
        
        logger.info(f"Archived {archived_count} old bookings")
        
        return {
            "status": "success",
            "archived_bookings": archived_count,
            "cutoff_date": cutoff_date.isoformat(),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error archiving old bookings: {e}")
        return {
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@celery_app.task(name="cleanup_unverified_users")
async def cleanup_unverified_users(days_old: int = 7) -> Dict[str, any]:
    """
    Delete unverified user accounts older than specified days.
    
    Args:
        days_old: Delete unverified accounts older than this many days
        
    Returns:
        Dict with cleanup statistics
    """
    try:
        db = get_database()
        users_collection = db.users
        
        # Calculate cutoff date
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        # Delete unverified users
        result = await users_collection.delete_many({
            "created_at": {"$lt": cutoff_date},
            "is_verified": False
        })
        
        deleted_count = result.deleted_count
        
        logger.info(f"Deleted {deleted_count} unverified users")
        
        return {
            "status": "success",
            "deleted_users": deleted_count,
            "cutoff_date": cutoff_date.isoformat(),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error deleting unverified users: {e}")
        return {
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@celery_app.task(name="optimize_database")
async def optimize_database() -> Dict[str, any]:
    """
    Optimize database performance by rebuilding indexes and compacting collections.
    
    Returns:
        Dict with optimization statistics
    """
    try:
        db = get_database()
        
        collections_optimized = []
        
        # List of collections to optimize
        collections = ["users", "bookings", "drivers", "cabs"]
        
        for collection_name in collections:
            try:
                collection = db[collection_name]
                
                # Rebuild indexes
                await collection.reindex()
                
                # Get collection stats
                stats = await db.command("collStats", collection_name)
                
                collections_optimized.append({
                    "collection": collection_name,
                    "size": stats.get("size", 0),
                    "count": stats.get("count", 0),
                    "indexes": stats.get("nindexes", 0)
                })
                
            except Exception as e:
                logger.error(f"Error optimizing collection {collection_name}: {e}")
        
        logger.info(f"Optimized {len(collections_optimized)} collections")
        
        return {
            "status": "success",
            "collections_optimized": collections_optimized,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error optimizing database: {e}")
        return {
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
