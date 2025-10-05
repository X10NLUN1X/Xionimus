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

# Use print for startup messages to ensure they're visible
def log_info(message):
    """Log to both logger and stdout for visibility"""
    print(message)
    logging.info(message)

def init_database():
    """
    Initialize database:
    - Create all tables
    - Create initial admin user if no users exist
    """
    try:
        log_info("=" * 60)
        log_info("🔧 Database Initialization")
        log_info("=" * 60)
        
        # Log database path
        log_info(f"📁 Database: {DATABASE_PATH}")
        log_info(f"   Exists: {DATABASE_PATH.exists()}")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        log_info("✅ Database tables created/verified")
        
        # Check if any users exist
        with Session(engine) as session:
            user_count = session.query(User).count()
            
            if user_count == 0:
                log_info("⚠️  No users found in database")
                log_info("🔧 Creating initial admin user...")
                
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
                
                log_info("✅ Initial admin user created!")
                log_info("=" * 60)
                log_info("🎉 FIRST TIME SETUP COMPLETE")
                log_info("=" * 60)
                log_info("📝 Default Login Credentials:")
                log_info("   Username: admin")
                log_info("   Password: admin123")
                log_info("=" * 60)
                log_info("⚠️  Please change the password after first login!")
                log_info("   Or register a new account via GUI")
                log_info("=" * 60)
                
            else:
                log_info(f"✅ Database initialized - {user_count} user(s) found")
                
                # Log first few users (for debugging)
                users = session.query(User).limit(3).all()
                log_info("📊 Registered users:")
                for user in users:
                    log_info(f"   - {user.username} ({user.email}) - {user.role}")
                
                if user_count > 3:
                    log_info(f"   ... and {user_count - 3} more")
        
        log_info("=" * 60)
        return True
        
    except Exception as e:
        error_msg = f"❌ Database initialization failed: {e}"
        print(error_msg)
        logging.error(error_msg)
        import traceback
        traceback.print_exc()
        return False
