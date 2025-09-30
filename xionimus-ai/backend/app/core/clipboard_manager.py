"""
Clipboard Assistant for Xionimus AI
Manage clipboard history and AI-powered transformations
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pathlib import Path
import json
import hashlib

logger = logging.getLogger(__name__)

class ClipboardManager:
    """Manage clipboard history and AI transformations"""
    
    MAX_HISTORY = 100
    MAX_ITEM_SIZE = 1024 * 1024  # 1MB
    
    def __init__(self, persist_dir: str = "~/.xionimus_ai/clipboard"):
        """
        Initialize clipboard manager
        
        Args:
            persist_dir: Directory to persist clipboard history
        """
        self.persist_dir = Path(persist_dir).expanduser()
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        
        self.history_file = self.persist_dir / "history.json"
        self.history = self._load_history()
        
        logger.info(f"Clipboard Manager initialized with {len(self.history)} items")
    
    def _load_history(self) -> List[Dict[str, Any]]:
        """Load clipboard history from disk"""
        if self.history_file.exists():
            try:
                with open(self.history_file) as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading clipboard history: {e}")
        return []
    
    def _save_history(self):
        """Save clipboard history to disk"""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving clipboard history: {e}")
    
    def _generate_id(self, content: str) -> str:
        """Generate unique ID for clipboard item"""
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def add_item(
        self,
        content: str,
        content_type: str = "text",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Add item to clipboard history
        
        Args:
            content: Content to add
            content_type: Type of content (text, code, url, etc.)
            metadata: Additional metadata
            
        Returns:
            Clipboard item
        """
        if len(content) > self.MAX_ITEM_SIZE:
            raise ValueError(f"Content too large: {len(content)} bytes (max: {self.MAX_ITEM_SIZE})")
        
        item_id = self._generate_id(content)
        
        # Check if already exists
        existing = next((item for item in self.history if item['id'] == item_id), None)
        if existing:
            # Update timestamp and move to front
            existing['timestamp'] = datetime.now(timezone.utc).isoformat()
            existing['access_count'] = existing.get('access_count', 0) + 1
            self.history.remove(existing)
            self.history.insert(0, existing)
            self._save_history()
            return existing
        
        # Create new item
        item = {
            'id': item_id,
            'content': content,
            'content_type': content_type,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'access_count': 0,
            'metadata': metadata or {},
            'size_bytes': len(content)
        }
        
        # Add to history (front)
        self.history.insert(0, item)
        
        # Trim if too long
        if len(self.history) > self.MAX_HISTORY:
            self.history = self.history[:self.MAX_HISTORY]
        
        self._save_history()
        logger.info(f"Added clipboard item: {item_id}")
        return item
    
    def get_history(
        self,
        limit: int = 50,
        content_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get clipboard history
        
        Args:
            limit: Maximum items to return
            content_type: Filter by content type
            
        Returns:
            List of clipboard items
        """
        history = self.history
        
        if content_type:
            history = [item for item in history if item.get('content_type') == content_type]
        
        return history[:limit]
    
    def get_item(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Get specific clipboard item"""
        item = next((item for item in self.history if item['id'] == item_id), None)
        
        if item:
            item['access_count'] = item.get('access_count', 0) + 1
            self._save_history()
        
        return item
    
    def delete_item(self, item_id: str) -> bool:
        """Delete clipboard item"""
        original_len = len(self.history)
        self.history = [item for item in self.history if item['id'] != item_id]
        
        if len(self.history) < original_len:
            self._save_history()
            logger.info(f"Deleted clipboard item: {item_id}")
            return True
        return False
    
    def clear_history(self) -> int:
        """Clear all clipboard history"""
        count = len(self.history)
        self.history = []
        self._save_history()
        logger.info(f"Cleared {count} clipboard items")
        return count
    
    def search(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search clipboard history
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            Matching items
        """
        query_lower = query.lower()
        results = []
        
        for item in self.history:
            content = item.get('content', '').lower()
            if query_lower in content:
                results.append(item)
                if len(results) >= limit:
                    break
        
        return results
    
    def transform_content(
        self,
        item_id: str,
        transformation: str,
        ai_result: str
    ) -> Dict[str, Any]:
        """
        Store AI transformation result
        
        Args:
            item_id: Original item ID
            transformation: Type of transformation
            ai_result: AI-generated result
            
        Returns:
            New clipboard item with transformation
        """
        original_item = self.get_item(item_id)
        
        if not original_item:
            raise ValueError(f"Item not found: {item_id}")
        
        # Create new item with transformation
        new_item = self.add_item(
            content=ai_result,
            content_type=f"{original_item.get('content_type', 'text')}_transformed",
            metadata={
                'transformation': transformation,
                'original_id': item_id,
                'original_content_preview': original_item.get('content', '')[:100]
            }
        )
        
        return new_item
    
    def get_stats(self) -> Dict[str, Any]:
        """Get clipboard manager statistics"""
        if not self.history:
            return {
                'total_items': 0,
                'total_size_bytes': 0,
                'content_types': {},
                'most_accessed': None
            }
        
        # Count by type
        type_counts = {}
        for item in self.history:
            ctype = item.get('content_type', 'unknown')
            type_counts[ctype] = type_counts.get(ctype, 0) + 1
        
        # Most accessed
        most_accessed = max(self.history, key=lambda x: x.get('access_count', 0))
        
        return {
            'total_items': len(self.history),
            'total_size_bytes': sum(item.get('size_bytes', 0) for item in self.history),
            'content_types': type_counts,
            'most_accessed': {
                'id': most_accessed['id'],
                'access_count': most_accessed.get('access_count', 0),
                'content_type': most_accessed.get('content_type'),
                'content_preview': most_accessed.get('content', '')[:50] + '...'
            } if most_accessed else None,
            'persist_directory': str(self.persist_dir)
        }
    
    def get_favorites(self, threshold: int = 3) -> List[Dict[str, Any]]:
        """Get frequently accessed items"""
        favorites = [
            item for item in self.history
            if item.get('access_count', 0) >= threshold
        ]
        return sorted(favorites, key=lambda x: x.get('access_count', 0), reverse=True)
