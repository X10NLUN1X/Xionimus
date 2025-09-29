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
    """Get database instance"""
    return db.db

async def init_database():
    """Initialize database connection"""
    try:
        db.client = AsyncIOMotorClient(settings.MONGO_URL)
        db.db = db.client.get_default_database()
        
        # Test connection
        await db.client.admin.command('ping')
        logger.info("✅ MongoDB connection established")
        
        # Create indexes
        await create_indexes()
        
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        # For development, continue without database
        logger.warning("⚠️ Continuing without database - some features disabled")

async def close_database():
    """Close database connection"""
    if db.client:
        db.client.close()
        logger.info("👋 Database connection closed")

async def create_indexes():
    """Create database indexes for optimal performance"""
    try:
        # Chat collections
        await db.db.chat_sessions.create_index("session_id")
        await db.db.chat_sessions.create_index("user_id")
        await db.db.chat_sessions.create_index("created_at")
        
        await db.db.chat_messages.create_index("session_id")
        await db.db.chat_messages.create_index("created_at")
        
        # File collections
        await db.db.uploaded_files.create_index("file_id")
        await db.db.uploaded_files.create_index("user_id")
        await db.db.uploaded_files.create_index("uploaded_at")
        
        # Workspace collections
        await db.db.workspace_files.create_index("file_path")
        await db.db.workspace_files.create_index("user_id")
        await db.db.workspace_files.create_index("modified_at")
        
        # User collections
        await db.db.users.create_index("email", unique=True)
        await db.db.users.create_index("username", unique=True)
        
        logger.info("✅ Database indexes created")
    except Exception as e:
        logger.warning(f"⚠️ Index creation failed: {e}")