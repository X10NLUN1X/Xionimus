"""
Local Storage Manager for XIONIMUS AI
Replaces MongoDB Docker dependency with local file-based storage
Maintains all API functionality without Docker restrictions
"""

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional
import asyncio
import logging

class LocalStorageManager:
    """
    Local file-based storage manager that provides MongoDB-like functionality
    without Docker dependencies. Stores data in JSON files.
    """
    
    def __init__(self, storage_dir: str = "local_data"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        
        # Initialize collections
        self.collections = {
            'projects': self.storage_dir / 'projects.json',
            'chat_sessions': self.storage_dir / 'chat_sessions.json',
            'uploaded_files': self.storage_dir / 'uploaded_files.json',
            'api_keys': self.storage_dir / 'api_keys.json',
            'agents': self.storage_dir / 'agents.json',
            'code_files': self.storage_dir / 'code_files.json'
        }
        
        # Initialize empty collections if they don't exist
        for collection_name, file_path in self.collections.items():
            if not file_path.exists():
                self._save_collection(collection_name, [])
        
        logging.info(f"✅ Local storage initialized at {self.storage_dir}")
    
    def _load_collection(self, collection_name: str) -> List[Dict]:
        """Load collection data from JSON file"""
        try:
            file_path = self.collections[collection_name]
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            logging.warning(f"Error loading collection {collection_name}: {e}")
            return []
    
    def _save_collection(self, collection_name: str, data: List[Dict]):
        """Save collection data to JSON file"""
        try:
            file_path = self.collections[collection_name]
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            logging.error(f"Error saving collection {collection_name}: {e}")
            raise
    
    async def list_collection_names(self) -> List[str]:
        """List all collection names (MongoDB compatible)"""
        return list(self.collections.keys())
    
    async def find(self, collection_name: str, filter_dict: Dict = None, limit: int = None) -> List[Dict]:
        """Find documents in collection (MongoDB compatible)"""
        data = self._load_collection(collection_name)
        
        if filter_dict:
            filtered_data = []
            for item in data:
                match = True
                for key, value in filter_dict.items():
                    if key not in item or item[key] != value:
                        match = False
                        break
                if match:
                    filtered_data.append(item)
            data = filtered_data
        
        if limit:
            data = data[:limit]
        
        return data
    
    async def find_one(self, collection_name: str, filter_dict: Dict) -> Optional[Dict]:
        """Find one document in collection (MongoDB compatible)"""
        results = await self.find(collection_name, filter_dict, limit=1)
        return results[0] if results else None
    
    async def insert_one(self, collection_name: str, document: Dict) -> Dict:
        """Insert one document into collection (MongoDB compatible)"""
        data = self._load_collection(collection_name)
        
        # Add timestamp and ID if not present
        if '_id' not in document:
            document['_id'] = str(uuid.uuid4())
        if 'created_at' not in document:
            document['created_at'] = datetime.now(timezone.utc).isoformat()
        
        data.append(document)
        self._save_collection(collection_name, data)
        
        logging.info(f"📝 Inserted document into {collection_name}: {document.get('_id', 'unknown')}")
        return document
    
    async def update_one(self, collection_name: str, filter_dict: Dict, update_dict: Dict) -> bool:
        """Update one document in collection (MongoDB compatible)"""
        data = self._load_collection(collection_name)
        
        for i, item in enumerate(data):
            match = True
            for key, value in filter_dict.items():
                if key not in item or item[key] != value:
                    match = False
                    break
            
            if match:
                # Update fields
                if '$set' in update_dict:
                    item.update(update_dict['$set'])
                else:
                    item.update(update_dict)
                
                item['updated_at'] = datetime.now(timezone.utc).isoformat()
                data[i] = item
                self._save_collection(collection_name, data)
                
                logging.info(f"🔄 Updated document in {collection_name}")
                return True
        
        return False
    
    async def delete_one(self, collection_name: str, filter_dict: Dict) -> bool:
        """Delete one document from collection (MongoDB compatible)"""
        data = self._load_collection(collection_name)
        
        for i, item in enumerate(data):
            match = True
            for key, value in filter_dict.items():
                if key not in item or item[key] != value:
                    match = False
                    break
            
            if match:
                del data[i]
                self._save_collection(collection_name, data)
                logging.info(f"🗑️ Deleted document from {collection_name}")
                return True
        
        return False
    
    async def count_documents(self, collection_name: str, filter_dict: Dict = None) -> int:
        """Count documents in collection (MongoDB compatible)"""
        results = await self.find(collection_name, filter_dict)
        return len(results)
    
    async def admin_command(self, command: str):
        """Admin command for health checks (MongoDB compatible)"""
        if command == 'ping':
            return {'ok': 1}
        return {'ok': 0}

# Create collection-like classes for MongoDB compatibility
class LocalUpdateResult:
    """Result object for update operations (MongoDB compatible)"""
    def __init__(self, matched_count: int = 0, modified_count: int = 0, upserted_id: str = None):
        self.matched_count = matched_count
        self.modified_count = modified_count
        self.upserted_id = upserted_id

class LocalDeleteResult:
    """Result object for delete operations (MongoDB compatible)"""
    def __init__(self, deleted_count: int = 0):
        self.deleted_count = deleted_count

class LocalCollection:
    def __init__(self, storage_manager: LocalStorageManager, collection_name: str):
        self.storage_manager = storage_manager
        self.collection_name = collection_name
    
    async def find(self, filter_dict: Dict = None):
        """Find documents - returns results directly"""
        results = await self.storage_manager.find(self.collection_name, filter_dict)
        return LocalCursor(results)
    
    async def find_one(self, filter_dict: Dict):
        return await self.storage_manager.find_one(self.collection_name, filter_dict)
    
    async def insert_one(self, document: Dict):
        return await self.storage_manager.insert_one(self.collection_name, document)
    
    async def update_one(self, filter_dict: Dict, update_dict: Dict, upsert: bool = False):
        # Handle upsert functionality
        if upsert:
            existing = await self.find_one(filter_dict)
            if existing:
                return await self.storage_manager.update_one(self.collection_name, filter_dict, update_dict)
            else:
                # Create new document with filter + update data
                new_doc = filter_dict.copy()
                if '$set' in update_dict:
                    new_doc.update(update_dict['$set'])
                if '$setOnInsert' in update_dict:
                    new_doc.update(update_dict['$setOnInsert'])
                result = await self.storage_manager.insert_one(self.collection_name, new_doc)
                return LocalUpdateResult(matched_count=0, modified_count=0, upserted_id=result['_id'])
        else:
            success = await self.storage_manager.update_one(self.collection_name, filter_dict, update_dict)
            return LocalUpdateResult(matched_count=1 if success else 0, modified_count=1 if success else 0)
    
    async def delete_one(self, filter_dict: Dict):
        success = await self.storage_manager.delete_one(self.collection_name, filter_dict)
        return LocalDeleteResult(deleted_count=1 if success else 0)
    
    async def count_documents(self, filter_dict: Dict = None):
        return await self.storage_manager.count_documents(self.collection_name, filter_dict)

class LocalCursor:
    """Cursor-like object for MongoDB compatibility"""
    def __init__(self, results: List[Dict]):
        self.results = results
    
    def sort(self, field: str, direction: int = 1):
        """Sort results by field (1 for ascending, -1 for descending)"""
        reverse = direction == -1
        try:
            # Handle datetime fields
            if self.results and field in self.results[0]:
                if 'at' in field:  # datetime fields like 'created_at', 'updated_at'
                    self.results.sort(key=lambda x: x.get(field, ''), reverse=reverse)
                else:
                    self.results.sort(key=lambda x: x.get(field, ''), reverse=reverse)
        except Exception:
            # Fallback to string sorting
            self.results.sort(key=lambda x: str(x.get(field, '')), reverse=reverse)
        return self
    
    async def to_list(self, length: Optional[int] = None):
        if length is None:
            return self.results
        return self.results[:length]
    
    def to_list(self, length: Optional[int] = None):
        """Synchronous version for direct calls"""
        if length is None:
            return self.results
        return self.results[:length]

class LocalDatabase:
    """Database-like object for MongoDB compatibility"""
    def __init__(self, storage_manager: LocalStorageManager):
        self.storage_manager = storage_manager
        
        # Create collection objects
        self.projects = LocalCollection(storage_manager, 'projects')
        self.chat_sessions = LocalCollection(storage_manager, 'chat_sessions')
        self.uploaded_files = LocalCollection(storage_manager, 'uploaded_files')
        self.api_keys = LocalCollection(storage_manager, 'api_keys')
        self.agents = LocalCollection(storage_manager, 'agents')
        self.code_files = LocalCollection(storage_manager, 'code_files')
    
    async def list_collection_names(self):
        return await self.storage_manager.list_collection_names()

class LocalClient:
    """Client-like object for MongoDB compatibility"""
    def __init__(self, storage_manager: LocalStorageManager):
        self.storage_manager = storage_manager
        
        # Admin interface
        self.admin = AdminInterface(storage_manager)
    
    def __getitem__(self, db_name: str):
        return LocalDatabase(self.storage_manager)
    
    def close(self):
        """Close connection (no-op for local storage)"""
        pass

class AdminInterface:
    """Admin interface for MongoDB compatibility"""
    def __init__(self, storage_manager: LocalStorageManager):
        self.storage_manager = storage_manager
    
    async def command(self, command: str):
        return await self.storage_manager.admin_command(command)