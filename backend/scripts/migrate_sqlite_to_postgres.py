#!/usr/bin/env python3
"""
SQLite to PostgreSQL Migration Script
Migrates all data from SQLite to PostgreSQL while preserving relationships
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from app.models.user_models import User
from app.models.session_models import Session, Message
from app.models.agent_models import AgentConnection, AgentActivity
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database URLs
SQLITE_URL = f"sqlite:///{Path.home() / '.xionimus_ai' / 'xionimus.db'}"
POSTGRES_URL = os.environ.get("DATABASE_URL", "postgresql://xionimus:xionimus_secure_password@localhost:5432/xionimus_ai")

def migrate_data():
    """Migrate all data from SQLite to PostgreSQL"""
    
    logger.info("🚀 Starting migration from SQLite to PostgreSQL...")
    
    # Create engines
    sqlite_engine = create_engine(SQLITE_URL)
    postgres_engine = create_engine(POSTGRES_URL)
    
    # Create all tables in PostgreSQL first
    from app.core.database import Base
    logger.info("📋 Creating tables in PostgreSQL...")
    Base.metadata.create_all(bind=postgres_engine)
    logger.info("✅ Tables created successfully")
    
    # Create sessions
    SQLiteSession = sessionmaker(bind=sqlite_engine)
    PostgresSession = sessionmaker(bind=postgres_engine)
    
    sqlite_session = SQLiteSession()
    postgres_session = PostgresSession()
    
    try:
        # Check if SQLite database exists
        inspector = inspect(sqlite_engine)
        tables = inspector.get_table_names()
        
        if not tables:
            logger.warning("⚠️ No tables found in SQLite database. Nothing to migrate.")
            return
        
        logger.info(f"📊 Found {len(tables)} tables in SQLite: {tables}")
        
        # Migrate Users
        if 'users' in tables:
            users = sqlite_session.query(User).all()
            logger.info(f"👥 Migrating {len(users)} users...")
            for user in users:
                # Check if user already exists in PostgreSQL
                existing = postgres_session.query(User).filter_by(id=user.id).first()
                if not existing:
                    postgres_session.add(User(
                        id=user.id,
                        username=user.username,
                        email=user.email,
                        hashed_password=user.hashed_password,
                        created_at=user.created_at,
                        last_login=user.last_login,
                        is_active=user.is_active,
                        role=user.role,
                        github_token=getattr(user, 'github_token', None),
                        github_username=getattr(user, 'github_username', None)
                    ))
            postgres_session.commit()
            logger.info(f"✅ Users migrated successfully")
        
        # Migrate Sessions
        if 'sessions' in tables:
            sessions = sqlite_session.query(Session).all()
            logger.info(f"💬 Migrating {len(sessions)} sessions...")
            for session in sessions:
                existing = postgres_session.query(Session).filter_by(session_id=session.session_id).first()
                if not existing:
                    postgres_session.add(Session(
                        session_id=session.session_id,
                        user_id=session.user_id,
                        name=session.name,
                        description=getattr(session, 'description', None),
                        created_at=session.created_at,
                        updated_at=session.updated_at,
                        is_active=session.is_active,
                        session_type=getattr(session, 'session_type', 'chat'),
                        model_used=getattr(session, 'model_used', None),
                        total_tokens=getattr(session, 'total_tokens', 0),
                        active_project=getattr(session, 'active_project', None),
                        project_branch=getattr(session, 'project_branch', None)
                    ))
            postgres_session.commit()
            logger.info(f"✅ Sessions migrated successfully")
        
        # Migrate Messages
        if 'messages' in tables:
            messages = sqlite_session.query(Message).all()
            logger.info(f"📝 Migrating {len(messages)} messages...")
            for message in messages:
                existing = postgres_session.query(Message).filter_by(message_id=message.message_id).first()
                if not existing:
                    postgres_session.add(Message(
                        message_id=message.message_id,
                        session_id=message.session_id,
                        role=message.role,
                        content=message.content,
                        timestamp=message.timestamp,
                        provider=getattr(message, 'provider', None),
                        model=getattr(message, 'model', None),
                        prompt_tokens=getattr(message, 'prompt_tokens', 0),
                        completion_tokens=getattr(message, 'completion_tokens', 0),
                        total_tokens=getattr(message, 'total_tokens', 0),
                        message_metadata=getattr(message, 'message_metadata', None)
                    ))
            postgres_session.commit()
            logger.info(f"✅ Messages migrated successfully")
        
        # Skip Session Forks - model doesn't exist in current schema
        
        # Migrate Agent Connections (if exists)
        if 'agent_connections' in tables:
            connections = sqlite_session.query(AgentConnection).all()
            logger.info(f"🤖 Migrating {len(connections)} agent connections...")
            for conn in connections:
                existing = postgres_session.query(AgentConnection).filter_by(connection_id=conn.connection_id).first()
                if not existing:
                    postgres_session.add(AgentConnection(
                        connection_id=conn.connection_id,
                        agent_id=conn.agent_id,
                        status=conn.status,
                        connected_at=conn.connected_at,
                        last_ping=conn.last_ping,
                        config=getattr(conn, 'config', None)
                    ))
            postgres_session.commit()
            logger.info(f"✅ Agent connections migrated successfully")
        
        # Migrate Agent Activities (if exists)
        if 'agent_activities' in tables:
            activities = sqlite_session.query(AgentActivity).all()
            logger.info(f"📊 Migrating {len(activities)} agent activities...")
            for activity in activities:
                existing = postgres_session.query(AgentActivity).filter_by(activity_id=activity.activity_id).first()
                if not existing:
                    postgres_session.add(AgentActivity(
                        activity_id=activity.activity_id,
                        agent_id=activity.agent_id,
                        activity_type=activity.activity_type,
                        description=activity.description,
                        timestamp=activity.timestamp,
                        details=getattr(activity, 'details', None)
                    ))
            postgres_session.commit()
            logger.info(f"✅ Agent activities migrated successfully")
        
        logger.info("🎉 Migration completed successfully!")
        logger.info("📝 Summary:")
        logger.info(f"   - Users: {postgres_session.query(User).count()}")
        logger.info(f"   - Sessions: {postgres_session.query(Session).count()}")
        logger.info(f"   - Messages: {postgres_session.query(Message).count()}")
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        postgres_session.rollback()
        raise
    finally:
        sqlite_session.close()
        postgres_session.close()

if __name__ == "__main__":
    migrate_data()
