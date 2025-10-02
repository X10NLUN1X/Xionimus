"""
Database Initialization Module
Automatically creates tables and initial users on startup
"""
from sqlalchemy.orm import Session
from app.core.database import engine, Base, DATABASE_PATH
from app.models.user_models import User
import bcrypt
import uuid
import logging

logger = logging.getLogger(__name__)

def init_database():
    """
    Initialize database:
    - Create all tables
    - Create initial admin user if no users exist
    """
    try:
        logger.info("=" * 60)
        logger.info("🔧 Database Initialization")
        logger.info("=" * 60)
        
        # Log database path
        logger.info(f"📁 Database: {DATABASE_PATH}")
        logger.info(f"   Exists: {DATABASE_PATH.exists()}")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created/verified")
        
        # Check if any users exist
        with Session(engine) as session:
            user_count = session.query(User).count()
            
            if user_count == 0:
                logger.warning("⚠️  No users found in database")
                logger.info("🔧 Creating initial admin user...")
                
                # Create initial admin user
                user_id = str(uuid.uuid4())
                hashed_password = bcrypt.hashpw(b"admin123", bcrypt.gensalt()).decode('utf-8')
                
                admin_user = User(
                    id=user_id,
                    username="admin",
                    email="admin@xionimus.ai",
                    hashed_password=hashed_password,
                    role="admin",
                    is_active=True
                )
                
                session.add(admin_user)
                session.commit()
                
                logger.info("✅ Initial admin user created!")
                logger.info("=" * 60)
                logger.info("🎉 FIRST TIME SETUP COMPLETE")
                logger.info("=" * 60)
                logger.info("📝 Default Login Credentials:")
                logger.info("   Username: admin")
                logger.info("   Password: admin123")
                logger.info("=" * 60)
                logger.info("⚠️  Please change the password after first login!")
                logger.info("=" * 60)
                
            else:
                logger.info(f"✅ Database initialized - {user_count} user(s) found")
                
                # Log first few users (for debugging)
                users = session.query(User).limit(3).all()
                logger.info("📊 Registered users:")
                for user in users:
                    logger.info(f"   - {user.username} ({user.email}) - {user.role}")
                
                if user_count > 3:
                    logger.info(f"   ... and {user_count - 3} more")
        
        logger.info("=" * 60)
        return True
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def ensure_user_exists(username: str, email: str, password: str, role: str = "user") -> bool:
    """
    Ensure a specific user exists in the database
    Creates the user if it doesn't exist
    
    Returns True if user was created, False if already existed
    """
    try:
        with Session(engine) as session:
            # Check if user exists
            existing_user = session.query(User).filter(
                (User.username == username) | (User.email == email)
            ).first()
            
            if existing_user:
                logger.info(f"✅ User '{username}' already exists")
                return False
            
            # Create user
            user_id = str(uuid.uuid4())
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            new_user = User(
                id=user_id,
                username=username,
                email=email,
                hashed_password=hashed_password,
                role=role,
                is_active=True
            )
            
            session.add(new_user)
            session.commit()
            
            logger.info(f"✅ User '{username}' created successfully")
            return True
            
    except Exception as e:
        logger.error(f"❌ Failed to ensure user '{username}' exists: {e}")
        return False
