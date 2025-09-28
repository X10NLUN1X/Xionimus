from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
import logging
from .config import settings

logger = logging.getLogger(__name__)

class Database:
    client: Optional[AsyncIOMotorClient] = None
    db = None

db = Database()

async def get_database():
    return db.db

async def init_database():
    """Initialize database connection"""
    try:
        db.client = AsyncIOMotorClient(settings.MONGO_URL)
        db.db = db.client.get_default_database()
        
        # Test connection
        await db.client.admin.command('ping')
        logger.info("✅ MongoDB connection established")
        
        # Create indexes if needed
        await create_indexes()
        
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        raise

async def create_indexes():
    """Create database indexes for optimal performance"""
    try:
        # Chat sessions index
        await db.db.chat_sessions.create_index("session_id")
        await db.db.chat_sessions.create_index("created_at")
        
        # Files index
        await db.db.uploaded_files.create_index("file_id")
        await db.db.uploaded_files.create_index("uploaded_at")
        
        # Projects index
        await db.db.projects.create_index("project_id")
        
        logger.info("✅ Database indexes created")
    except Exception as e:
        logger.warning(f"⚠️ Index creation failed: {e}")

async def close_database():
    """Close database connection"""
    if db.client:
        db.client.close()
        logger.info("👋 Database connection closed")