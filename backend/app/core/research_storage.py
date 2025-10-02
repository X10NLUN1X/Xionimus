"""
Research Storage Manager für Xionimus AI
Speichert Research-Daten persistent und macht sie allen Agenten zugänglich
"""
import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pathlib import Path
import hashlib

logger = logging.getLogger(__name__)

class ResearchStorageManager:
    """Manages persistent research data storage"""
    
    def __init__(self, storage_dir: str = "/app/xionimus-ai/research_data"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.storage_dir / "research_index.json"
        self._init_index()
    
    def _init_index(self):
        """Initialize research index file"""
        if not self.index_file.exists():
            self._save_index({
                "created_at": datetime.now(timezone.utc).isoformat(),
                "total_research_items": 0,
                "research_items": []
            })
    
    def _load_index(self) -> Dict[str, Any]:
        """Load research index"""
        try:
            with open(self.index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load research index: {e}")
            return {"research_items": []}
    
    def _save_index(self, index: Dict[str, Any]):
        """Save research index"""
        try:
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(index, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save research index: {e}")
    
    def store_research(
        self,
        topic: str,
        content: str,
        source: str = "perplexity",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Store research data
        
        Returns:
            Research ID
        """
        # Generate unique ID
        research_id = hashlib.md5(f"{topic}_{datetime.now().isoformat()}".encode(), usedforsecurity=False).hexdigest()[:16]
        
        research_data = {
            "id": research_id,
            "topic": topic,
            "content": content,
            "source": source,
            "metadata": metadata or {},
            "created_at": datetime.now(timezone.utc).isoformat(),
            "tags": self._generate_tags(topic, content)
        }
        
        # Save research data to file
        research_file = self.storage_dir / f"{research_id}.json"
        try:
            with open(research_file, 'w', encoding='utf-8') as f:
                json.dump(research_data, f, indent=2, ensure_ascii=False)
            
            # Update index
            index = self._load_index()
            index["research_items"].append({
                "id": research_id,
                "topic": topic,
                "created_at": research_data["created_at"],
                "tags": research_data["tags"]
            })
            index["total_research_items"] = len(index["research_items"])
            self._save_index(index)
            
            logger.info(f"✅ Research stored: {research_id} - {topic}")
            return research_id
            
        except Exception as e:
            logger.error(f"Failed to store research: {e}")
            return ""
    
    def get_research(self, research_id: str) -> Optional[Dict[str, Any]]:
        """Get research by ID"""
        research_file = self.storage_dir / f"{research_id}.json"
        if not research_file.exists():
            return None
        
        try:
            with open(research_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load research {research_id}: {e}")
            return None
    
    def search_research(
        self,
        query: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search research by query
        
        Returns:
            List of matching research items
        """
        index = self._load_index()
        query_lower = query.lower()
        
        results = []
        for item in index.get("research_items", []):
            # Simple matching: check if query is in topic or tags
            if (query_lower in item["topic"].lower() or 
                any(query_lower in tag.lower() for tag in item.get("tags", []))):
                
                # Load full research data
                research_data = self.get_research(item["id"])
                if research_data:
                    results.append(research_data)
                    
                if len(results) >= limit:
                    break
        
        logger.info(f"🔍 Research search '{query}': {len(results)} results")
        return results
    
    def get_all_research(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get all research items (most recent first)"""
        index = self._load_index()
        items = index.get("research_items", [])
        
        # Sort by creation date (most recent first)
        items_sorted = sorted(items, key=lambda x: x.get("created_at", ""), reverse=True)
        
        results = []
        for item in items_sorted[:limit]:
            research_data = self.get_research(item["id"])
            if research_data:
                results.append(research_data)
        
        return results
    
    def _generate_tags(self, topic: str, content: str) -> List[str]:
        """Generate tags for research"""
        tags = []
        
        # Extract keywords from topic
        topic_words = topic.lower().split()
        tags.extend([word for word in topic_words if len(word) > 3])
        
        # Common technical keywords
        tech_keywords = [
            'python', 'javascript', 'typescript', 'react', 'vue', 'angular',
            'docker', 'kubernetes', 'api', 'backend', 'frontend', 'database',
            'mongodb', 'postgresql', 'mysql', 'redis', 'fastapi', 'flask',
            'django', 'nodejs', 'express', 'security', 'performance', 'testing'
        ]
        
        content_lower = content.lower()
        for keyword in tech_keywords:
            if keyword in content_lower:
                tags.append(keyword)
        
        # Remove duplicates and limit
        return list(set(tags))[:10]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get research storage statistics"""
        index = self._load_index()
        return {
            "total_research_items": index.get("total_research_items", 0),
            "created_at": index.get("created_at"),
            "storage_dir": str(self.storage_dir)
        }

# Global instance
research_storage = ResearchStorageManager()
