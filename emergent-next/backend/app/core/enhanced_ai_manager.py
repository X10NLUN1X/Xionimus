from typing import Dict, Any, Optional, List, AsyncGenerator
import logging
from datetime import datetime, timezone
import os
from dotenv import load_dotenv

# Standard AI provider imports (fallback)
from openai import AsyncOpenAI
import anthropic
import httpx

# Emergent integrations for latest models
from emergentintegrations.llm.chat import LlmChat, UserMessage

from .config import settings

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class EnhancedAIManager:
    """Enhanced AI Manager with latest model support and Emergent integrations"""
    
    def __init__(self):
        self.emergent_llm_key = settings.EMERGENT_LLM_KEY or os.getenv('EMERGENT_LLM_KEY')
        
        # Latest model configurations
        self.latest_models = {
            "openai": {
                "gpt-5": "gpt-5",                           # Latest GPT-5
                "gpt-4o": "gpt-4o",                         # Updated GPT-4o
                "gpt-4.1": "gpt-4.1",                       # GPT-4.1 series
                "o1": "o1",                                 # O1 series
                "o3": "o3"                                  # O3 series
            },
            "anthropic": {
                "claude-4-opus-20250514": "claude-4-opus-20250514",       # Latest Claude 4 Opus
                "claude-4-sonnet-20250514": "claude-4-sonnet-20250514",   # Latest Claude 4 Sonnet
                "claude-3-7-sonnet-20250219": "claude-3-7-sonnet-20250219" # Latest Claude 3.7
            },
            "gemini": {
                "gemini-2.5-pro": "gemini-2.5-pro",       # Latest Gemini 2.5 Pro
                "gemini-2.5-flash": "gemini-2.5-flash",   # Latest Gemini 2.5 Flash
                "gemini-2.0-flash": "gemini-2.0-flash"    # Gemini 2.0 Flash
            }
        }
        
        # Initialize traditional providers as fallback
        self.traditional_providers = {
            "openai": AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None,
            "anthropic": anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY) if settings.ANTHROPIC_API_KEY else None,
            "perplexity": httpx.AsyncClient(
                base_url="https://api.perplexity.ai",
                headers={"Authorization": f"Bearer {settings.PERPLEXITY_API_KEY}"}
            ) if settings.PERPLEXITY_API_KEY else None
        }

    async def generate_response_with_emergent(
        self,
        provider: str,
        model: str,
        messages: List[Dict[str, str]],
        session_id: str,
        stream: bool = False
    ) -> Dict[str, Any]:
        """Generate response using Emergent integrations with latest models"""
        
        if not self.emergent_llm_key:
            raise ValueError("Emergent LLM key not configured")
        
        try:
            # Convert messages to proper format
            if messages and messages[0].get('role') == 'system':
                system_message = messages[0]['content']
                user_messages = messages[1:]
            else:
                system_message = "You are a helpful AI assistant."
                user_messages = messages
            
            # Initialize chat with Emergent integrations
            chat = LlmChat(
                api_key=self.emergent_llm_key,
                session_id=session_id,
                system_message=system_message
            )
            
            # Set the model and provider
            chat.with_model(provider, model)
            
            # Get the last user message
            if user_messages:
                last_message = user_messages[-1]['content']
                user_message = UserMessage(text=last_message)
                
                # Send message and get response
                response = await chat.send_message(user_message)
                
                return {
                    "content": response,
                    "provider": provider,
                    "model": model,
                    "usage": {
                        "prompt_tokens": len(' '.join([msg['content'] for msg in messages])) // 4,
                        "completion_tokens": len(response) // 4,
                        "total_tokens": (len(' '.join([msg['content'] for msg in messages])) + len(response)) // 4
                    }
                }
            else:
                raise ValueError("No user messages provided")
                
        except Exception as e:
            logger.error(f"Emergent integration error for {provider}/{model}: {e}")
            raise

    async def generate_response_traditional(
        self,
        provider: str,
        model: str,
        messages: List[Dict[str, str]],
        api_keys: Optional[Dict[str, str]] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """Generate response using traditional provider APIs"""
        
        # Use dynamic API keys if provided
        if api_keys and api_keys.get(provider):
            api_key = api_keys[provider]
        else:
            api_key = getattr(settings, f"{provider.upper()}_API_KEY", None)
        
        if not api_key:
            raise ValueError(f"No API key configured for {provider}")
        
        # Use traditional provider implementations
        if provider == "openai":
            client = AsyncOpenAI(api_key=api_key)
            response = await client.chat.completions.create(
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
            
        elif provider == "anthropic":
            client = anthropic.AsyncAnthropic(api_key=api_key)
            
            # Convert messages format for Anthropic
            system_message = ""
            anthropic_messages = []
            
            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                else:
                    anthropic_messages.append(msg)
            
            response = await client.messages.create(
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
        
        elif provider == "perplexity":
            client = httpx.AsyncClient(
                base_url="https://api.perplexity.ai",
                headers={"Authorization": f"Bearer {api_key}"}
            )
            
            response = await client.post(
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
        
        else:
            raise ValueError(f"Unknown provider: {provider}")

    async def generate_response(
        self,
        provider: str,
        model: str,
        messages: List[Dict[str, str]],
        session_id: Optional[str] = None,
        stream: bool = False,
        api_keys: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Generate AI response using best available method"""
        
        # Try Emergent integrations first for latest models
        if self.emergent_llm_key and session_id and model in self.latest_models.get(provider, {}):
            try:
                logger.info(f"🚀 Using Emergent integration for {provider}/{model}")
                return await self.generate_response_with_emergent(
                    provider, model, messages, session_id, stream
                )
            except Exception as e:
                logger.warning(f"Emergent integration failed, falling back to traditional: {e}")
        
        # Fallback to traditional providers
        logger.info(f"📡 Using traditional API for {provider}/{model}")
        return await self.generate_response_traditional(
            provider, model, messages, api_keys, stream
        )

    def get_provider_status(self) -> Dict[str, bool]:
        """Get status of all AI providers"""
        status = {}
        
        # Check Emergent integration availability
        emergent_available = bool(self.emergent_llm_key)
        
        # Check traditional providers
        for provider, client in self.traditional_providers.items():
            traditional_available = client is not None
            
            # Provider is available if either method works
            status[provider] = emergent_available or traditional_available
        
        # Add Gemini support via Emergent
        status["gemini"] = emergent_available
        
        return status

    def get_available_models(self) -> Dict[str, List[str]]:
        """Get available models for each provider"""
        models = {}
        
        for provider in ["openai", "anthropic", "gemini", "perplexity"]:
            provider_models = []
            
            # Add latest models if Emergent key available
            if self.emergent_llm_key and provider in self.latest_models:
                provider_models.extend(list(self.latest_models[provider].keys()))
            
            # Add traditional models if traditional API available
            if provider in self.traditional_providers and self.traditional_providers[provider]:
                if provider == "openai":
                    provider_models.extend(["gpt-4o", "gpt-4o-mini", "o1-preview", "o1-mini"])
                elif provider == "anthropic":
                    provider_models.extend(["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022"])
                elif provider == "perplexity":
                    provider_models.extend(["llama-3.1-sonar-large-128k-online", "llama-3.1-sonar-small-128k-online"])
            
            # Remove duplicates and set
            models[provider] = list(dict.fromkeys(provider_models))
        
        return models

    async def test_connection(self, provider: str, model: str) -> bool:
        """Test connection to a specific provider/model"""
        try:
            test_messages = [{"role": "user", "content": "Hello, this is a connection test."}]
            response = await self.generate_response(
                provider=provider,
                model=model,
                messages=test_messages,
                session_id="test-session"
            )
            return bool(response.get("content"))
        except Exception as e:
            logger.error(f"Connection test failed for {provider}/{model}: {e}")
            return False

# Create enhanced manager instance
enhanced_ai_manager = EnhancedAIManager()

# Backward compatibility - alias for existing code
AIManager = EnhancedAIManager

async def test_ai_services():
    """Test AI service availability with enhanced manager"""
    ai_manager = enhanced_ai_manager
    providers = ai_manager.get_provider_status()
    
    logger.info("🧪 Testing AI services with enhanced manager...")
    
    for provider, available in providers.items():
        if available:
            logger.info(f"✅ {provider.title()} provider available")
            
            # Test latest model if available
            models = ai_manager.get_available_models().get(provider, [])
            if models:
                latest_model = models[0]  # First model is usually the latest
                logger.info(f"🚀 Latest {provider} model: {latest_model}")
        else:
            logger.warning(f"⚠️ {provider.title()} provider not configured")
    
    # Test Emergent key if available
    if ai_manager.emergent_llm_key:
        logger.info(f"🔑 Emergent LLM key configured: {ai_manager.emergent_llm_key[:20]}...")
    else:
        logger.warning("⚠️ Emergent LLM key not configured - Add to enable latest models")