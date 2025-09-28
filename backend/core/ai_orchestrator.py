from typing import Dict, Any, Optional, List
import logging
from fastapi import HTTPException
from openai import AsyncOpenAI
import anthropic
import httpx
from .config import settings

logger = logging.getLogger(__name__)

class AIOrchestrator:
    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        self.perplexity_client = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize AI service clients"""
        try:
            if settings.OPENAI_API_KEY:
                self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
                logger.info("✅ OpenAI client initialized")
            
            if settings.ANTHROPIC_API_KEY:
                self.anthropic_client = anthropic.AsyncAnthropic(
                    api_key=settings.ANTHROPIC_API_KEY
                )
                logger.info("✅ Anthropic client initialized")
            
            if settings.PERPLEXITY_API_KEY:
                self.perplexity_client = httpx.AsyncClient(
                    base_url="https://api.perplexity.ai",
                    headers={"Authorization": f"Bearer {settings.PERPLEXITY_API_KEY}"}
                )
                logger.info("✅ Perplexity client initialized")
                
        except Exception as e:
            logger.error(f"❌ AI client initialization failed: {e}")
    
    async def generate_response(
        self, 
        agent_type: str, 
        message: str, 
        model: str = "gpt-4o-mini",
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Generate AI response based on agent type and model"""
        try:
            if model.startswith("gpt") and self.openai_client:
                return await self._openai_generate(agent_type, message, model, context)
            elif model.startswith("claude") and self.anthropic_client:
                return await self._anthropic_generate(agent_type, message, model, context)
            elif model.startswith("perplexity") and self.perplexity_client:
                return await self._perplexity_generate(agent_type, message, context)
            else:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Model {model} not available or API key not configured"
                )
        except Exception as e:
            logger.error(f"❌ AI generation failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def _openai_generate(
        self, agent_type: str, message: str, model: str, context: Optional[Dict]
    ) -> Dict[str, Any]:
        """Generate response using OpenAI"""
        system_prompt = self._get_agent_prompt(agent_type)
        
        response = await self.openai_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        return {
            "content": response.choices[0].message.content,
            "model": model,
            "agent": agent_type,
            "usage": response.usage.dict() if response.usage else None
        }
    
    async def _anthropic_generate(
        self, agent_type: str, message: str, model: str, context: Optional[Dict]
    ) -> Dict[str, Any]:
        """Generate response using Anthropic Claude"""
        system_prompt = self._get_agent_prompt(agent_type)
        
        response = await self.anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            temperature=0.7,
            system=system_prompt,
            messages=[
                {"role": "user", "content": message}
            ]
        )
        
        return {
            "content": response.content[0].text,
            "model": "claude-3-5-sonnet",
            "agent": agent_type,
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens
            }
        }
    
    async def _perplexity_generate(
        self, agent_type: str, message: str, context: Optional[Dict]
    ) -> Dict[str, Any]:
        """Generate response using Perplexity"""
        system_prompt = self._get_agent_prompt(agent_type)
        
        response = await self.perplexity_client.post(
            "/chat/completions",
            json={
                "model": "llama-3.1-sonar-large-128k-online",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                "temperature": 0.7,
                "max_tokens": 2000
            }
        )
        
        result = response.json()
        return {
            "content": result["choices"][0]["message"]["content"],
            "model": "perplexity-sonar",
            "agent": agent_type,
            "usage": result.get("usage")
        }
    
    def _get_agent_prompt(self, agent_type: str) -> str:
        """Get system prompt for specific agent type"""
        prompts = {
            "code": "You are a specialized code generation and analysis agent. Help with programming tasks, debugging, and code optimization.",
            "research": "You are a research agent specialized in deep web research, information gathering, and fact-checking. Provide comprehensive, accurate information.",
            "writing": "You are a writing agent specialized in content creation, documentation, and communication. Create clear, engaging content.",
            "data": "You are a data analysis agent specialized in statistical analysis, data processing, and insights generation.",
            "qa": "You are a quality assurance agent specialized in testing, validation, and quality control processes.",
            "github": "You are a GitHub integration agent specialized in repository management, version control, and code collaboration.",
            "file": "You are a file management agent specialized in file operations, organization, and data handling.",
            "session": "You are a session management agent specialized in conversation flow, state management, and user experience.",
            "experimental": "You are an experimental agent for advanced AI features, code review, and innovative solutions."
        }
        return prompts.get(agent_type, "You are a helpful AI assistant.")
    
    def get_available_services(self) -> Dict[str, bool]:
        """Get status of available AI services"""
        return {
            "openai": self.openai_client is not None,
            "anthropic": self.anthropic_client is not None,
            "perplexity": self.perplexity_client is not None
        }

# Global orchestrator instance
orchestrator = AIOrchestrator()

async def test_ai_services():
    """Test AI service availability"""
    services = orchestrator.get_available_services()
    
    for service, available in services.items():
        if available:
            logger.info(f"✅ {service.title()} service available")
        else:
            logger.warning(f"⚠️ {service.title()} service not configured")
    
    if not any(services.values()):
        logger.warning("⚠️ No AI services configured - Please add API keys")