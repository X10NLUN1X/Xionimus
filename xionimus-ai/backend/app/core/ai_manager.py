from typing import Dict, Any, Optional, List, AsyncGenerator
import logging
from openai import AsyncOpenAI
import anthropic
import httpx
import json
from .config import settings

logger = logging.getLogger(__name__)

class AIProvider:
    """Base class for AI providers"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = None
    
    async def generate_response(
        self, 
        messages: List[Dict[str, str]], 
        model: str,
        stream: bool = False
    ) -> Dict[str, Any]:
        raise NotImplementedError

class OpenAIProvider(AIProvider):
    def __init__(self, api_key: str):
        super().__init__(api_key)
        if api_key:
            self.client = AsyncOpenAI(api_key=api_key)
    
    async def generate_response(
        self, 
        messages: List[Dict[str, str]], 
        model: str = "gpt-5",  # Updated default to GPT-5
        stream: bool = False
    ) -> Dict[str, Any]:
        if not self.client:
            raise ValueError("OpenAI API key not configured")
        
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
                max_tokens=2000,
                stream=stream
            )
            
            if stream:
                return {"stream": response}
            
            return {
                "content": response.choices[0].message.content,
                "model": model,
                "provider": "openai",
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                } if response.usage else None
            }
            
        except Exception as e:
            logger.error(f"OpenAI API error: {type(e).__name__}")
            # Sanitize error message to avoid API key exposure
            error_msg = str(e)
            if "sk-" in error_msg:
                error_msg = "Invalid API key provided"
            raise ValueError(f"OpenAI API error: {error_msg}")

class AnthropicProvider(AIProvider):
    def __init__(self, api_key: str):
        super().__init__(api_key)
        if api_key:
            self.client = anthropic.AsyncAnthropic(api_key=api_key)
    
    async def generate_response(
        self, 
        messages: List[Dict[str, str]], 
        model: str = "claude-opus-4-1-20250805",  # Updated to Claude Opus 4.1
        stream: bool = False
    ) -> Dict[str, Any]:
        if not self.client:
            raise ValueError("Anthropic API key not configured")
        
        try:
            # Convert messages format for Anthropic
            system_message = ""
            anthropic_messages = []
            
            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                else:
                    anthropic_messages.append(msg)
            
            response = await self.client.messages.create(
                model=model,
                max_tokens=2000,
                temperature=0.7,
                system=system_message,
                messages=anthropic_messages,
                stream=stream
            )
            
            if stream:
                return {"stream": response}
            
            return {
                "content": response.content[0].text,
                "model": model,
                "provider": "anthropic",
                "usage": {
                    "prompt_tokens": response.usage.input_tokens,
                    "completion_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens
                }
            }
            
        except Exception as e:
            logger.error(f"Anthropic API error: {type(e).__name__}")
            # Sanitize error message to avoid API key exposure
            error_msg = str(e)
            if "sk-ant-" in error_msg:
                error_msg = "Invalid API key provided"
            raise ValueError(f"Anthropic API error: {error_msg}")

class PerplexityProvider(AIProvider):
    def __init__(self, api_key: str):
        super().__init__(api_key)
        if api_key:
            self.client = httpx.AsyncClient(
                base_url="https://api.perplexity.ai",
                headers={"Authorization": f"Bearer {api_key}"}
            )
    
    async def generate_response(
        self, 
        messages: List[Dict[str, str]], 
        model: str = "llama-3.1-sonar-large-128k-online",
        stream: bool = False
    ) -> Dict[str, Any]:
        if not self.client:
            raise ValueError("Perplexity API key not configured")
        
        try:
            response = await self.client.post(
                "/chat/completions",
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 2000,
                    "stream": stream
                }
            )
            
            if stream:
                return {"stream": response}
            
            result = response.json()
            return {
                "content": result["choices"][0]["message"]["content"],
                "model": model,
                "provider": "perplexity",
                "usage": result.get("usage")
            }
            
        except Exception as e:
            logger.error(f"Perplexity API error: {type(e).__name__}")
            # Sanitize error message to avoid API key exposure
            error_msg = str(e)
            if "pplx-" in error_msg:
                error_msg = "Invalid API key provided"
            raise ValueError(f"Perplexity API error: {error_msg}")

class AIManager:
    """Classic AI Manager - Only traditional API keys, no third-party integration"""
    
    def __init__(self):
        self.providers = {
            "openai": OpenAIProvider(settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None,
            "anthropic": AnthropicProvider(settings.ANTHROPIC_API_KEY) if settings.ANTHROPIC_API_KEY else None,
            "perplexity": PerplexityProvider(settings.PERPLEXITY_API_KEY) if settings.PERPLEXITY_API_KEY else None
        }
    
    async def generate_response(
        self,
        provider: str,
        model: str,
        messages: List[Dict[str, str]],
        stream: bool = False,
        api_keys: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Generate AI response using specified provider - Classic APIs only"""
        
        # Use dynamic API keys if provided
        if api_keys and api_keys.get(provider):
            dynamic_provider = self._create_dynamic_provider(provider, api_keys[provider])
            return await dynamic_provider.generate_response(messages, model, stream)
        
        # Use configured providers
        if provider not in self.providers or self.providers[provider] is None:
            raise ValueError(f"Provider {provider} not configured - Please configure API key")
        
        return await self.providers[provider].generate_response(messages, model, stream)
    
    def _create_dynamic_provider(self, provider: str, api_key: str):
        """Create provider instance with dynamic API key"""
        if provider == "openai":
            return OpenAIProvider(api_key)
        elif provider == "anthropic":
            return AnthropicProvider(api_key)
        elif provider == "perplexity":
            return PerplexityProvider(api_key)
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    def get_provider_status(self) -> Dict[str, bool]:
        """Get status of all AI providers"""
        return {
            name: provider is not None 
            for name, provider in self.providers.items()
        }
    
    def get_available_models(self) -> Dict[str, List[str]]:
        """Get available models for each provider - Latest models only (shows models even without API keys)"""
        return {
            "openai": [
                "gpt-5",
                "gpt-4o", 
                "gpt-4.1",
                "o1",
                "o3"
            ],
            "anthropic": [
                "claude-opus-4-1-20250805",     # User specified model
                "claude-4-sonnet-20250514",
                "claude-3-7-sonnet-20250219"
            ],
            "perplexity": [
                "llama-3.1-sonar-large-128k-online"
            ]
        }

async def test_ai_services():
    """Test AI service availability - Classic APIs only"""
    ai_manager = AIManager()
    providers = ai_manager.get_provider_status()
    
    logger.info("🧪 Testing AI services with classic API keys...")
    
    for provider, available in providers.items():
        if available:
            logger.info(f"✅ {provider.title()} provider available")
            
            # Show available models
            models = ai_manager.get_available_models().get(provider, [])
            if models:
                logger.info(f"📋 {provider.title()} models: {', '.join(models[:3])}...")
        else:
            logger.warning(f"⚠️ {provider.title()} provider not configured - Add {provider.upper()}_API_KEY")
    
    if not any(providers.values()):
        logger.warning("⚠️ No AI providers configured - Add API keys to enable AI features")