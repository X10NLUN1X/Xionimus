from fastapi import WebSocket
import json
import logging
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class MessageType(str, Enum):
    """WebSocket message types"""
    CHAT_MESSAGE = "chat_message"
    CODE_GENERATED = "code_generated"
    FILE_WRITTEN = "file_written"
    TEST_STARTED = "test_started"
    TEST_COMPLETED = "test_completed"
    SERVICE_STATUS = "service_status"
    ERROR = "error"
    PROGRESS = "progress"

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        """Connect a WebSocket to a session"""
        await websocket.accept()
        
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []
        
        self.active_connections[session_id].append(websocket)
        logger.info(f"🔗 WebSocket connected to session {session_id}")
    
    def disconnect(self, websocket: WebSocket, session_id: str):
        """Disconnect a WebSocket from a session"""
        if session_id in self.active_connections:
            if websocket in self.active_connections[session_id]:
                self.active_connections[session_id].remove(websocket)
            
            # Clean up empty sessions
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]
        
        logger.info(f"🔌 WebSocket disconnected from session {session_id}")
    
    async def broadcast_to_session(self, session_id: str, message: dict):
        """Broadcast message to all connections in a session"""
        if session_id in self.active_connections:
            for connection in self.active_connections[session_id]:
                try:
                    await connection.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"Failed to send message to WebSocket: {e}")
    
    async def send_to_connection(self, websocket: WebSocket, message: dict):
        """Send message to specific WebSocket connection"""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Failed to send message to WebSocket: {e}")
    
    async def send_progress_update(
        self, 
        session_id: str,
        message: str,
        progress: float,
        details: Optional[Dict[str, Any]] = None
    ):
        """Send progress update to session"""
        await self.broadcast_to_session(session_id, {
            'type': MessageType.PROGRESS,
            'message': message,
            'progress': progress,
            'details': details or {},
            'timestamp': datetime.now().isoformat()
        })
    
    async def send_code_generated(
        self,
        session_id: str,
        file_path: str,
        language: str
    ):
        """Notify that code was generated"""
        await self.broadcast_to_session(session_id, {
            'type': MessageType.CODE_GENERATED,
            'file_path': file_path,
            'language': language,
            'timestamp': datetime.now().isoformat()
        })
    
    async def send_file_written(
        self,
        session_id: str,
        file_path: str,
        size: int
    ):
        """Notify that file was written"""
        await self.broadcast_to_session(session_id, {
            'type': MessageType.FILE_WRITTEN,
            'file_path': file_path,
            'size': size,
            'timestamp': datetime.now().isoformat()
        })
    
    async def send_test_update(
        self,
        session_id: str,
        test_type: str,
        status: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """Send test status update"""
        message_type = MessageType.TEST_STARTED if status == 'started' else MessageType.TEST_COMPLETED
        
        await self.broadcast_to_session(session_id, {
            'type': message_type,
            'test_type': test_type,
            'status': status,
            'details': details or {},
            'timestamp': datetime.now().isoformat()
        })
    
    async def send_service_status(
        self,
        session_id: str,
        service: str,
        status: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """Send service status update"""
        await self.broadcast_to_session(session_id, {
            'type': MessageType.SERVICE_STATUS,
            'service': service,
            'status': status,
            'details': details or {},
            'timestamp': datetime.now().isoformat()
        })
    
    async def send_error(
        self,
        session_id: str,
        error_message: str,
        error_type: Optional[str] = None
    ):
        """Send error message"""
        await self.broadcast_to_session(session_id, {
            'type': MessageType.ERROR,
            'error': error_message,
            'error_type': error_type,
            'timestamp': datetime.now().isoformat()
        })
    
    def get_active_sessions(self) -> List[str]:
        """Get list of active session IDs"""
        return list(self.active_connections.keys())
    
    def get_connection_count(self, session_id: Optional[str] = None) -> int:
        """Get connection count for session or all sessions"""
        if session_id:
            return len(self.active_connections.get(session_id, []))
        return sum(len(conns) for conns in self.active_connections.values())
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get WebSocket statistics"""
        return {
            'total_sessions': len(self.active_connections),
            'total_connections': self.get_connection_count(),
            'active_sessions': self.get_active_sessions(),
            'timestamp': datetime.now().isoformat()
        }