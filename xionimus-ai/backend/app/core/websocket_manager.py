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