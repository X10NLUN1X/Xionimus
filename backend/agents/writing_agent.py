from .base_agent import BaseAgent, AgentCapability
from typing import Dict, Any
import anthropic
import os
import logging

class WritingAgent(BaseAgent):
    """Agent specialized in writing tasks"""
    
    def __init__(self):
        super().__init__(
            name="Writing Agent", 
            description="Writing",
            capabilities=[
                AgentCapability.WRITING,
                AgentCapability.CONTENT_CREATION,
                AgentCapability.DOCUMENTATION
            ]
        )
        self.client = None
        self.ai_model = "claude"
        
    async def _get_client(self):
        """Get or create Anthropic client"""
        if self.client is None:
            api_key = os.environ.get('ANTHROPIC_API_KEY')
            if api_key:
                self.client = anthropic.AsyncAnthropic(api_key=api_key)
        return self.client
    
    def can_handle_task(self, message: str, context: Dict[str, Any] = None) -> float:
        """Determine if this agent can handle the task"""
        writing_keywords = [
            "write", "essay", "article", "blog", "content", "story", 
            "documentation", "report", "proposal", "letter", "email",
            "creative", "narrative", "description", "summary", "review"
        ]
        
        message_lower = message.lower()
        score = 0.0
        
        for keyword in writing_keywords:
            if keyword in message_lower:
                if keyword in ["write", "article", "essay", "story"]:
                    score += 0.3
                else:
                    score += 0.2
        
        # Boost score for explicit writing requests
        if any(phrase in message_lower for phrase in ["write a", "create content", "help me write"]):
            score += 0.4
        
        return min(score, 1.0)
    
    async def execute_task(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute writing task"""
        try:
            client = await self._get_client()
            if not client:
                return {
                    "status": "error",
                    "error": "Anthropic API key not configured"
                }
            
            # Enhanced system message for writing tasks
            system_message = """Du bist ein erfahrener Schreiber und Content-Creator. Du hilfst beim Erstellen hochwertiger, gut strukturierter Texte für verschiedene Zwecke:

- Essays und Artikel
- Kreative Geschichten
- Technische Dokumentation
- Berichte und Vorschläge
- Marketing-Content

Antworte immer auf Deutsch in einem klaren, professionellen Stil."""
            
            # Call Claude API with correct model
            response = await client.messages.create(
                model="claude-3-5-sonnet",
                max_tokens=4000,
                temperature=0.7,
                system=system_message,
                messages=[
                    {
                        "role": "user",
                        "content": message
                    }
                ]
            )
            
            content = response.content[0].text
            
            # Structure the response for writing tasks
            result = {
                "status": "completed",
                "content": content,
                "word_count": len(content.split()),
                "writing_type": self._detect_writing_type(message),
                "tokens_used": response.usage.input_tokens + response.usage.output_tokens if response.usage else None
            }
            
            # Add sections if it's a structured document
            if any(keyword in message.lower() for keyword in ["outline", "structure", "sections"]):
                result["sections"] = self._extract_sections(content)
            
            return result
            
        except Exception as e:
            logging.error(f"Writing agent error: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _detect_writing_type(self, message: str) -> str:
        """Detect the type of writing requested"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["essay", "academic"]):
            return "essay"
        elif any(word in message_lower for word in ["article", "blog"]):
            return "article"
        elif any(word in message_lower for word in ["story", "creative", "narrative"]):
            return "creative"
        elif any(word in message_lower for word in ["documentation", "manual", "guide"]):
            return "technical"
        elif any(word in message_lower for word in ["report", "analysis"]):
            return "report"
        else:
            return "general"
    
    def _extract_sections(self, content: str) -> list:
        """Extract section headings from content"""
        import re
        
        # Look for markdown-style headers
        sections = re.findall(r'^#+\s+(.+)$', content, re.MULTILINE)
        
        # If no markdown headers, look for numbered sections
        if not sections:
            sections = re.findall(r'^\d+\.\s+(.+)$', content, re.MULTILINE)
        
        return sections[:10]  # Limit to first 10 sections