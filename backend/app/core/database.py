from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pathlib import Path
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Database Configuration - PostgreSQL with pgvector support
DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    # Fallback to SQLite if DATABASE_URL not configured
    HOME_DIR = Path.home() / ".xionimus_ai"
    HOME_DIR.mkdir(exist_ok=True)
    DATABASE_PATH = HOME_DIR / "xionimus.db"
    
    # Use proper SQLite URL format for cross-platform compatibility
    # Windows paths work better with forward slashes in SQLite URLs
    database_path_str = str(DATABASE_PATH).replace('\\', '/')
    DATABASE_URL = f"sqlite:///{database_path_str}"
    logger.warning(f"⚠️ DATABASE_URL not set, falling back to SQLite: {DATABASE_URL}")

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
    # SQLite settings with Windows-optimized configuration
    engine = create_engine(
        DATABASE_URL, 
        connect_args={
            "check_same_thread": False,
            "timeout": 30.0,  # Longer timeout for Windows file locking
            "isolation_level": None,  # Autocommit mode to reduce locking
        },
        pool_size=5,  # Reduced pool size for SQLite
        max_overflow=10,  # Lower overflow for SQLite
        pool_timeout=60,
        pool_recycle=3600,
        pool_pre_ping=True,
        echo=False
    )
    logger.info("✅ Using SQLite database with Windows-optimized settings")

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
        # Enable WAL mode for SQLite (better concurrency on Windows)
        if not IS_POSTGRESQL:
            from sqlalchemy import text
            with engine.connect() as conn:
                conn.execute(text("PRAGMA journal_mode=WAL"))
                conn.execute(text("PRAGMA synchronous=NORMAL"))
                conn.execute(text("PRAGMA cache_size=10000"))
                conn.execute(text("PRAGMA temp_store=MEMORY"))
                conn.commit()
                logger.info("✅ SQLite WAL mode enabled for better Windows concurrency")
        
        # Create all tables
        from ..models import session_models, user_models  # Import models here
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


async def get_database_health() -> bool:
    """
    Check database health for readiness probe
    
    Returns:
        bool: True if database is healthy, False otherwise
    """
    try:
        from sqlalchemy import text
        db = SessionLocal()
        try:
            # Execute a simple query to test connection
            db.execute(text("SELECT 1"))
            return True
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False
