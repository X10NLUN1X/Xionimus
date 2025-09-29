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
            # Normalize model name for detection (lowercase)
            model_lower = model.lower()
            
            # Use max_completion_tokens for newer models (GPT-5, O1, O3)
            # Use max_tokens for older models (GPT-4, GPT-3.5)
            newer_models = ['gpt-5', 'o1', 'o3']
            use_new_param = any(model_lower.startswith(m) for m in newer_models)
            
            # GPT-5, O1 and O3 models don't support custom temperature - they only support default (1)
            # These are reasoning/advanced models with fixed temperature
            reasoning_models = ['gpt-5', 'o1', 'o3']
            is_reasoning_model = any(m in model_lower for m in reasoning_models)
            
            # Debug logging
            logger.info(f"🔍 Model: {model} (lowercase: {model_lower})")
            logger.info(f"🔍 is_reasoning_model: {is_reasoning_model}")
            logger.info(f"🔍 Will add temperature: {not is_reasoning_model}")
            
            params = {
                "model": model,
                "messages": messages,
                "stream": stream
            }
            
            # Only add temperature for older models (GPT-4, GPT-3.5)
            # GPT-5, O1, O3 do NOT support custom temperature
            if not is_reasoning_model:
                params["temperature"] = 0.7
                logger.info(f"✅ Added temperature=0.7 to params")
            else:
                logger.info(f"⚠️ Skipping temperature for reasoning model")
            
            if use_new_param:
                params["max_completion_tokens"] = 2000
            else:
                params["max_tokens"] = 2000
            
            logger.info(f"🔍 Final params keys: {list(params.keys())}")
            
            response = await self.client.chat.completions.create(**params)
            
            # Debug: Check response structure
            logger.info(f"🔍 OpenAI response type: {type(response)}")
            logger.info(f"🔍 OpenAI response choices length: {len(response.choices)}")
            logger.info(f"🔍 OpenAI response first choice: {response.choices[0]}")
            logger.info(f"🔍 OpenAI response message: {response.choices[0].message}")
            logger.info(f"🔍 OpenAI response content: '{response.choices[0].message.content}'")
            
            if stream:
                return {"stream": response}
            
            # Extract content - might be in different fields for reasoning models
            content = response.choices[0].message.content
            
            # For reasoning models (O1, O3, GPT-5), check if content is in a different field
            if not content or content == "":
                # Try alternative fields
                message = response.choices[0].message
                if hasattr(message, 'text'):
                    content = message.text
                elif hasattr(message, 'output'):
                    content = message.output
                else:
                    logger.error(f"❌ No content found! Message object: {dir(message)}")
                    logger.error(f"❌ Full response: {response}")
            
            logger.info(f"✅ Extracted content length: {len(content) if content else 0} chars")
            
            logger.info(f"✅ Extracted content length: {len(content) if content else 0} chars")
            
            return {
                "content": content or "",  # Ensure content is never None
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
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=60.0  # Increased timeout for research queries (60 seconds)
            )
    
    async def generate_response(
        self, 
        messages: List[Dict[str, str]], 
        model: str = "sonar-pro",  # Updated to current model name
        stream: bool = False
    ) -> Dict[str, Any]:
        if not self.client:
            raise ValueError("Perplexity API key not configured")
        
        try:
            # Validate and fix message format for Perplexity
            # Perplexity requires alternating user/assistant messages
            validated_messages = []
            last_role = None
            
            for msg in messages:
                current_role = msg.get("role")
                
                # Skip if same role as previous (already handled by deduplication in chat.py)
                # But add assistant response between consecutive user messages if needed
                if last_role == "user" and current_role == "user":
                    # Insert a dummy assistant message to maintain alternating pattern
                    logger.info("⚠️ Detected consecutive user messages, skipping duplicate")
                    continue
                
                validated_messages.append(msg)
                last_role = current_role
            
            # Ensure we have at least one message
            if not validated_messages:
                validated_messages = messages
            
            payload = {
                "model": model,
                "messages": validated_messages,
                "temperature": 0.7,
                "max_tokens": 2000
            }
            
            # Only add stream parameter if it's True
            if stream:
                payload["stream"] = True
            
            logger.info(f"🔍 Perplexity request: model={model}, messages={len(validated_messages)} messages, stream={stream}")
            logger.info(f"🔍 Perplexity payload: {payload}")
            
            response = await self.client.post(
                "/chat/completions",
                json=payload
            )
            
            logger.info(f"🔍 Perplexity response status: {response.status_code}")
            
            if stream:
                return {"stream": response}
            
            result = response.json()
            logger.info(f"🔍 Perplexity response keys: {list(result.keys())}")
            
            # Check if response is an error
            if response.status_code != 200:
                error_message = result.get("error", {}).get("message", str(result))
                logger.error(f"Perplexity API error (status {response.status_code}): {error_message}")
                raise ValueError(f"Perplexity API error: {error_message}")
            
            # Check if choices exists in response
            if "choices" not in result:
                logger.error(f"Perplexity API unexpected response: {result}")
                raise ValueError(f"Perplexity API unexpected response format")
            
            content = result["choices"][0]["message"]["content"]
            logger.info(f"✅ Perplexity response content length: {len(content)} characters")
            logger.info(f"✅ Perplexity response preview: {content[:200]}...")
            
            response_data = {
                "content": content,
                "model": model,
                "provider": "perplexity",
                "usage": result.get("usage"),
                "citations": result.get("citations", []),  # Include citations
                "search_results": result.get("search_results", [])  # Include search results
            }
            
            logger.info(f"✅ Returning response with {len(response_data.get('citations', []))} citations")
            return response_data
            
        except httpx.ReadTimeout as e:
            logger.error(f"Perplexity API timeout: Request took longer than 60 seconds")
            raise ValueError(f"Perplexity API timeout: The research query is taking longer than expected. Please try again or use a simpler query.")
        except httpx.HTTPStatusError as e:
            logger.error(f"Perplexity HTTP error: {e.response.status_code}")
            error_msg = str(e)
            if "pplx-" in error_msg:
                error_msg = "Invalid API key provided"
            raise ValueError(f"Perplexity API error: {error_msg}")
        except KeyError as e:
            logger.error(f"Perplexity API response missing key: {e}")
            raise ValueError(f"Perplexity API error: Missing field {e} in response")
        except Exception as e:
            logger.error(f"Perplexity API error: {type(e).__name__} - {str(e)}")
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
                "claude-sonnet-4-5-20250929",   # Latest Claude Sonnet 4.5 - NEW
                "claude-opus-4-1-20250805",     # Claude Opus 4.1
                "claude-4-sonnet-20250514",     # Claude 4 Sonnet
                "claude-3-7-sonnet-20250219"    # Claude 3.7 Sonnet
            ],
            "perplexity": [
                "sonar-pro",              # Best for research and synthesis
                "sonar",                  # Default free model  
                "sonar-deep-research"     # Deep research with reasoning
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