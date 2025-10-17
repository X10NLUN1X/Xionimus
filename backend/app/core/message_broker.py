"""
Message Broker System for Inter-Agent Communication
Enables agents to communicate, share context, and coordinate tasks

Location: /backend/app/core/message_broker.py
"""
import asyncio
import logging
from typing import Dict, List, Any, Optional, Callable, AsyncGenerator
from datetime import datetime, timezone
from enum import Enum
from dataclasses import dataclass, field
from uuid import uuid4
from collections import defaultdict

logger = logging.getLogger(__name__)


class MessageType(Enum):
    """Types of messages agents can send"""
    REQUEST = "request"          # Request information from another agent
    RESPONSE = "response"        # Response to a request
    NOTIFICATION = "notification"  # Notify other agents of an event
    ERROR = "error"              # Error notification
    STATUS_UPDATE = "status_update"  # Progress/status update
    ARTIFACT = "artifact"        # Share artifact (code, data, etc.)


class MessagePriority(Enum):
    """Message priority levels"""
    LOW = 1
    NORMAL = 5
    HIGH = 8
    CRITICAL = 10


@dataclass
class Message:
    """Message object for agent communication"""
    message_id: str = field(default_factory=lambda: str(uuid4()))
    from_agent: str = None  # AgentType.value
    to_agent: Optional[str] = None  # AgentType.value, None = broadcast
    message_type: MessageType = MessageType.NOTIFICATION
    priority: MessagePriority = MessagePriority.NORMAL
    content: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    response_to: Optional[str] = None  # Message ID this responds to
    execution_id: Optional[str] = None  # Link to orchestrator execution
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "message_id": self.message_id,
            "from_agent": self.from_agent,
            "to_agent": self.to_agent,
            "message_type": self.message_type.value,
            "priority": self.priority.value,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "response_to": self.response_to,
            "execution_id": self.execution_id
        }


