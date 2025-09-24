from .base_agent import BaseAgent, AgentCapability
from typing import Dict, Any
import anthropic
import os
import logging

class CodeAgent(BaseAgent):
    """Agent specialized in code generation and analysis"""
    
    def __init__(self):
        super().__init__(
            name="Code Agent", 
            description="Code Generation, Code Analysis, Debugging",
            capabilities=[
                AgentCapability.CODE_GENERATION,
                AgentCapability.CODE_ANALYSIS,
                AgentCapability.DEBUGGING
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
        code_keywords = [
            "code", "function", "class", "debug", "error", "bug", "python", 
            "javascript", "react", "api", "algorithm", "program", "script",
            "implementation", "refactor", "optimize", "fix", "compile", "syntax"
        ]
        
        # High priority code-specific phrases
        high_priority_phrases = [
            "write code", "create function", "debug this", "fix error", "python function",
            "javascript code", "write a function", "implement algorithm", "programming",
            "calculate", "fibonacci", "prime numbers", "code example"
        ]
        
        message_lower = message.lower()
        score = 0.0
        
        # Check for high priority phrases first
        for phrase in high_priority_phrases:
            if phrase in message_lower:
                score += 0.6  # Much higher weight for specific code requests
                break
        
        # Add points for individual keywords
        for keyword in code_keywords:
            if keyword in message_lower:
                if keyword in ["code", "function", "debug", "python", "javascript", "algorithm"]:
                    score += 0.3
                else:
                    score += 0.2
        
        # Penalize if it's clearly a writing/documentation task
        writing_indicators = ["documentation", "write about", "explain the concept", "create content"]
        for indicator in writing_indicators:
            if indicator in message_lower:
                score *= 0.3  # Reduce score significantly
        
        return min(score, 1.0)
    
    async def execute_task(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute code-related task"""
        try:
            client = await self._get_client()
            if not client:
                return {
                    "status": "error",
                    "error": "Anthropic API key not configured"
                }
            
            # Enhanced system message for coding tasks
            system_message = """Du bist ein erfahrener Software-Entwickler. Du hilfst bei:

- Code-Generierung in Python, JavaScript, React, FastAPI
- Debugging und Fehlerbehebung
- Code-Analyse und Review
- Optimierung und Refactoring
- Algorithmus-Implementierung

Antworte auf Deutsch mit sauberem, gut kommentiertem Code. Erkläre die Logik und gib Empfehlungen für Best Practices."""
            
            # Call Claude API with correct model
            response = await client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4000,
                temperature=0.3,  # Lower temperature for more precise code
                system=system_message,
                messages=[
                    {
                        "role": "user",
                        "content": message
                    }
                ]
            )
            
            content = response.content[0].text
            
            # Extract code blocks and create structured response
            result = {
                "status": "completed",
                "main_code": self._extract_main_code(content),
                "explanation": self._extract_explanation(content),
                "language": self._detect_language(message, content),
                "recommendations": self._extract_recommendations(content),
                "tokens_used": response.usage.input_tokens + response.usage.output_tokens if response.usage else None
            }
            
            return result
            
        except Exception as e:
            logging.error(f"Code agent error: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _extract_main_code(self, content: str) -> str:
        """Extract the main code block from the response"""
        import re
        
        # Look for code blocks
        code_blocks = re.findall(r'```[\w]*\n(.*?)\n```', content, re.DOTALL)
        
        if code_blocks:
            # Return the largest code block
            return max(code_blocks, key=len).strip()
        
        return ""
    
    def _extract_explanation(self, content: str) -> str:
        """Extract explanation text (non-code parts)"""
        import re
        
        # Remove code blocks and get remaining text
        no_code = re.sub(r'```[\w]*\n.*?\n```', '', content, flags=re.DOTALL)
        
        # Clean up extra whitespace
        explanation = ' '.join(no_code.split())
        
        return explanation.strip() if explanation else ""
    
    def _detect_language(self, message: str, content: str) -> str:
        """Detect the programming language"""
        message_lower = message.lower()
        content_lower = content.lower()
        
        languages = {
            "python": ["python", "py", "def ", "import ", "from "],
            "javascript": ["javascript", "js", "function", "const ", "let ", "var "],
            "react": ["react", "jsx", "component", "usestate", "useeffect"],
            "html": ["html", "<div", "<span", "<html"],
            "css": ["css", "style", "background", "color:"],
            "sql": ["sql", "select", "from", "where", "insert"]
        }
        
        for lang, keywords in languages.items():
            if any(keyword in message_lower or keyword in content_lower for keyword in keywords):
                return lang
        
        return "text"
    
    def _extract_recommendations(self, content: str) -> list:
        """Extract recommendations from the response"""
        import re
        
        # Look for bullet points or numbered recommendations
        recommendations = []
        
        # Look for bullet points
        bullets = re.findall(r'[•\-\*]\s+(.+)', content)
        recommendations.extend(bullets)
        
        # Look for numbered points  
        numbered = re.findall(r'\d+\.\s+(.+)', content)
        recommendations.extend(numbered)
        
        # Look for "empfehlung" or "tipp" sections
        recommendation_sections = re.findall(r'(?i)(?:empfehlung|tipp|hinweis).*?:\s*(.+)', content)
        recommendations.extend(recommendation_sections)
        
        # Clean and limit recommendations
        clean_recs = [rec.strip() for rec in recommendations if rec.strip()]
        return clean_recs[:5]  # Limit to 5 recommendations