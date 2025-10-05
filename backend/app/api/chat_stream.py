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
from ..core.database import get_db_session as get_database

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
    # Check origin header for CORS (WebSocket doesn't use CORS middleware)
    # Note: WebSocket headers are case-sensitive, check both cases
    origin = websocket.headers.get("Origin", "") or websocket.headers.get("origin", "")
    logger.info(f"WebSocket connection attempt - Origin: '{origin}', Headers: {dict(websocket.headers)}")
    
    allowed_origins = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
        "http://127.0.0.1:5173",
    ]
    
    # Allow connections from allowed origins or when origin is empty (same-origin)
    if origin and origin not in allowed_origins:
        logger.warning(f"WebSocket connection rejected: Invalid origin '{origin}' not in {allowed_origins}")
        await websocket.close(code=1008, reason="Origin not allowed")
        return
    
    logger.info(f"WebSocket origin check passed for origin: '{origin}'")
    
    # Accept WebSocket connection
    try:
        await manager.connect(websocket, session_id)
    except Exception as e:
        logger.error(f"Failed to accept WebSocket: {e}")
        return
    
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
            
            # Debug logging for API keys
            logger.info(f"🔍 WebSocket received - Provider: {provider}, Model: {model}")
            logger.info(f"🔍 API keys received: {list(api_keys.keys())}")
            logger.info(f"🔍 API key for {provider}: {'✅ Present' if api_keys.get(provider) else '❌ Missing'}")
            
            # CRITICAL: Load active project context from session
            project_context = None
            db = get_database()
            try:
                from ..models.session_models import Session
                session_obj = db.query(Session).filter(Session.id == session_id).first()
                if session_obj and session_obj.active_project:
                    project_context = {
                        "project_name": session_obj.active_project,
                        "branch": session_obj.active_project_branch or "main",
                        "working_directory": f"/app/{session_obj.active_project}"
                    }
                    logger.info(f"✅ Active project loaded: {session_obj.active_project}")
                else:
                    logger.warning(f"⚠️ No active project set for session {session_id}")
            except Exception as e:
                logger.error(f"❌ Failed to load project context: {e}")
            finally:
                db.close()
            
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
                
                # Stream AI response
                full_response = ""
                chunk_count = 0
                
                # Pass api_keys and project_context to stream_response
                async for chunk in ai_manager.stream_response(
                    provider=provider,
                    model=model,
                    messages=conversation_history,
                    ultra_thinking=ultra_thinking,
                    api_keys=api_keys,
                    project_context=project_context
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
                # Get token usage stats
                from ..core.token_tracker import token_tracker
                token_stats = token_tracker.get_usage_stats()
                
                await manager.send_message({
                    "type": "complete",
                    "full_content": full_response,
                    "model": model,
                    "provider": provider,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "token_usage": token_stats  # NEW: Include token usage
                }, session_id)
                
                # Save to SQLite
                db = get_database()
                
                try:
                    from ..models.session_models import Message, Session
                    import uuid
                    
                    # Check if session exists, create if not
                    session = db.query(Session).filter(Session.id == session_id).first()
                    if not session:
                        # Create session if it doesn't exist
                        new_session = Session(
                            id=session_id,
                            name="Chat Session",
                            user_id=None  # Will be set later if authenticated
                        )
                        db.add(new_session)
                        db.commit()
                    
                    # Save user message
                    user_msg = Message(
                        id=f"msg_{uuid.uuid4().hex[:16]}",
                        session_id=session_id,
                        role="user",
                        content=user_message,
                        provider=provider,
                        model=model
                    )
                    db.add(user_msg)
                    
                    # Save assistant message
                    assistant_msg = Message(
                        id=f"msg_{uuid.uuid4().hex[:16]}",
                        session_id=session_id,
                        role="assistant",
                        content=full_response,
                        provider=provider,
                        model=model
                    )
                    db.add(assistant_msg)
                    
                    db.commit()
                    logger.info(f"✅ Messages saved to database")
                    
                except Exception as e:
                    logger.error(f"❌ Error saving messages to database: {e}")
                    db.rollback()
                finally:
                    if "db" in locals() and db is not None:
                        db.close()
                
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
