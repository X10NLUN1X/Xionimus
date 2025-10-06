from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pathlib import Path
import logging
import os

logger = logging.getLogger(__name__)

# Database Configuration - PostgreSQL with pgvector support
DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    # Fallback to SQLite if DATABASE_URL not configured
    HOME_DIR = Path.home() / ".xionimus_ai"
    HOME_DIR.mkdir(exist_ok=True)
    DATABASE_PATH = HOME_DIR / "xionimus.db"
    DATABASE_URL = f"sqlite:///{DATABASE_PATH}"
    logger.warning("⚠️ DATABASE_URL not set, falling back to SQLite")

# Determine if using PostgreSQL
IS_POSTGRESQL = DATABASE_URL.startswith("postgresql")

# Create engine with appropriate settings
if IS_POSTGRESQL:
    engine = create_engine(
        DATABASE_URL,
        pool_size=20,  # Larger pool for PostgreSQL
        max_overflow=40,
        pool_timeout=60,
        pool_recycle=3600,
        pool_pre_ping=True,
        echo=False  # Set to True for SQL debugging
    )
    logger.info("✅ Using PostgreSQL database with pgvector support")
else:
    # SQLite settings
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False},
        pool_size=10,
        max_overflow=20,
        pool_timeout=60,
        pool_recycle=3600,
        pool_pre_ping=True
    )
    logger.info("✅ Using SQLite database")

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

def get_database():
    """
    Get database session - for dependency injection
    IMPORTANT: When used as Depends(), FastAPI handles closing automatically
    When called directly: MUST close with db.close() in finally block
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_session():
    """
    Get database session - for direct usage (not dependency injection)
    IMPORTANT: Caller MUST close the session with db.close() in finally block
    """
    return SessionLocal()

async def init_database():
    """Initialize database and create tables"""
    try:
        # Create all tables
        from ..models import session_models, user_models, agent_models  # Import models here
        Base.metadata.create_all(bind=engine)
        
        db_type = "PostgreSQL" if IS_POSTGRESQL else "SQLite"
        logger.info(f"✅ {db_type} database initialized successfully")
        
        # Auto-create initial user if database is empty
        from .db_init import init_database as init_db_with_users
        init_db_with_users()
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise

async def close_database():
    """Close database connection"""
    try:
        engine.dispose()
        logger.info("👋 Database connection closed")
    except Exception as e:
        logger.warning(f"⚠️ Database close failed: {e}")