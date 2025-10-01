"""
Cache Manager - Simple in-memory caching for performance optimization
"""
from functools import lru_cache
from typing import Optional, Any
import hashlib
import json
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class SimpleCacheManager:
    """
    Simple in-memory cache with TTL support
    Used for caching expensive operations like AI responses (when appropriate)
    """
    
    def __init__(self, max_size: int = 1000, default_ttl_seconds: int = 3600):
        """
        Initialize cache manager
        
        Args:
            max_size: Maximum number of items to cache
            default_ttl_seconds: Default time-to-live in seconds (1 hour default)
        """
        self.cache = {}
        self.max_size = max_size
        self.default_ttl = default_ttl_seconds
        logger.info(f"✅ Cache Manager initialized (max_size: {max_size}, ttl: {default_ttl_seconds}s)")
    
    def _generate_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments"""
        key_data = {
            'args': args,
            'kwargs': kwargs
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value if exists and not expired, None otherwise
        """
        if key in self.cache:
            value, expiry = self.cache[key]
            
            # Check if expired
            if datetime.now() < expiry:
                logger.debug(f"✅ Cache HIT: {key[:8]}...")
                return value
            else:
                # Expired, remove from cache
                del self.cache[key]
                logger.debug(f"⏰ Cache EXPIRED: {key[:8]}...")
        
        logger.debug(f"❌ Cache MISS: {key[:8]}...")
        return None
    
    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None):
        """
        Set value in cache with TTL
        
        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Time to live in seconds (uses default if not provided)
        """
        if ttl_seconds is None:
            ttl_seconds = self.default_ttl
        
        expiry = datetime.now() + timedelta(seconds=ttl_seconds)
        
        # Check cache size limit
        if len(self.cache) >= self.max_size:
            # Remove oldest entry (simple FIFO eviction)
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
            logger.debug(f"🗑️ Cache EVICTED: {oldest_key[:8]}... (size limit)")
        
        self.cache[key] = (value, expiry)
        logger.debug(f"💾 Cache SET: {key[:8]}... (ttl: {ttl_seconds}s)")
    
    def delete(self, key: str):
        """Delete specific key from cache"""
        if key in self.cache:
            del self.cache[key]
            logger.debug(f"🗑️ Cache DELETED: {key[:8]}...")
    
    def clear(self):
        """Clear all cache entries"""
        count = len(self.cache)
        self.cache.clear()
        logger.info(f"🗑️ Cache CLEARED: {count} entries removed")
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        total_entries = len(self.cache)
        
        # Count expired entries
        expired_count = 0
        for _, (_, expiry) in self.cache.items():
            if datetime.now() >= expiry:
                expired_count += 1
        
        return {
            'total_entries': total_entries,
            'active_entries': total_entries - expired_count,
            'expired_entries': expired_count,
            'max_size': self.max_size,
            'utilization': f"{(total_entries / self.max_size) * 100:.1f}%"
        }


# Global cache instance
cache_manager = SimpleCacheManager(max_size=1000, default_ttl_seconds=3600)


# Decorator for easy caching
def cached(ttl_seconds: int = 3600):
    """
    Decorator to cache function results
    
    Example:
        @cached(ttl_seconds=300)
        async def expensive_operation(arg1, arg2):
            # Expensive operation
            return result
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Generate cache key
            key = cache_manager._generate_key(func.__name__, *args, **kwargs)
            
            # Try to get from cache
            result = cache_manager.get(key)
            if result is not None:
                return result
            
            # Execute function if not in cache
            result = await func(*args, **kwargs)
            
            # Store in cache
            cache_manager.set(key, result, ttl_seconds)
            
            return result
        
        return wrapper
    return decorator


# LRU Cache for frequently called utility functions
@lru_cache(maxsize=256)
def get_language_from_extension(extension: str) -> str:
    """
    Cached language detection from file extension
    This is called frequently and never changes
    """
    lang_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.jsx': 'javascript',
        '.ts': 'typescript',
        '.tsx': 'typescript',
        '.java': 'java',
        '.cpp': 'cpp',
        '.c': 'c',
        '.go': 'go',
        '.rs': 'rust',
        '.rb': 'ruby',
        '.php': 'php',
    }
    return lang_map.get(extension, 'unknown')
