"""
Base Agent class for the Technical Documentation Suite
Built for the Google Cloud ADK Hackathon
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List, Optional
import uuid

@dataclass
class Message:
    """Message structure for inter-agent communication"""
    type: str
    data: Dict[str, Any]
    sender: str
    recipient: str
    timestamp: datetime = field(default_factory=datetime.now)
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))

class BaseAgent(ABC):
    """Base class for all agents in the Technical Documentation Suite"""
    
    def __init__(self, agent_id: str, name: str = None):
        self.agent_id = agent_id
        self.name = name or self.__class__.__name__
        self.message_queue = asyncio.Queue()
        self.is_running = False
        self.logger = logging.getLogger(f"agent.{self.name}")
        
        # Agent state
        self.state = "initialized"
        self.processed_messages = 0
        self.start_time = datetime.now()
        
        self.logger.info(f"Agent {self.name} ({self.agent_id}) initialized")
    
    async def start(self):
        """Start the agent's message processing loop"""
        self.is_running = True
        self.state = "running"
        self.logger.info(f"Agent {self.name} started")
        
        while self.is_running:
            try:
                # Wait for messages with timeout
                message = await asyncio.wait_for(
                    self.message_queue.get(), 
                    timeout=1.0
                )
                await self.handle_message(message)
                self.processed_messages += 1
                
            except asyncio.TimeoutError:
                # Continue running, just no messages to process
                continue
            except Exception as e:
                self.logger.error(f"Error processing message: {e}")
    
    async def stop(self):
        """Stop the agent"""
        self.is_running = False
        self.state = "stopped"
        self.logger.info(f"Agent {self.name} stopped")
    
    async def send_message(self, recipient_agent: 'BaseAgent', message_type: str, data: Dict[str, Any]):
        """Send a message to another agent"""
        message = Message(
            type=message_type,
            data=data,
            sender=self.agent_id,
            recipient=recipient_agent.agent_id
        )
        
        await recipient_agent.receive_message(message)
        self.logger.debug(f"Sent message {message_type} to {recipient_agent.name}")
        return message
    
    async def receive_message(self, message: Message):
        """Receive a message from another agent"""
        await self.message_queue.put(message)
        self.logger.debug(f"Received message {message.type} from {message.sender}")
    
    @abstractmethod
    async def handle_message(self, message: Message) -> Optional[Message]:
        """Handle incoming messages - must be implemented by subclasses"""
        pass
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status information"""
        uptime = datetime.now() - self.start_time
        
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "state": self.state,
            "is_running": self.is_running,
            "processed_messages": self.processed_messages,
            "uptime_seconds": uptime.total_seconds(),
            "queue_size": self.message_queue.qsize()
        }
    
    async def health_check(self) -> bool:
        """Check if agent is healthy"""
        return self.is_running and self.state == "running" 