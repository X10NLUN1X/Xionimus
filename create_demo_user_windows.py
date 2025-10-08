"""
Script zum Erstellen des Demo-Users für Windows
Führen Sie dies im backend-Verzeichnis aus:
python create_demo_user_windows.py
"""
import sys
sys.path.insert(0, '.')

from app.models.user_models import User
from app.core.database import engine, DATABASE_PATH, Base
from sqlalchemy.orm import Session
import bcrypt

print("=" * 60)
print("DEMO USER CREATION FOR WINDOWS")
print("=" * 60)

# Create tables
Base.metadata.create_all(bind=engine)
print(f"\n✅ Tables created")
print(f"📁 Database: {DATABASE_PATH}")

with Session(engine) as session:
    # Check if demo user exists
    demo_user = session.query(User).filter(User.username == "demo").first()
    
    if demo_user:
        print("\n⚠️  Demo user already exists!")
        print(f"   Username: {demo_user.username}")
        print(f"   Email: {demo_user.email}")
        print(f"   Active: {demo_user.is_active}")
        
        # Update password to be sure
        response = input("\nPassword auf 'demo123' zurücksetzen? (y/n): ")
        if response.lower() == 'y':
            hashed_password = bcrypt.hashpw("demo123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            demo_user.hashed_password = hashed_password
            session.commit()
            print("✅ Password zurückgesetzt!")
    else:
        # Create demo user
        print("\n🔧 Erstelle Demo-User...")
        hashed_password = bcrypt.hashpw("demo123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        demo_user = User(
            username="demo",
            email="demo@xionimus.ai",
            hashed_password=hashed_password,
            role="user",
            is_active=True
        )
        
        session.add(demo_user)
        session.commit()
        
        print("✅ Demo user erstellt!")
        print(f"   Username: demo")
        print(f"   Password: demo123")
        print(f"   Email: demo@xionimus.ai")

print("\n" + "=" * 60)
print("FERTIG!")
print("=" * 60)
print("\nSie können sich jetzt einloggen mit:")
print("  Username: demo")
print("  Password: demo123")
