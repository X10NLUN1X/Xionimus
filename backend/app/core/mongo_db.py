"""
MongoDB Connection for Research History
Simple async MongoDB client using motor
"""
import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# MongoDB Configuration
MONGO_URL = os.environ.get("MONGO_URL")  # None if not set
DATABASE_NAME = "xionimus_ai"

# Global MongoDB client
_mongo_client: AsyncIOMotorClient = None
_mongo_db = None


async def connect_mongodb():
    """Connect to MongoDB"""
    global _mongo_client, _mongo_db
    
    try:
        _mongo_client = AsyncIOMotorClient(MONGO_URL)
        _mongo_db = _mongo_client[DATABASE_NAME]
        
        # Test connection
        await _mongo_client.admin.command('ping')
        logger.info(f"✅ Connected to MongoDB at {MONGO_URL}")
        
        # Create indexes for research_history collection
        await _mongo_db.research_history.create_index([("user_id", 1), ("timestamp", -1)])
        await _mongo_db.research_history.create_index([("id", 1), ("user_id", 1)])
        logger.info("✅ MongoDB indexes created for research_history")
        
        return _mongo_db
    except Exception as e:
        logger.error(f"❌ Failed to connect to MongoDB: {e}")
        raise


async def close_mongodb():
    """Close MongoDB connection"""
    global _mongo_client
    
    if _mongo_client:
        _mongo_client.close()
        logger.info("✅ MongoDB connection closed")


def get_mongodb():
    """Get MongoDB database instance"""
    return _mongo_db


# For backward compatibility with existing code
def get_database():
    """Alias for get_mongodb()"""
    return get_mongodb()



async def get_mongo_health() -> bool:
    """
    Check MongoDB health for readiness probe
    
    Returns:
        bool: True if MongoDB is healthy, False otherwise
    """
    global _mongo_client
    
    try:
        if _mongo_client:
            await _mongo_client.admin.command('ping')
            return True
        return False
    except Exception as e:
        logger.error(f"MongoDB health check failed: {e}")
        return False
