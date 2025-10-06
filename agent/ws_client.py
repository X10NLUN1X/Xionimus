"""
WebSocket Client for Xionimus Agent
Connects to backend WebSocket endpoint and sends/receives messages
"""

import json
import asyncio
import logging
import websockets
from typing import Callable, Optional, Dict, Any
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class XionimusWebSocketClient:
    """WebSocket client for real-time communication with Xionimus backend"""
    
    def __init__(self, backend_url: str, agent_id: str):
        """
        Initialize WebSocket client
        
        Args:
            backend_url: Backend URL (e.g., http://localhost:8001)
            agent_id: Unique identifier for this agent instance
        """
        # Convert http/https to ws/wss
        ws_url = backend_url.replace('http://', 'ws://').replace('https://', 'wss://')
        self.ws_url = f"{ws_url}/api/ws/agent/{agent_id}"
        self.agent_id = agent_id
        
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.connected = False
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 10
        self.reconnect_delay = 5  # seconds
        
        # Callbacks
        self.on_message_callback: Optional[Callable] = None
        self.on_connect_callback: Optional[Callable] = None
        self.on_disconnect_callback: Optional[Callable] = None
        
    def on_message(self, callback: Callable[[Dict[Any, Any]], None]):
        """Register callback for incoming messages"""
        self.on_message_callback = callback
        
    def on_connect(self, callback: Callable[[], None]):
        """Register callback for connection established"""
        self.on_connect_callback = callback
        
    def on_disconnect(self, callback: Callable[[], None]):
        """Register callback for disconnection"""
        self.on_disconnect_callback = callback
    
    async def connect(self):
        """Establish WebSocket connection"""
        try:
            logger.info(f"Connecting to {self.ws_url}")
            self.websocket = await websockets.connect(
                self.ws_url,
                ping_interval=30,
                ping_timeout=10
            )
            self.connected = True
            self.reconnect_attempts = 0
            logger.info("✅ Connected to Xionimus backend")
            
            if self.on_connect_callback:
                self.on_connect_callback()
                
            # Start heartbeat
            asyncio.create_task(self._heartbeat())
            
            # Start message receiver
            asyncio.create_task(self._receive_messages())
            
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            self.connected = False
            await self._attempt_reconnect()
    
    async def disconnect(self):
        """Close WebSocket connection"""
        if self.websocket:
            await self.websocket.close()
            self.connected = False
            logger.info("Disconnected from backend")
            
            if self.on_disconnect_callback:
                self.on_disconnect_callback()
    
    async def send_file_event(self, event_type: str, file_path: str, content: Optional[str] = None):
        """
        Send file change event to backend
        
        Args:
            event_type: Type of event (created, modified, deleted)
            file_path: Windows path of the file
            content: Optional file content (for analysis)
        """
        if not self.connected or not self.websocket:
            logger.warning("Cannot send event: Not connected")
            return False
            
        message = {
            "type": "file_event",
            "agent_id": self.agent_id,
            "timestamp": datetime.now().isoformat(),
            "data": {
                "event_type": event_type,
                "file_path": file_path,
                "content": content
            }
        }
        
        try:
            await self.websocket.send(json.dumps(message))
            logger.debug(f"Sent file event: {event_type} - {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to send file event: {e}")
            self.connected = False
            await self._attempt_reconnect()
            return False
    
    async def _heartbeat(self):
        """Send periodic heartbeat to keep connection alive"""
        while self.connected:
            try:
                await asyncio.sleep(20)
                if self.websocket:
                    heartbeat = {
                        "type": "heartbeat",
                        "agent_id": self.agent_id,
                        "timestamp": datetime.now().isoformat()
                    }
                    await self.websocket.send(json.dumps(heartbeat))
                    logger.debug("Sent heartbeat")
            except Exception as e:
                logger.error(f"Heartbeat failed: {e}")
                self.connected = False
                break
    
    async def _receive_messages(self):
        """Receive and process messages from backend"""
        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    logger.debug(f"Received message: {data.get('type', 'unknown')}")
                    
                    if self.on_message_callback:
                        self.on_message_callback(data)
                        
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON received: {message}")
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.warning("Connection closed by server")
            self.connected = False
            await self._attempt_reconnect()
        except Exception as e:
            logger.error(f"Error in message receiver: {e}")
            self.connected = False
    
    async def _attempt_reconnect(self):
        """Attempt to reconnect with exponential backoff"""
        if self.reconnect_attempts >= self.max_reconnect_attempts:
            logger.error("Max reconnection attempts reached. Giving up.")
            return
            
        self.reconnect_attempts += 1
        wait_time = self.reconnect_delay * self.reconnect_attempts
        logger.info(f"Attempting reconnect in {wait_time} seconds (attempt {self.reconnect_attempts}/{self.max_reconnect_attempts})")
        
        await asyncio.sleep(wait_time)
        await self.connect()
    
    def is_connected(self) -> bool:
        """Check if connected to backend"""
        return self.connected


if __name__ == "__main__":
    # Test the WebSocket client
    async def test():
        def on_msg(data):
            print(f"Received: {data}")
            
        def on_conn():
            print("✅ Connected!")
            
        def on_disc():
            print("❌ Disconnected!")
        
        client = XionimusWebSocketClient("http://localhost:8001", "test-agent-123")
        client.on_message(on_msg)
        client.on_connect(on_conn)
        client.on_disconnect(on_disc)
        
        await client.connect()
        
        # Keep running
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            await client.disconnect()
    
    asyncio.run(test())
