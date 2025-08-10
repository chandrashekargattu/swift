from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class MongoDB:
    client: Optional[AsyncIOMotorClient] = None
    database: Optional[AsyncIOMotorDatabase] = None
    is_memory: bool = False


db = MongoDB()
memory_db = None


async def connect_to_mongo():
    """Create database connection."""
    global memory_db
    
    try:
        # Try to connect to MongoDB
        db.client = AsyncIOMotorClient(settings.MONGODB_URL, serverSelectionTimeoutMS=5000)
        
        # Verify connection
        await db.client.server_info()
        db.database = db.client[settings.DATABASE_NAME]
        db.is_memory = False
        logger.info("Successfully connected to MongoDB")
    except Exception as e:
        logger.warning(f"Could not connect to MongoDB: {e}")
        logger.info("Using in-memory database for testing")
        
        # Use in-memory database as fallback
        from app.core.memory_db import memory_db as mem_db
        memory_db = mem_db
        db.is_memory = True
        db.database = memory_db


async def close_mongo_connection():
    """Close database connection."""
    if not db.is_memory and db.client:
        db.client.close()
        logger.info("Disconnected from MongoDB")


def get_database():
    """Get database instance."""
    if db.database is None:
        raise RuntimeError("Database is not initialized")
    return db.database


# Collection helpers
def get_collection(collection_name: str):
    """Get a specific collection."""
    if db.is_memory:
        return memory_db.get_collection(collection_name)
    
    database = get_database()
    return database[collection_name]


# Collections
def users_collection():
    return get_collection("users")


def bookings_collection():
    return get_collection("bookings")


def cabs_collection():
    return get_collection("cabs")


def drivers_collection():
    return get_collection("drivers")


def locations_collection():
    return get_collection("locations")


def payments_collection():
    return get_collection("payments")


def reviews_collection():
    return get_collection("reviews")