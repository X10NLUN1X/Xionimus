"""
Redis Client Configuration for Caching and Session Management
"""
import redis
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Redis Configuration
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

# Global Redis client
redis_client: Optional[redis.Redis] = None

def get_redis_client() -> Optional[redis.Redis]:
    """
    Get Redis client instance
    Returns None if Redis is not available (graceful degradation)
    """
    global redis_client
    
    if redis_client is None:
        try:
            redis_client = redis.from_url(
                REDIS_URL,
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
            # Test connection
            redis_client.ping()
            logger.info(f"✅ Redis connected successfully at {REDIS_URL}")
        except Exception as e:
            logger.warning(f"⚠️ Redis connection failed: {e}. Continuing without cache...")
            redis_client = None
    
    return redis_client

def close_redis():
    """Close Redis connection"""
    global redis_client
    if redis_client:
        try:
            redis_client.close()
            logger.info("👋 Redis connection closed")
        except Exception as e:
            logger.warning(f"⚠️ Redis close failed: {e}")
        finally:
            redis_client = None

async def init_redis():
    """Initialize Redis connection"""
    # Only try to connect if REDIS_URL is explicitly set
    if os.environ.get("REDIS_URL"):
        get_redis_client()
    else:
        logger.info("ℹ️  Redis not configured (REDIS_URL not set). Skipping Redis initialization.")

async def close_redis_async():
    """Async wrapper for closing Redis"""
    close_redis()


async def get_redis_health() -> bool:
    """
    Check Redis health for readiness probe
    
    Returns:
        bool: True if Redis is healthy, False otherwise
    """
    try:
        client = get_redis_client()
        if client:
            client.ping()
            return True
        return False
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        return False


# Utility functions for common Redis operations
def cache_set(key: str, value: str, expire_seconds: int = 3600) -> bool:
    """
    Set a value in Redis cache
    Returns True if successful, False otherwise
    """
    try:
        client = get_redis_client()
        if client:
            client.setex(key, expire_seconds, value)
            return True
    except Exception as e:
        logger.error(f"Redis cache_set error: {e}")
    return False

def cache_get(key: str) -> Optional[str]:
    """
    Get a value from Redis cache
    Returns None if key doesn't exist or Redis unavailable
    """
    try:
        client = get_redis_client()
        if client:
            return client.get(key)
    except Exception as e:
        logger.error(f"Redis cache_get error: {e}")
    return None

def cache_delete(key: str) -> bool:
    """
    Delete a key from Redis cache
    Returns True if successful, False otherwise
    """
    try:
        client = get_redis_client()
        if client:
            client.delete(key)
            return True
    except Exception as e:
        logger.error(f"Redis cache_delete error: {e}")
    return False

def cache_exists(key: str) -> bool:
    """
    Check if a key exists in Redis cache
    """
    try:
        client = get_redis_client()
        if client:
            return client.exists(key) > 0
    except Exception as e:
        logger.error(f"Redis cache_exists error: {e}")
    return False
