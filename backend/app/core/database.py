from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pathlib import Path
import logging
import os

logger = logging.getLogger(__name__)

# SQLite Database - Local-first approach
HOME_DIR = Path.home() / ".xionimus_ai"
HOME_DIR.mkdir(exist_ok=True)
DATABASE_PATH = HOME_DIR / "xionimus.db"

SQLALCHEMY_DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# Create engine with proper pooling settings
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    pool_size=10,  # Increased from default 5
    max_overflow=20,  # Increased from default 10
    pool_timeout=60,  # Increased from 30 seconds
    pool_recycle=3600,  # Recycle connections after 1 hour
    pool_pre_ping=True  # Verify connections before using
)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

def get_database():
    """Get database session"""
    db = SessionLocal()
    try:
        return db
    finally:
        pass

async def init_database():
    """Initialize SQLite database and create tables"""
    try:
        # Create all tables
        from ..models import session_models, user_models  # Import models here
        Base.metadata.create_all(bind=engine)
        logger.info(f"✅ SQLite database initialized at {DATABASE_PATH}")
        
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