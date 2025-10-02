#!/usr/bin/env python3
"""
Demo User Setup Script
Creates a demo user for testing authentication
"""

import sys
import os
sys.path.append('/app/backend')

from app.core.database import SessionLocal, Base, engine
from app.models.user_models import User
from datetime import datetime, timezone
import bcrypt
import uuid

def create_demo_user():
    """Create demo user if it doesn't exist"""
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Get database session
    db = get_sync_session()
    
    try:
        # Check if demo user exists
        existing_user = db.query(User).filter(User.username == "demo").first()
        
        if existing_user:
            print("✅ Demo user already exists")
            print(f"   Username: {existing_user.username}")
            print(f"   Email: {existing_user.email}")
            return
        
        # Create demo user
        demo_password = "demo123"
        hashed_password = bcrypt.hashpw(demo_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        demo_user = User(
            id=str(uuid.uuid4()),
            username="demo",
            email="demo@xionimus-ai.com",
            hashed_password=hashed_password,
            created_at=datetime.now(timezone.utc).isoformat(),
            is_active=True,
            role="user"
        )
        
        db.add(demo_user)
        db.commit()
        db.refresh(demo_user)
        
        print("✅ Demo user created successfully!")
        print(f"   Username: demo")
        print(f"   Password: demo123")
        print(f"   Email: demo@xionimus-ai.com")
        print(f"   User ID: {demo_user.id}")
        
    except Exception as e:
        print(f"❌ Error creating demo user: {e}")
        db.rollback()
        
    finally:
        db.close()

if __name__ == "__main__":
    print("🔧 Setting up demo user...")
    create_demo_user()