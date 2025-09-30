"""
Streaming Chat API with WebSocket
Real-time AI response streaming for better UX
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from typing import Dict, Set
import json
import asyncio
import logging
from datetime import datetime, timezone

from ..core.ai_manager import AIManager
from ..core.database_sqlite import get_sqlite_db

logger = logging.getLogger(__name__)
router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections for streaming"""
    
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        """Accept and store WebSocket connection"""
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = set()
        self.active_connections[session_id].add(websocket)
        logger.info(f"✅ WebSocket connected: {session_id}")
    
    def disconnect(self, websocket: WebSocket, session_id: str):
        """Remove WebSocket connection"""
        if session_id in self.active_connections:
            self.active_connections[session_id].discard(websocket)
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]
        logger.info(f"❌ WebSocket disconnected: {session_id}")
    
    async def send_message(self, message: dict, session_id: str):
        """Send message to all connections in a session"""
        if session_id in self.active_connections:
            disconnected = set()
            for connection in self.active_connections[session_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending message: {e}")
                    disconnected.add(connection)
            
            # Clean up disconnected sockets
            for conn in disconnected:
                self.disconnect(conn, session_id)


# Global connection manager
manager = ConnectionManager()


@router.websocket("/ws/chat/{session_id}")
async def websocket_chat_endpoint(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for streaming chat
    
    Expected message format:
    {
        "type": "chat",
        "content": "user message",
        "provider": "anthropic",
        "model": "claude-sonnet-4",
        "ultra_thinking": false,
        "api_keys": {...}
    }
    """
    await manager.connect(websocket, session_id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data.get("type") == "ping":
                # Heartbeat
                await websocket.send_json({"type": "pong"})
                continue
            
            if message_data.get("type") != "chat":
                continue
            
            # Extract message details
            user_message = message_data.get("content", "")
            provider = message_data.get("provider", "openai")
            model = message_data.get("model", "gpt-5")
            ultra_thinking = message_data.get("ultra_thinking", False)
            api_keys = message_data.get("api_keys", {})
            conversation_history = message_data.get("messages", [])
            
            # Add user message to history
            conversation_history.append({
                "role": "user",
                "content": user_message
            })
            
            # Send acknowledgment
            await manager.send_message({
                "type": "start",
                "session_id": session_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }, session_id)
            
            try:
                # Initialize AI Manager
                ai_manager = AIManager()
                
                # Configure API keys if provided
                if api_keys:
                    for key, value in api_keys.items():
                        if value and value.strip():
                            setattr(ai_manager, f"{key}_api_key", value)
                
                # Stream AI response
                full_response = ""
                chunk_count = 0
                
                async for chunk in ai_manager.stream_response(
                    provider=provider,
                    model=model,
                    messages=conversation_history,
                    ultra_thinking=ultra_thinking
                ):
                    chunk_count += 1
                    chunk_text = chunk.get("content", "")
                    full_response += chunk_text
                    
                    # Send chunk to client
                    await manager.send_message({
                        "type": "chunk",
                        "content": chunk_text,
                        "chunk_id": chunk_count
                    }, session_id)
                    
                    # Small delay to prevent overwhelming client
                    await asyncio.sleep(0.01)
                
                # Send completion message
                await manager.send_message({
                    "type": "complete",
                    "full_content": full_response,
                    "model": model,
                    "provider": provider,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }, session_id)
                
                # Save to SQLite
                db = get_sqlite_db()
                
                # Save user message
                db.add_message(
                    message_id=f"msg_{datetime.now().timestamp()}",
                    session_id=session_id,
                    role="user",
                    content=user_message,
                    provider=provider,
                    model=model
                )
                
                # Save assistant message
                db.add_message(
                    message_id=f"msg_{datetime.now().timestamp()}_assistant",
                    session_id=session_id,
                    role="assistant",
                    content=full_response,
                    provider=provider,
                    model=model
                )
                
                logger.info(f"✅ Streaming complete: {chunk_count} chunks, {len(full_response)} chars")
                
            except ValueError as e:
                # Handle configuration errors (missing API keys)
                error_message = str(e)
                logger.warning(f"⚠️ Configuration error: {error_message}")
                
                # Send user-friendly error message
                await manager.send_message({
                    "type": "error",
                    "message": "⚠️ API Key Not Configured",
                    "details": f"{error_message}\n\n📝 Please configure your API keys:\n1. Click on Settings (⚙️)\n2. Scroll to 'AI Provider API Keys'\n3. Add your API key for {provider}\n4. Click 'Save API Keys'\n5. Return to chat and try again",
                    "action_required": "configure_api_keys",
                    "provider": provider,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }, session_id)
                
            except Exception as e:
                logger.error(f"Streaming error: {e}")
                await manager.send_message({
                    "type": "error",
                    "message": "An error occurred while processing your message",
                    "details": str(e),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }, session_id)
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, session_id)
        logger.info(f"Client disconnected: {session_id}")
    
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket, session_id)


@router.get("/stream/status")
async def get_stream_status():
    """Get streaming service status"""
    return {
        "status": "active",
        "active_sessions": len(manager.active_connections),
        "total_connections": sum(len(conns) for conns in manager.active_connections.values())
    }
