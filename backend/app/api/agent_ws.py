"""
Agent WebSocket Endpoint
Handles WebSocket connections from local Xionimus agents
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends
from sqlalchemy.orm import Session

from ..core.database import get_db_session
from ..models.agent_models import AgentConnection, AgentActivity

logger = logging.getLogger(__name__)

router = APIRouter()

# Connected agents tracking
connected_agents: Dict[str, WebSocket] = {}


class AgentConnectionManager:
    """Manages WebSocket connections from agents"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        
    async def connect(self, agent_id: str, websocket: WebSocket):
        """Register new agent connection"""
        await websocket.accept()
        self.active_connections[agent_id] = websocket
        logger.info(f"Agent connected: {agent_id}")
        
    def disconnect(self, agent_id: str):
        """Remove agent connection"""
        if agent_id in self.active_connections:
            del self.active_connections[agent_id]
            logger.info(f"Agent disconnected: {agent_id}")
            
    async def send_message(self, agent_id: str, message: dict):
        """Send message to specific agent"""
        if agent_id in self.active_connections:
            try:
                await self.active_connections[agent_id].send_json(message)
                return True
            except Exception as e:
                logger.error(f"Failed to send message to agent {agent_id}: {e}")
                return False
        return False
        
    async def broadcast(self, message: dict):
        """Broadcast message to all connected agents"""
        for agent_id, websocket in list(self.active_connections.items()):
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Failed to broadcast to agent {agent_id}: {e}")
                
    def get_connected_agents(self) -> Set[str]:
        """Get list of connected agent IDs"""
        return set(self.active_connections.keys())
        
    def is_connected(self, agent_id: str) -> bool:
        """Check if agent is connected"""
        return agent_id in self.active_connections


# Global connection manager
manager = AgentConnectionManager()


@router.websocket("/ws/agent/{agent_id}")
async def agent_websocket_endpoint(
    websocket: WebSocket,
    agent_id: str,
    db: Session = Depends(get_db_session)
):
    """
    WebSocket endpoint for agent connections
    Receives file events and sends analysis results
    """
    await manager.connect(agent_id, websocket)
    
    # Record connection in database
    try:
        connection = AgentConnection(
            agent_id=agent_id,
            connected_at=datetime.now(),
            status="connected"
        )
        db.add(connection)
        db.commit()
    except Exception as e:
        logger.error(f"Failed to record agent connection: {e}")
    
    try:
        # Send welcome message
        await websocket.send_json({
            "type": "welcome",
            "agent_id": agent_id,
            "message": "Connected to Xionimus backend",
            "timestamp": datetime.now().isoformat()
        })
        
        # Message loop
        while True:
            try:
                # Receive message from agent
                data = await websocket.receive_text()
                message = json.loads(data)
                
                msg_type = message.get('type', 'unknown')
                logger.debug(f"Received {msg_type} from agent {agent_id}")
                
                # Handle different message types
                if msg_type == 'file_event':
                    await handle_file_event(agent_id, message, websocket, db)
                elif msg_type == 'heartbeat':
                    await handle_heartbeat(agent_id, message, websocket)
                elif msg_type == 'ping':
                    await websocket.send_json({"type": "pong"})
                else:
                    logger.warning(f"Unknown message type from agent {agent_id}: {msg_type}")
                    
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON from agent {agent_id}")
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON format"
                })
                
    except WebSocketDisconnect:
        logger.info(f"Agent {agent_id} disconnected normally")
    except Exception as e:
        logger.error(f"Error in agent WebSocket for {agent_id}: {e}")
    finally:
        manager.disconnect(agent_id)
        
        # Update connection status in database
        try:
            connection = db.query(AgentConnection).filter(
                AgentConnection.agent_id == agent_id
            ).order_by(AgentConnection.connected_at.desc()).first()
            
            if connection:
                connection.status = "disconnected"
                connection.disconnected_at = datetime.now()
                db.commit()
        except Exception as e:
            logger.error(f"Failed to update agent disconnection: {e}")


