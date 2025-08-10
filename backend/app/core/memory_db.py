"""In-memory database for development/testing when MongoDB is not available."""
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid
from bson import ObjectId

class InMemoryDatabase:
    """Simple in-memory database that mimics MongoDB operations."""
    
    def __init__(self):
        self.collections: Dict[str, List[Dict[str, Any]]] = {
            'users': [],
            'bookings': [],
            'cabs': []
        }
    
    def get_collection(self, name: str):
        """Get a collection by name."""
        if name not in self.collections:
            self.collections[name] = []
        return InMemoryCollection(name, self.collections[name])


class InMemoryCollection:
    """Mimics MongoDB collection operations."""
    
    def __init__(self, name: str, data: List[Dict[str, Any]]):
        self.name = name
        self.data = data
    
    async def find_one(self, filter_dict: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find one document matching the filter."""
        for doc in self.data:
            if all(doc.get(k) == v for k, v in filter_dict.items()):
                return doc.copy()
        return None
    
    async def find(self, filter_dict: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Find all documents matching the filter."""
        if not filter_dict:
            return [doc.copy() for doc in self.data]
        
        result = []
        for doc in self.data:
            if all(doc.get(k) == v for k, v in filter_dict.items()):
                result.append(doc.copy())
        return result
    
    async def insert_one(self, document: Dict[str, Any]) -> Any:
        """Insert one document."""
        doc = document.copy()
        doc['_id'] = ObjectId()
        doc['created_at'] = datetime.utcnow()
        doc['updated_at'] = datetime.utcnow()
        self.data.append(doc)
        
        class InsertResult:
            def __init__(self, inserted_id):
                self.inserted_id = inserted_id
        
        return InsertResult(doc['_id'])
    
    async def update_one(self, filter_dict: Dict[str, Any], update_dict: Dict[str, Any]) -> Any:
        """Update one document."""
        for doc in self.data:
            if all(doc.get(k) == v for k, v in filter_dict.items()):
                if '$set' in update_dict:
                    doc.update(update_dict['$set'])
                    doc['updated_at'] = datetime.utcnow()
                if '$unset' in update_dict:
                    for key in update_dict['$unset']:
                        doc.pop(key, None)
                break
        
        class UpdateResult:
            def __init__(self):
                self.modified_count = 1
        
        return UpdateResult()
    
    async def delete_one(self, filter_dict: Dict[str, Any]) -> Any:
        """Delete one document."""
        for i, doc in enumerate(self.data):
            if all(doc.get(k) == v for k, v in filter_dict.items()):
                self.data.pop(i)
                break
        
        class DeleteResult:
            def __init__(self):
                self.deleted_count = 1
        
        return DeleteResult()


# Global instance
memory_db = InMemoryDatabase()