class MessageBroker:
    """
    Central message broker for agent communication
    Handles message routing, subscriptions, and request-response patterns
    """
    
    def __init__(self):
        # Agent mailboxes - each agent has an inbox
        self._mailboxes: Dict[str, asyncio.Queue] = defaultdict(asyncio.Queue)
        
        # Subscribers - agents that want to receive certain message types
        self._subscribers: Dict[MessageType, List[str]] = defaultdict(list)
        
        # Response waiters - for request-response pattern
        self._response_waiters: Dict[str, asyncio.Future] = {}
        
        # Message history for debugging
        self._message_history: List[Message] = []
        self._max_history = 1000
        
        # Statistics
        self._stats = {
            "total_messages": 0,
            "messages_by_type": defaultdict(int),
            "messages_by_agent": defaultdict(int)
        }
        
        logger.info("🔄 Message Broker initialized")
    
    async def publish(self, message: Message) -> None:
        """
        Publish a message to the broker
        Routes to specific agent or broadcasts
        """
        # Update statistics
        self._stats["total_messages"] += 1
        self._stats["messages_by_type"][message.message_type.value] += 1
        self._stats["messages_by_agent"][message.from_agent] += 1
        
        # Add to history
        self._message_history.append(message)
        if len(self._message_history) > self._max_history:
            self._message_history.pop(0)
        
        logger.info(
            f"📤 Message published: {message.message_type.value} "
            f"from {message.from_agent} to {message.to_agent or 'ALL'}"
        )
        
        # If it's a response, notify the waiter
        if message.message_type == MessageType.RESPONSE and message.response_to:
            if message.response_to in self._response_waiters:
                future = self._response_waiters.pop(message.response_to)
                if not future.done():
                    future.set_result(message)
        
        # Route message
        if message.to_agent:
            # Direct message to specific agent
            await self._mailboxes[message.to_agent].put(message)
        else:
            # Broadcast to all subscribers
            for agent in self._subscribers.get(message.message_type, []):
                if agent != message.from_agent:  # Don't send back to sender
                    await self._mailboxes[agent].put(message)
    
    async def subscribe(self, agent_type: str, message_types: List[MessageType]) -> None:
        """
        Subscribe an agent to specific message types
        Agent will receive all messages of these types
        """
        for msg_type in message_types:
            if agent_type not in self._subscribers[msg_type]:
                self._subscribers[msg_type].append(agent_type)
        
        logger.info(
            f"📬 Agent {agent_type} subscribed to "
            f"{[mt.value for mt in message_types]}"
        )
    
    async def unsubscribe(self, agent_type: str, message_types: List[MessageType]) -> None:
        """Unsubscribe agent from message types"""
        for msg_type in message_types:
            if agent_type in self._subscribers[msg_type]:
                self._subscribers[msg_type].remove(agent_type)
        
        logger.info(
            f"📭 Agent {agent_type} unsubscribed from "
            f"{[mt.value for mt in message_types]}"
        )
    
    async def get_messages(
        self,
        agent_type: str,
        timeout: Optional[float] = None
    ) -> AsyncGenerator[Message, None]:
        """
        Get messages for an agent (async generator)
        Yields messages as they arrive
        """
        mailbox = self._mailboxes[agent_type]
        
        while True:
            try:
                if timeout:
                    message = await asyncio.wait_for(
                        mailbox.get(),
                        timeout=timeout
                    )
                else:
                    message = await mailbox.get()
                
                yield message
                
            except asyncio.TimeoutError:
                break
            except Exception as e:
                logger.error(f"Error getting messages for {agent_type}: {e}")
                break
    
    async def get_next_message(
        self,
        agent_type: str,
        timeout: float = 1.0
    ) -> Optional[Message]:
        """
        Get next message for agent (synchronous style)
        Returns None if no message within timeout
        """
        try:
            mailbox = self._mailboxes[agent_type]
            message = await asyncio.wait_for(mailbox.get(), timeout=timeout)
            return message
        except asyncio.TimeoutError:
            return None
        except Exception as e:
            logger.error(f"Error getting next message: {e}")
            return None
    
    async def request_response(
        self,
        from_agent: str,
        to_agent: str,
        request_content: Dict[str, Any],
        timeout: float = 30.0,
        priority: MessagePriority = MessagePriority.NORMAL
    ) -> Optional[Message]:
        """
        Send a request and wait for response
        Returns response message or None if timeout
        """
        # Create request message
        request = Message(
            from_agent=from_agent,
            to_agent=to_agent,
            message_type=MessageType.REQUEST,
            priority=priority,
            content=request_content
        )
        
        # Create future for response
        response_future = asyncio.Future()
        self._response_waiters[request.message_id] = response_future
        
        # Send request
        await self.publish(request)
        
        # Wait for response
        try:
            response = await asyncio.wait_for(response_future, timeout=timeout)
            logger.info(
                f"✅ Got response from {to_agent} to {from_agent} "
                f"in {(datetime.now(timezone.utc) - request.timestamp).total_seconds():.2f}s"
            )
            return response
        except asyncio.TimeoutError:
            logger.warning(
                f"⏱️ Request timeout: {from_agent} -> {to_agent} "
                f"(waited {timeout}s)"
            )
            # Clean up waiter
            self._response_waiters.pop(request.message_id, None)
            return None
        except Exception as e:
            logger.error(f"Error in request-response: {e}")
            self._response_waiters.pop(request.message_id, None)
            return None
    
    async def send_response(
        self,
        to_agent: str,
        request_message_id: str,
        response_content: Dict[str, Any],
        from_agent: str
    ) -> None:
        """
        Send a response to a previous request
        """
        response = Message(
            from_agent=from_agent,
            to_agent=to_agent,
            message_type=MessageType.RESPONSE,
            priority=MessagePriority.HIGH,
            content=response_content,
            response_to=request_message_id
        )
        
        await self.publish(response)
    
    def get_mailbox_size(self, agent_type: str) -> int:
        """Get number of pending messages for agent"""
        return self._mailboxes[agent_type].qsize()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get broker statistics"""
        return {
            "total_messages": self._stats["total_messages"],
            "messages_by_type": dict(self._stats["messages_by_type"]),
            "messages_by_agent": dict(self._stats["messages_by_agent"]),
            "mailbox_sizes": {
                agent: queue.qsize() 
                for agent, queue in self._mailboxes.items()
            },
            "active_subscribers": {
                msg_type.value: len(agents)
                for msg_type, agents in self._subscribers.items()
            }
        }
    
    def get_message_history(
        self,
        agent: Optional[str] = None,
        message_type: Optional[MessageType] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get message history with optional filters
        """
        filtered = self._message_history
        
        # Filter by agent
        if agent:
            filtered = [
                msg for msg in filtered
                if msg.from_agent == agent or msg.to_agent == agent
            ]
        
        # Filter by type
        if message_type:
            filtered = [
                msg for msg in filtered
                if msg.message_type == message_type
            ]
        
        # Limit results
        filtered = filtered[-limit:]
        
        return [msg.to_dict() for msg in filtered]
    
    async def clear_mailbox(self, agent_type: str) -> int:
        """Clear all messages in agent's mailbox, return count cleared"""
        count = 0
        mailbox = self._mailboxes[agent_type]
        
        while not mailbox.empty():
            try:
                mailbox.get_nowait()
                count += 1
            except asyncio.QueueEmpty:
                break
        
        logger.info(f"🧹 Cleared {count} messages from {agent_type} mailbox")
        return count
    
    def reset(self) -> None:
        """Reset broker (for testing)"""
        self._mailboxes.clear()
        self._subscribers.clear()
        self._response_waiters.clear()
        self._message_history.clear()
        self._stats = {
            "total_messages": 0,
            "messages_by_type": defaultdict(int),
            "messages_by_agent": defaultdict(int)
        }
        logger.info("🔄 Message Broker reset")


# Global broker instance
_broker: Optional[MessageBroker] = None


def get_message_broker() -> MessageBroker:
    """Get or create global message broker instance"""
    global _broker
    if _broker is None:
        _broker = MessageBroker()
    return _broker


def reset_message_broker() -> None:
    """Reset global broker (for testing)"""
    global _broker
    if _broker:
        _broker.reset()
    _broker = None