async def handle_file_event(
    agent_id: str,
    message: dict,
    websocket: WebSocket,
    db: Session
):
    """Handle file change events from agent"""
    data = message.get('data', {})
    event_type = data.get('event_type')
    file_path = data.get('file_path')
    content = data.get('content')
    
    logger.info(f"File {event_type}: {file_path} from agent {agent_id}")
    
    # Record activity
    try:
        activity = AgentActivity(
            agent_id=agent_id,
            activity_type="file_event",
            file_path=file_path,
            event_type=event_type,
            timestamp=datetime.now()
        )
        db.add(activity)
        db.commit()
    except Exception as e:
        logger.error(f"Failed to record agent activity: {e}")
    
    # Analyze file if content provided
    if content and event_type != 'deleted':
        analysis_result = await analyze_code(file_path, content)
        
        # Send analysis result back to agent
        await websocket.send_json({
            "type": "analysis_result",
            "data": {
                "file_path": file_path,
                "issues": analysis_result.get('issues', []),
                "suggestions": analysis_result.get('suggestions', []),
                "timestamp": datetime.now().isoformat()
            }
        })


async def handle_heartbeat(agent_id: str, message: dict, websocket: WebSocket):
    """Handle heartbeat from agent"""
    logger.debug(f"Heartbeat from agent {agent_id}")
    
    # Send acknowledgment
    await websocket.send_json({
        "type": "heartbeat_ack",
        "timestamp": datetime.now().isoformat()
    })


async def analyze_code(file_path: str, content: str) -> dict:
    """
    Analyze code using AI
    
    Args:
        file_path: Path to the file
        content: File content
        
    Returns:
        Dictionary with analysis results
    """
    # Check if API keys are configured
    claude_key = os.getenv('CLAUDE_API_KEY')
    if not claude_key:
        logger.warning("Claude API key not configured")
        return {
            "issues": [],
            "suggestions": [],
            "error": "AI analysis not available - API key not configured"
        }
    
    try:
        # Import Claude client
        from anthropic import Anthropic
        
        client = Anthropic(api_key=claude_key)
        
        # Determine file type
        file_extension = file_path.split('.')[-1].lower()
        language_map = {
            'py': 'Python',
            'js': 'JavaScript',
            'jsx': 'JavaScript React',
            'ts': 'TypeScript',
            'tsx': 'TypeScript React',
            'html': 'HTML',
            'css': 'CSS',
            'json': 'JSON',
            'md': 'Markdown'
        }
        language = language_map.get(file_extension, 'code')
        
        # Create analysis prompt
        prompt = f"""Analyze this {language} code and provide:
1. Any bugs or potential issues
2. Code quality improvements
3. Performance optimizations
4. Security concerns

Format your response as JSON with structure:
{{
  "issues": [
    {{"severity": "error|warning|info", "line": number, "message": "description"}}
  ],
  "suggestions": [
    {{"type": "improvement|optimization|security", "message": "description"}}
  ]
}}

Code:
```{language}
{content}
```"""
        
        # Call Claude Sonnet 4.5 for analysis
        response = client.messages.create(
            model="claude-sonnet-4.5-20250514",
            max_tokens=2000,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        # Parse response
        result_text = response.content[0].text
        
        # Try to extract JSON from response
        import re
        json_match = re.search(r'```json\n(.*?)\n```', result_text, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group(1))
        else:
            # Try to parse entire response as JSON
            result = json.loads(result_text)
            
        return result
        
    except Exception as e:
        logger.error(f"Code analysis failed: {e}")
        return {
            "issues": [],
            "suggestions": [],
            "error": str(e)
        }


@router.get("/agent/status")
async def get_agent_status():
    """Get status of all connected agents"""
    connected = manager.get_connected_agents()
    return {
        "connected_agents": list(connected),
        "count": len(connected),
        "timestamp": datetime.now().isoformat()
    }


@router.post("/agent/{agent_id}/send")
async def send_to_agent(agent_id: str, message: dict):
    """Send message to specific agent"""
    success = await manager.send_message(agent_id, message)
    if not success:
        raise HTTPException(status_code=404, detail="Agent not connected")
    return {"success": True}
