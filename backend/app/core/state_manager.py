"""
State Manager for Autonomous Execution
Handles checkpointing, rollback, and action history
"""
from typing import Dict, Any, Optional, List
import os
import shutil
import json
import logging
from pathlib import Path
from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, String, DateTime, Text, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)

Base = declarative_base()

class Checkpoint(Base):
    """Database model for file checkpoints"""
    __tablename__ = "checkpoints"
    
    id = Column(String, primary_key=True)
    session_id = Column(String, index=True)
    file_path = Column(String)
    content_backup = Column(Text)
    action_type = Column(String)
    created_at = Column(DateTime)

class ActionLog(Base):
    """Database model for action history"""
    __tablename__ = "action_logs"
    
    id = Column(String, primary_key=True)
    session_id = Column(String, index=True)
    tool_name = Column(String)
    arguments = Column(Text)  # JSON string
    result = Column(Text)  # JSON string
    success = Column(Integer)  # SQLite doesn't have Boolean
    execution_time = Column(String)
    created_at = Column(DateTime)

class StateManager:
    """
    Manages state checkpoints and rollback for autonomous execution
    Supports both per-action and per-session rollback
    """
    
    def __init__(self, session_id: str, db_path: str = "~/.xionimus_ai/autonomous_state.db"):
        self.session_id = session_id
        
        # Setup database
        db_full_path = os.path.expanduser(db_path)
        os.makedirs(os.path.dirname(db_full_path), exist_ok=True)
        
        self.engine = create_engine(f"sqlite:///{db_full_path}", echo=False)
        Base.metadata.create_all(self.engine)
        
        Session = sessionmaker(bind=self.engine)
        self.db = Session()
        
        # In-memory cache for session start state
        self.session_start_state: Dict[str, str] = {}
        self.checkpoint_count = 0
        
        logger.info(f"✅ StateManager initialized for session: {session_id}")
    
    async def create_checkpoint(self, file_path: str, action_type: str) -> str:
        """
        Create a checkpoint before modifying a file
        Returns checkpoint ID
        """
        try:
            path = Path(file_path)
            
            # Read current content if file exists
            content_backup = ""
            if path.exists() and path.is_file():
                content_backup = path.read_text(encoding='utf-8')
            
            # Generate checkpoint ID
            checkpoint_id = f"cp_{self.session_id}_{self.checkpoint_count}_{int(datetime.now(timezone.utc).timestamp())}"
            self.checkpoint_count += 1
            
            # Save to database
            checkpoint = Checkpoint(
                id=checkpoint_id,
                session_id=self.session_id,
                file_path=file_path,
                content_backup=content_backup,
                action_type=action_type,
                created_at=datetime.now(timezone.utc)
            )
            self.db.add(checkpoint)
            self.db.commit()
            
            logger.info(f"📸 Checkpoint created: {checkpoint_id} for {file_path}")
            return checkpoint_id
            
        except Exception as e:
            logger.error(f"❌ Failed to create checkpoint: {e}")
            self.db.rollback()
            return ""
    
    async def log_action(self, tool_name: str, arguments: Dict[str, Any], result: Dict[str, Any]):
        """Log an autonomous action to history"""
        try:
            action_id = f"action_{self.session_id}_{int(datetime.now(timezone.utc).timestamp())}"
            
            action = ActionLog(
                id=action_id,
                session_id=self.session_id,
                tool_name=tool_name,
                arguments=json.dumps(arguments),
                result=json.dumps(result),
                success=1 if result.get("success") else 0,
                execution_time=str(result.get("execution_time", 0)),
                created_at=datetime.now(timezone.utc)
            )
            self.db.add(action)
            self.db.commit()
            
            logger.info(f"📝 Action logged: {tool_name}")
            
        except Exception as e:
            logger.error(f"❌ Failed to log action: {e}")
            self.db.rollback()
    
    async def rollback_last_action(self) -> Dict[str, Any]:
        """
        Rollback the last action (restore last checkpoint)
        Returns result dict with success status
        """
        try:
            # Get last checkpoint for this session
            last_checkpoint = self.db.query(Checkpoint).filter(
                Checkpoint.session_id == self.session_id
            ).order_by(Checkpoint.created_at.desc()).first()
            
            if not last_checkpoint:
                return {
                    "success": False,
                    "message": "No checkpoints found for this session"
                }
            
            # Restore file content
            path = Path(last_checkpoint.file_path)
            
            if last_checkpoint.content_backup:
                # Restore previous content
                path.write_text(last_checkpoint.content_backup, encoding='utf-8')
                message = f"✅ Restored {last_checkpoint.file_path} to previous state"
            else:
                # File didn't exist before, delete it
                if path.exists():
                    path.unlink()
                    message = f"✅ Deleted {last_checkpoint.file_path} (did not exist before)"
                else:
                    message = f"⚠️ File {last_checkpoint.file_path} already doesn't exist"
            
            # Delete checkpoint from database
            self.db.delete(last_checkpoint)
            self.db.commit()
            
            logger.info(f"↩️ Rollback complete: {last_checkpoint.file_path}")
            
            return {
                "success": True,
                "message": message,
                "file_path": last_checkpoint.file_path,
                "action_type": last_checkpoint.action_type
            }
            
        except Exception as e:
            logger.error(f"❌ Rollback failed: {e}")
            self.db.rollback()
            return {
                "success": False,
                "message": f"Rollback failed: {str(e)}"
            }
    
    async def rollback_session(self) -> Dict[str, Any]:
        """
        Rollback entire session (restore all checkpoints)
        Returns result dict with list of restored files
        """
        try:
            # Get all checkpoints for this session, ordered by creation time (oldest first)
            checkpoints = self.db.query(Checkpoint).filter(
                Checkpoint.session_id == self.session_id
            ).order_by(Checkpoint.created_at.asc()).all()
            
            if not checkpoints:
                return {
                    "success": False,
                    "message": "No checkpoints found for this session",
                    "restored_files": []
                }
            
            restored_files = []
            
            # Restore each checkpoint
            for checkpoint in checkpoints:
                try:
                    path = Path(checkpoint.file_path)
                    
                    if checkpoint.content_backup:
                        # Restore previous content
                        path.write_text(checkpoint.content_backup, encoding='utf-8')
                        restored_files.append(f"✅ {checkpoint.file_path}")
                    else:
                        # File didn't exist before, delete it
                        if path.exists():
                            path.unlink()
                            restored_files.append(f"🗑️ {checkpoint.file_path} (deleted)")
                
                except Exception as e:
                    restored_files.append(f"❌ {checkpoint.file_path} (failed: {str(e)})")
            
            # Delete all checkpoints for this session
            self.db.query(Checkpoint).filter(
                Checkpoint.session_id == self.session_id
            ).delete()
            self.db.commit()
            
            logger.info(f"↩️ Session rollback complete: {len(restored_files)} files")
            
            return {
                "success": True,
                "message": f"Session rollback complete: {len(restored_files)} files restored",
                "restored_files": restored_files
            }
            
        except Exception as e:
            logger.error(f"❌ Session rollback failed: {e}")
            self.db.rollback()
            return {
                "success": False,
                "message": f"Session rollback failed: {str(e)}",
                "restored_files": []
            }
    
    async def get_action_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get action history for this session"""
        try:
            actions = self.db.query(ActionLog).filter(
                ActionLog.session_id == self.session_id
            ).order_by(ActionLog.created_at.desc()).limit(limit).all()
            
            history = []
            for action in actions:
                history.append({
                    "id": action.id,
                    "tool_name": action.tool_name,
                    "arguments": json.loads(action.arguments),
                    "result": json.loads(action.result),
                    "success": bool(action.success),
                    "execution_time": action.execution_time,
                    "created_at": action.created_at.isoformat()
                })
            
            return history
            
        except Exception as e:
            logger.error(f"❌ Failed to get action history: {e}")
            return []
    
    async def get_checkpoint_count(self) -> int:
        """Get number of checkpoints for this session"""
        try:
            count = self.db.query(Checkpoint).filter(
                Checkpoint.session_id == self.session_id
            ).count()
            return count
        except Exception as e:
            logger.error(f"❌ Failed to get checkpoint count: {e}")
            return 0
    
    def close(self):
        """Close database connection"""
        try:
            self.db.close()
            logger.info(f"✅ StateManager closed for session: {self.session_id}")
        except Exception as e:
            logger.error(f"❌ Failed to close StateManager: {e}")