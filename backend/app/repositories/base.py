from typing import Optional, List, Dict, Any, TypeVar, Generic
from motor.motor_asyncio import AsyncIOMotorCollection
from bson import ObjectId
from datetime import datetime
import logging

T = TypeVar('T')

logger = logging.getLogger(__name__)


class BaseRepository(Generic[T]):
    """Base repository class with common CRUD operations."""
    
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection
    
    async def create(self, data: Dict[str, Any]) -> T:
        """Create a new document."""
        try:
            # Add timestamps
            data['created_at'] = datetime.utcnow()
            data['updated_at'] = datetime.utcnow()
            
            result = await self.collection.insert_one(data)
            data['_id'] = result.inserted_id
            return data
        except Exception as e:
            logger.error(f"Error creating document: {e}")
            raise
    
    async def find_by_id(self, id: str) -> Optional[T]:
        """Find a document by ID."""
        try:
            object_id = ObjectId(id)
            document = await self.collection.find_one({"_id": object_id})
            return document
        except Exception as e:
            logger.error(f"Error finding document by id {id}: {e}")
            raise
    
    async def find_one(self, filter: Dict[str, Any]) -> Optional[T]:
        """Find a single document matching the filter."""
        try:
            document = await self.collection.find_one(filter)
            return document
        except Exception as e:
            logger.error(f"Error finding document: {e}")
            raise
    
    async def find_many(
        self,
        filter: Dict[str, Any] = {},
        skip: int = 0,
        limit: int = 100,
        sort: List[tuple] = None
    ) -> List[T]:
        """Find multiple documents matching the filter."""
        try:
            cursor = self.collection.find(filter)
            
            if sort:
                cursor = cursor.sort(sort)
            
            cursor = cursor.skip(skip).limit(limit)
            
            documents = await cursor.to_list(length=limit)
            return documents
        except Exception as e:
            logger.error(f"Error finding documents: {e}")
            raise
    
    async def count(self, filter: Dict[str, Any] = {}) -> int:
        """Count documents matching the filter."""
        try:
            count = await self.collection.count_documents(filter)
            return count
        except Exception as e:
            logger.error(f"Error counting documents: {e}")
            raise
    
    async def update_by_id(self, id: str, data: Dict[str, Any]) -> Optional[T]:
        """Update a document by ID."""
        try:
            object_id = ObjectId(id)
            
            # Add updated timestamp
            data['updated_at'] = datetime.utcnow()
            
            result = await self.collection.update_one(
                {"_id": object_id},
                {"$set": data}
            )
            
            if result.modified_count == 0:
                return None
            
            return await self.find_by_id(id)
        except Exception as e:
            logger.error(f"Error updating document {id}: {e}")
            raise
    
    async def update_many(self, filter: Dict[str, Any], data: Dict[str, Any]) -> int:
        """Update multiple documents matching the filter."""
        try:
            # Add updated timestamp
            data['updated_at'] = datetime.utcnow()
            
            result = await self.collection.update_many(
                filter,
                {"$set": data}
            )
            
            return result.modified_count
        except Exception as e:
            logger.error(f"Error updating documents: {e}")
            raise
    
    async def delete_by_id(self, id: str) -> bool:
        """Delete a document by ID."""
        try:
            object_id = ObjectId(id)
            result = await self.collection.delete_one({"_id": object_id})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting document {id}: {e}")
            raise
    
    async def delete_many(self, filter: Dict[str, Any]) -> int:
        """Delete multiple documents matching the filter."""
        try:
            result = await self.collection.delete_many(filter)
            return result.deleted_count
        except Exception as e:
            logger.error(f"Error deleting documents: {e}")
            raise
    
    async def aggregate(self, pipeline: List[Dict[str, Any]]) -> List[Any]:
        """Execute an aggregation pipeline."""
        try:
            cursor = self.collection.aggregate(pipeline)
            results = await cursor.to_list(length=None)
            return results
        except Exception as e:
            logger.error(f"Error executing aggregation: {e}")
            raise
    
    async def exists(self, filter: Dict[str, Any]) -> bool:
        """Check if a document exists."""
        try:
            count = await self.collection.count_documents(filter, limit=1)
            return count > 0
        except Exception as e:
            logger.error(f"Error checking document existence: {e}")
            raise
