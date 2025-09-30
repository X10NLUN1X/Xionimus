"""
SQLite Database Manager for Local Sessions
Lightweight alternative to MongoDB for local usage
"""
import sqlite3
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# Database file location
DB_PATH = Path.home() / ".xionimus_ai" / "xionimus.db"
DB_PATH.parent.mkdir(exist_ok=True)


class SQLiteManager:
    """Manages SQLite database for local chat sessions"""
    
    def __init__(self):
        self.db_path = DB_PATH
        self._init_db()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def _init_db(self):
        """Initialize database schema"""
        # Force delete old database file if it exists with wrong schema
        if self.db_path.exists():
            try:
                # Try to detect old schema
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.cursor()
                cursor.execute("PRAGMA table_info(messages)")
                columns = [col[1] for col in cursor.fetchall()]
                conn.close()
                
                # If timestamp column doesn't exist, delete the old db
                if 'timestamp' not in columns and 'created_at' in columns:
                    self.db_path.unlink()
                    print(f"Deleted old database with incompatible schema")
            except:
                # If any error, just delete and recreate
                try:
                    self.db_path.unlink()
                except:
                    pass
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    workspace_id TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    metadata TEXT
                )
            """)
            
            # Messages table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    provider TEXT,
                    model TEXT,
                    usage TEXT,
                    parent_message_id TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE
                )
            """)
            
            # Settings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # Workspaces table (for L3.3)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS workspaces (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    path TEXT,
                    created_at TEXT NOT NULL,
                    metadata TEXT
                )
            """)
            
            # Indexes for performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_session 
                ON messages(session_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_messages_timestamp 
                ON messages(timestamp DESC)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_sessions_workspace 
                ON sessions(workspace_id)
            """)
            
            logger.info(f"✅ SQLite database initialized at {self.db_path}")
    
    # ==================== SESSIONS ====================
    
    def create_session(self, session_id: str, name: str = None, workspace_id: str = None) -> Dict[str, Any]:
        """Create a new chat session"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.now(timezone.utc).isoformat()
            
            cursor.execute("""
                INSERT INTO sessions (id, name, workspace_id, created_at, updated_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (session_id, name or "New Chat", workspace_id, now, now, "{}"))
            
            return {
                "id": session_id,
                "name": name or "New Chat",
                "workspace_id": workspace_id,
                "created_at": now,
                "updated_at": now,
                "message_count": 0
            }
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.*, COUNT(m.id) as message_count
                FROM sessions s
                LEFT JOIN messages m ON s.id = m.session_id
                WHERE s.id = ?
                GROUP BY s.id
            """, (session_id,))
            
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
    
    def list_sessions(self, workspace_id: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """List all sessions, optionally filtered by workspace"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if workspace_id:
                query = """
                    SELECT s.*, COUNT(m.id) as message_count
                    FROM sessions s
                    LEFT JOIN messages m ON s.id = m.session_id
                    WHERE s.workspace_id = ?
                    GROUP BY s.id
                    ORDER BY s.updated_at DESC
                    LIMIT ?
                """
                cursor.execute(query, (workspace_id, limit))
            else:
                query = """
                    SELECT s.*, COUNT(m.id) as message_count
                    FROM sessions s
                    LEFT JOIN messages m ON s.id = m.session_id
                    GROUP BY s.id
                    ORDER BY s.updated_at DESC
                    LIMIT ?
                """
                cursor.execute(query, (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def update_session(self, session_id: str, name: str = None, workspace_id: str = None):
        """Update session metadata"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.now(timezone.utc).isoformat()
            
            # Safe: updates list contains only hardcoded strings
            updates = ["updated_at = ?"]
            params = [now]
            
            if name is not None:
                updates.append("name = ?")
                params.append(name)
            
            if workspace_id is not None:
                updates.append("workspace_id = ?")
                params.append(workspace_id)
            
            params.append(session_id)
            
            # Build query safely - updates list is controlled, not user input
            query = f"UPDATE sessions SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
    
    def delete_session(self, session_id: str):
        """Delete session and all its messages"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
            cursor.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
            logger.info(f"✅ Deleted session {session_id}")
    
    # ==================== MESSAGES ====================
    
    def add_message(
        self, 
        message_id: str,
        session_id: str,
        role: str,
        content: str,
        provider: str = None,
        model: str = None,
        usage: Dict = None,
        parent_message_id: str = None
    ) -> Dict[str, Any]:
        """Add a message to a session"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.now(timezone.utc).isoformat()
            
            cursor.execute("""
                INSERT INTO messages 
                (id, session_id, role, content, timestamp, provider, model, usage, parent_message_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                message_id,
                session_id,
                role,
                content,
                now,
                provider,
                model,
                json.dumps(usage) if usage else None,
                parent_message_id
            ))
            
            # Update session timestamp
            cursor.execute("""
                UPDATE sessions SET updated_at = ? WHERE id = ?
            """, (now, session_id))
            
            return {
                "id": message_id,
                "session_id": session_id,
                "role": role,
                "content": content,
                "timestamp": now,
                "provider": provider,
                "model": model,
                "usage": usage
            }
    
    def get_messages(self, session_id: str, limit: int = None) -> List[Dict[str, Any]]:
        """Get all messages for a session"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            query = """
                SELECT * FROM messages 
                WHERE session_id = ?
                ORDER BY timestamp ASC
            """
            
            if limit:
                query += f" LIMIT {limit}"
            
            cursor.execute(query, (session_id,))
            
            messages = []
            for row in cursor.fetchall():
                msg = dict(row)
                if msg['usage']:
                    msg['usage'] = json.loads(msg['usage'])
                messages.append(msg)
            
            return messages
    
    def update_message(self, message_id: str, content: str):
        """Update message content (for edit feature)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE messages SET content = ? WHERE id = ?
            """, (content, message_id))
    
    def delete_message(self, message_id: str):
        """Delete a specific message"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM messages WHERE id = ?", (message_id,))
    
    def delete_messages_after(self, session_id: str, timestamp: str):
        """Delete all messages after a certain timestamp (for branch feature)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM messages 
                WHERE session_id = ? AND timestamp > ?
            """, (session_id, timestamp))
    
    # ==================== SETTINGS ====================
    
    def get_setting(self, key: str) -> Optional[str]:
        """Get a setting value"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row['value'] if row else None
    
    def set_setting(self, key: str, value: str):
        """Set a setting value"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.now(timezone.utc).isoformat()
            
            cursor.execute("""
                INSERT OR REPLACE INTO settings (key, value, updated_at)
                VALUES (?, ?, ?)
            """, (key, value, now))
    
    # ==================== WORKSPACES ====================
    
    def create_workspace(self, workspace_id: str, name: str, path: str = None) -> Dict[str, Any]:
        """Create a new workspace"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.now(timezone.utc).isoformat()
            
            cursor.execute("""
                INSERT INTO workspaces (id, name, path, created_at, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (workspace_id, name, path, now, "{}"))
            
            return {
                "id": workspace_id,
                "name": name,
                "path": path,
                "created_at": now
            }
    
    def list_workspaces(self) -> List[Dict[str, Any]]:
        """List all workspaces"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT w.*, COUNT(s.id) as session_count
                FROM workspaces w
                LEFT JOIN sessions s ON w.id = s.workspace_id
                GROUP BY w.id
                ORDER BY w.name
            """)
            return [dict(row) for row in cursor.fetchall()]
    
    # ==================== UTILITY ====================
    
    def get_db_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) as count FROM sessions")
            session_count = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM messages")
            message_count = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM workspaces")
            workspace_count = cursor.fetchone()['count']
            
            # Get database file size
            db_size = self.db_path.stat().st_size if self.db_path.exists() else 0
            
            return {
                "db_path": str(self.db_path),
                "db_size_mb": round(db_size / (1024 * 1024), 2),
                "sessions": session_count,
                "messages": message_count,
                "workspaces": workspace_count
            }
    
    def vacuum(self):
        """Optimize database (reclaim space after deletions)"""
        with self.get_connection() as conn:
            conn.execute("VACUUM")
            logger.info("✅ Database vacuumed")


# Global instance
_db_manager = None

def get_sqlite_db() -> SQLiteManager:
    """Get or create SQLite database manager instance"""
    global _db_manager
    if _db_manager is None:
        _db_manager = SQLiteManager()
    return _db_manager
