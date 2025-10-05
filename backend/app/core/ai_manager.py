from typing import Dict, Any, Optional, List, AsyncGenerator
import logging
from openai import AsyncOpenAI
import anthropic
import httpx
import json
from .config import settings

# Retry logic for AI API calls
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)

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
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError)),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
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
            
            # For reasoning models (GPT-5, O1, O3), we need to include reasoning in the response
            if is_reasoning_model:
                # Note: Reasoning models return their content in reasoning_tokens
                # We need to check if the OpenAI SDK supports include_reasoning parameter
                # For now, we'll use the standard API and handle empty content
                logger.info("⚠️ Using reasoning model - content may be in reasoning_tokens")
            
            params = {
                "model": model,
                "messages": messages,
                "stream": stream
            }
            
            # Only add temperature for older models (GPT-4, GPT-3.5)
            # GPT-5, O1, O3 do NOT support custom temperature
            if not is_reasoning_model:
                params["temperature"] = 0.7
                logger.info("✅ Added temperature=0.7 to params")
            else:
                logger.info("⚠️ Skipping temperature for reasoning model")
            
            if use_new_param:
                params["max_completion_tokens"] = 2000
            else:
                params["max_tokens"] = 2000
            
            logger.info(f"🔍 Final params keys: {list(params.keys())}")
            
            response = await self.client.chat.completions.create(**params)
            
            # If streaming, return the stream immediately
            if stream:
                logger.info("✅ Returning stream object for streaming response")
                return {"stream": response}
            
            # For non-streaming: Debug and check response structure
            logger.info(f"🔍 OpenAI response finish_reason: {response.choices[0].finish_reason}")
            logger.info(f"🔍 OpenAI response content: '{response.choices[0].message.content}'")
            if response.usage:
                completion_details = getattr(response.usage, 'completion_tokens_details', None)
                if completion_details:
                    reasoning_tokens = getattr(completion_details, 'reasoning_tokens', 0)
                    logger.info(f"🔍 Reasoning tokens: {reasoning_tokens}")
            
            # Extract content
            content = response.choices[0].message.content
            
            # For reasoning models: If content is empty but we have reasoning tokens,
            # we need to inform the user that reasoning content is not available via standard API
            if (not content or content == "") and is_reasoning_model:
                if response.usage and hasattr(response.usage, 'completion_tokens_details'):
                    details = response.usage.completion_tokens_details
                    if hasattr(details, 'reasoning_tokens') and details.reasoning_tokens > 0:
                        # Model generated reasoning but it's not accessible
                        content = (
                            f"⚠️ **Reasoning Model Response Issue**\n\n"
                            f"The model generated {details.reasoning_tokens} reasoning tokens, "
                            f"but the content is not available through the standard Chat Completions API.\n\n"
                            f"**Possible solutions:**\n"
                            f"1. Use GPT-4o or GPT-4.1 instead (they return content normally)\n"
                            f"2. Contact OpenAI support about GPT-5 reasoning content access\n"
                            f"3. Wait for OpenAI to update the API to return reasoning content\n\n"
                            f"**Model used:** {model}\n"
                            f"**Reasoning tokens generated:** {details.reasoning_tokens}"
                        )
                        logger.error(f"❌ Reasoning model returned empty content with {details.reasoning_tokens} reasoning tokens")
            
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
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError)),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    async def generate_response(
        self, 
        messages: List[Dict[str, str]], 
        model: str = "claude-sonnet-4-5-20250929",  # Latest Claude 3.5 Sonnet (Oktober 2024)
        stream: bool = False,
        extended_thinking: bool = False  # NEW: Ultra Thinking parameter
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
            
            # Build request parameters
            params = {
                "model": model,
                "system": system_message,
                "messages": anthropic_messages,
                "stream": stream
            }
            
            # Add extended thinking if enabled
            if extended_thinking:
                # Claude's extended thinking uses "thinking" parameter
                # IMPORTANT: max_tokens MUST be > budget_tokens (Anthropic requirement)
                thinking_budget = 5000
                params["thinking"] = {
                    "type": "enabled",
                    "budget_tokens": thinking_budget  # Thinking tokens
                }
                # max_tokens must be greater than thinking budget
                # Total tokens = thinking_budget + output_tokens
                params["max_tokens"] = thinking_budget + 3000  # 5000 + 3000 = 8000 total
                # Temperature MUST be 1 when thinking is enabled (Anthropic requirement)
                params["temperature"] = 1.0
                logger.info(f"🧠 Extended Thinking aktiviert (budget={thinking_budget}, max_tokens={params['max_tokens']}, temperature=1.0)")
            else:
                # Without thinking, standard max_tokens
                params["max_tokens"] = 2000
                # Without thinking, temperature can be 0 to < 1
                # Using 0.7 as a good balance for creativity and consistency
                params["temperature"] = 0.7
                logger.info("💬 Standard mode (max_tokens=2000, temperature=0.7)")
            
            response = await self.client.messages.create(**params)
            
            if stream:
                return {"stream": response}
            
            # Extract thinking content if available
            thinking_content = None
            main_content = None
            
            for block in response.content:
                if hasattr(block, 'type'):
                    if block.type == 'thinking':
                        # ThinkingBlock has 'thinking' attribute, not 'text'
                        thinking_content = getattr(block, 'thinking', '') or getattr(block, 'text', '')
                    elif block.type == 'text':
                        main_content = block.text
            
            # If no main content but has thinking, try to get text from first block
            if not main_content and response.content:
                first_block = response.content[0]
                main_content = getattr(first_block, 'text', '') or str(first_block)
            
            # Format response with thinking if available
            content = main_content
            if thinking_content and extended_thinking:
                content = f"**🧠 Gedankenprozess:**\n\n{thinking_content}\n\n---\n\n**💬 Antwort:**\n\n{main_content}"
                logger.info(f"✅ Extended Thinking Response: {len(thinking_content)} thinking chars, {len(main_content)} response chars")
            
            return {
                "content": content,
                "model": model,
                "provider": "anthropic",
                "usage": {
                    "prompt_tokens": response.usage.input_tokens,
                    "completion_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens
                },
                "thinking_used": extended_thinking,
                "thinking_content": thinking_content if extended_thinking else None
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
                timeout=900.0  # Increased timeout for deep research queries (15 minutes = 900 seconds)
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
                raise ValueError("Perplexity API unexpected response format")
            
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
            
        except httpx.ReadTimeout:
            logger.error("Perplexity API timeout: Request took longer than 900 seconds (15 minutes)")
            raise ValueError("Perplexity API timeout: The research query is taking longer than expected (15 min limit). Please try again or use a simpler query.")
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
        api_keys: Optional[Dict[str, str]] = None,
        ultra_thinking: bool = False
    ) -> Dict[str, Any]:
        """Generate AI response using specified provider - Classic APIs only"""
        
        # Use dynamic API keys if provided
        if api_keys and api_keys.get(provider):
            dynamic_provider = self._create_dynamic_provider(provider, api_keys[provider])
            # Pass ultra_thinking only to Anthropic provider
            if provider == "anthropic":
                return await dynamic_provider.generate_response(messages, model, stream, extended_thinking=ultra_thinking)
            return await dynamic_provider.generate_response(messages, model, stream)
        
        # Use configured providers
        if provider not in self.providers or self.providers[provider] is None:
            raise ValueError(f"Provider {provider} not configured - Please configure API key")
        
        # Pass ultra_thinking only to Anthropic provider
        if provider == "anthropic":
            return await self.providers[provider].generate_response(messages, model, stream, extended_thinking=ultra_thinking)
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
                "gpt-4o-mini",        # ⭐ 94% GÜNSTIGER - $0.38/1M Tokens - Empfohlen für die meisten Aufgaben
                "gpt-3.5-turbo",      # 💰 84% GÜNSTIGER - $1.00/1M Tokens - Gut für einfache Chats
                "gpt-4o",             # ✅ Premium Modell - $6.25/1M Tokens
                "gpt-4.1",            # ✅ Premium Modell - $6.25/1M Tokens
                "o1",                 # ⚠️ Reasoning model - $37.50/1M Tokens (sehr teuer!)
                "o3"                  # ⚠️ Reasoning model - $37.50/1M Tokens (sehr teuer!)
                # "gpt-5" removed temporarily due to reasoning content API limitations
            ],
            "anthropic": [
                "claude-haiku-3.5-20241022",      # ⭐ 73% GÜNSTIGER - $2.40/1M Tokens - Schnell & günstig
                "claude-sonnet-4-5-20250929"      # Premium Modell - $9.00/1M Tokens
            ],
            "perplexity": [
                "sonar",                  # ⭐ 98% GÜNSTIGER - $0.20/1M Tokens - Standard für Research
                "sonar-pro",              # Premium - $9.00/1M Tokens - Best for research and synthesis
                "sonar-deep-research"     # Premium - Deep research with reasoning
            ]
        }
    
    async def stream_response(
        self,
        provider: str,
        model: str,
        messages: List[Dict[str, str]],
        ultra_thinking: bool = False,
        api_keys: Optional[Dict[str, str]] = None,
        project_context: Optional[Dict[str, Any]] = None,
        autonomous_mode: bool = False,
        session_id: Optional[str] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream AI response chunk by chunk for real-time display
        
        Args:
            project_context: Optional dict with project info (project_name, branch, working_directory)
        
        Yields:
            Dict with 'content' key containing text chunk
        """
        # CRITICAL: Inject project context into system message
        if project_context and project_context.get("project_name"):
            project_info = f"""

🎯 AKTIVES PROJEKT: {project_context['project_name']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📁 Working Directory: {project_context.get('working_directory', f"/app/{project_context['project_name']}")}
🌿 Branch: {project_context.get('branch', 'main')}

✅ DU HAST VOLLSTÄNDIGEN ZUGRIFF AUF DIESES PROJEKT!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 ARBEITSWEISE - VOLLSTÄNDIGE DURCHFÜHRUNG IN EINER ANTWORT:

⚠️ KRITISCH: Führe ALLE Schritte in EINER Response durch! Keine Ankündigungen ohne Ausführung!

🚫 VERBOTEN:
❌ "Ich werde jetzt die Schritte ausführen..."
❌ "Bitte einen Moment Geduld..."
❌ "Ich beginne jetzt mit..."
❌ Jegliche Ankündigung OHNE sofortige Ausführung!

✅ ERLAUBT - MACH ES SO:

**Für Debugging/Code-Analyse**:
```
🔍 VOLLSTÄNDIGE ANALYSE VON {project_context.get('working_directory', f"/app/{project_context['project_name']}")}

━━━ SCHRITT 1: package.json ━━━
[Zeige relevante Inhalte]
✅ Gefunden: [Konkrete Befunde]
⚠️ Problem: [Beschreibung]
💡 Fix: [Konkreter Code]

━━━ SCHRITT 2: app.py ━━━
[Zeige relevante Inhalte]
✅ Gefunden: [Konkrete Befunde]
⚠️ Problem: [Beschreibung]
💡 Fix: [Konkreter Code]

━━━ SCHRITT 3: requirements.txt ━━━
[Zeige relevante Inhalte]
✅ Status: [Befund]

📊 ZUSAMMENFASSUNG:
• Geprüfte Dateien: 3
• Gefundene Probleme: 2
• Vorgeschlagene Fixes: 2

🎯 NÄCHSTE SCHRITTE:
1. [Konkreter Schritt]
2. [Konkreter Schritt]
```

**Für Implementierungen/Änderungen**:
```
🔧 VOLLSTÄNDIGE UMSETZUNG

━━━ ÄNDERUNG 1: package.json ━━━
VORHER:
[Alter Code]

NACHHER:
[Neuer Code]

GRUND: [Erklärung]
✅ Erledigt

━━━ ÄNDERUNG 2: app.py ━━━
VORHER:
[Alter Code]

NACHHER:
[Neuer Code]

GRUND: [Erklärung]
✅ Erledigt

━━━ INSTALLATION ━━━
Benötigte Pakete: mysql2, dotenv
Befehl: npm install mysql2 dotenv
✅ Würde installiert werden

📊 ERGEBNIS:
Alle 2 Änderungen erfolgreich vorgeschlagen
```

🎯 REGEL: Zeige ALLES in EINER Response - Plan + Durchführung + Ergebnis!

"""
            # Add project context to the first system message or create one
            if messages and messages[0]["role"] == "system":
                messages[0]["content"] += project_info
            else:
                # Insert system message with project context at the beginning
                messages.insert(0, {
                    "role": "system",
                    "content": project_info
                })
            
            logger.info(f"✅ Project context injected: {project_context['project_name']}")
        
        # ===== AUTONOMOUS MODE: Function Calling =====
        if autonomous_mode and provider == "openai":
            logger.info("🤖 AUTONOMOUS MODE ACTIVATED - Function calling enabled")
            async for chunk in self._autonomous_openai_stream(
                messages=messages,
                model=model,
                api_keys=api_keys,
                session_id=session_id
            ):
                yield chunk
            return  # Exit after autonomous execution
        
        # Use dynamic API keys if provided
        if api_keys and api_keys.get(provider):
            provider_instance = self._create_dynamic_provider(provider, api_keys[provider])
        elif provider not in self.providers or self.providers[provider] is None:
            raise ValueError(f"Provider {provider} not configured")
        else:
            provider_instance = self.providers[provider]
        
        # OpenAI Streaming
        if provider == "openai":
            if not provider_instance.client:
                raise ValueError("OpenAI API key not configured")
            
            # Check if it's a reasoning model
            model_lower = model.lower()
            is_reasoning_model = any(m in model_lower for m in ['gpt-5', 'o1', 'o3'])
            
            logger.info(f"🔍 Streaming with model: {model}")
            logger.info(f"🔍 Is reasoning model: {is_reasoning_model}")
            
            try:
                stream = await provider_instance.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    stream=True,
                    temperature=0.7 if not is_reasoning_model else None
                )
                
                full_content = ""
                async for chunk in stream:
                    delta = chunk.choices[0].delta
                    
                    # Try to extract content from various possible fields
                    content = None
                    
                    # Standard content field
                    if hasattr(delta, 'content') and delta.content:
                        content = delta.content
                    
                    # For reasoning models, also check reasoning field
                    elif is_reasoning_model:
                        # Try to get reasoning content if available
                        if hasattr(delta, 'reasoning') and delta.reasoning:
                            content = delta.reasoning
                        # Some models may use different field names
                        elif hasattr(delta, 'thinking') and delta.thinking:
                            content = delta.thinking
                    
                    if content:
                        full_content += content
                        yield {"content": content}
                
                # If no content was streamed but it's a reasoning model, inform user
                if not full_content and is_reasoning_model:
                    error_msg = (
                        f"⚠️ Reasoning model '{model}' did not return displayable content.\n\n"
                        f"This can happen when:\n"
                        f"1. The model is still in beta and API doesn't fully support streaming\n"
                        f"2. The reasoning content is not accessible via standard API\n\n"
                        f"Try using GPT-4o or GPT-4.1 instead for consistent results."
                    )
                    yield {"content": error_msg}
                    logger.warning(f"⚠️ Reasoning model {model} returned no displayable content in stream")
            
            except Exception as e:
                logger.error(f"OpenAI streaming error: {e}")
                raise
        
        # Anthropic Streaming
        elif provider == "anthropic":
            if not provider_instance.client:
                raise ValueError("Anthropic API key not configured")
            
            try:
                # Build parameters dynamically
                stream_params = {
                    "model": model,
                    "messages": messages
                }
                
                # Configure thinking and tokens based on ultra_thinking
                if ultra_thinking:
                    # Extended thinking mode
                    thinking_budget = 5000
                    stream_params["thinking"] = {
                        "type": "enabled",
                        "budget_tokens": thinking_budget
                    }
                    # max_tokens MUST be > budget_tokens (Anthropic requirement)
                    stream_params["max_tokens"] = thinking_budget + 3000  # 5000 + 3000 = 8000
                    # Temperature MUST be 1.0 for extended thinking (Anthropic requirement)
                    stream_params["temperature"] = 1.0
                    logger.info(f"🧠 Extended Thinking streaming: budget={thinking_budget}, max_tokens={stream_params['max_tokens']}, temperature=1.0")
                else:
                    # Standard mode
                    stream_params["max_tokens"] = 4096
                    stream_params["temperature"] = 0.7
                    logger.info("💬 Standard streaming: max_tokens=4096, temperature=0.7")
                
                async with provider_instance.client.messages.stream(**stream_params) as stream:
                    async for text in stream.text_stream:
                        yield {"content": text}
            
            except Exception as e:
                logger.error(f"Anthropic streaming error: {e}")
                raise
        
        # Perplexity Streaming
        elif provider == "perplexity":
            if not provider_instance.client:
                raise ValueError("Perplexity API key not configured")
            
            try:
                response = await provider_instance.client.post(
                    "/chat/completions",
                    json={
                        "model": model,
                        "messages": messages,
                        "stream": True,
                        "temperature": 0.7
                    }
                )
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data)
                            if chunk["choices"][0]["delta"].get("content"):
                                yield {"content": chunk["choices"][0]["delta"]["content"]}
                        except (json.JSONDecodeError, KeyError, IndexError):
                            continue
            
            except Exception as e:
                logger.error(f"Perplexity streaming error: {e}")
                raise
        
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    async def _autonomous_openai_stream(
        self,
        messages: List[Dict[str, str]],
        model: str,
        api_keys: Optional[Dict[str, str]] = None,
        session_id: Optional[str] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Autonomous OpenAI streaming with function calling
        Automatically executes tools and streams both thinking and actions
        """
        from .autonomous_tools import AutonomousTools
        from .autonomous_engine import AutonomousExecutionEngine
        from .state_manager import StateManager
        
        # Initialize autonomous components
        tools = AutonomousTools()
        tool_schemas = tools.get_tool_schemas()
        
        state_manager = StateManager(session_id) if session_id else None
        engine = AutonomousExecutionEngine(state_manager)
        
        # Get OpenAI client
        if api_keys and api_keys.get("openai"):
            client = AsyncOpenAI(api_key=api_keys["openai"])
        elif self.providers["openai"]:
            client = self.providers["openai"].client
        else:
            raise ValueError("OpenAI API key not configured")
        
        logger.info(f"🤖 Starting autonomous execution with {len(tool_schemas)} tools")
        
        # Multi-turn function calling loop
        conversation = messages.copy()
        max_iterations = 10  # Prevent infinite loops
        iteration = 0
        
        try:
            while iteration < max_iterations:
                iteration += 1
                logger.info(f"🔄 Autonomous iteration {iteration}/{max_iterations}")
                
                # Call OpenAI with function calling
                response = await client.chat.completions.create(
                    model=model,
                    messages=conversation,
                    tools=tool_schemas,
                    tool_choice="auto",  # Let AI decide when to use tools
                    stream=False  # We'll manually stream results
                )
                
                assistant_message = response.choices[0].message
                finish_reason = response.choices[0].finish_reason
                
                # Check if AI wants to call functions
                if finish_reason == "tool_calls" and assistant_message.tool_calls:
                    logger.info(f"🔧 AI requested {len(assistant_message.tool_calls)} tool calls")
                    
                    # Add assistant message to conversation
                    conversation.append({
                        "role": "assistant",
                        "content": assistant_message.content or "",
                        "tool_calls": [
                            {
                                "id": tc.id,
                                "type": "function",
                                "function": {
                                    "name": tc.function.name,
                                    "arguments": tc.function.arguments
                                }
                            }
                            for tc in assistant_message.tool_calls
                        ]
                    })
                    
                    # Execute each tool call
                    for tool_call in assistant_message.tool_calls:
                        tool_name = tool_call.function.name
                        try:
                            arguments = json.loads(tool_call.function.arguments)
                        except json.JSONDecodeError:
                            arguments = {}
                        
                        # Stream action start
                        yield {
                            "type": "action_start",
                            "tool": tool_name,
                            "arguments": arguments
                        }
                        
                        # Execute tool
                        result = await engine.execute_tool(tool_name, arguments)
                        
                        # Log action to state manager
                        if state_manager:
                            await state_manager.log_action(tool_name, arguments, result)
                        
                        # Stream action complete
                        yield {
                            "type": "action_complete",
                            "tool": tool_name,
                            "success": result["success"],
                            "result": result["result"],
                            "error": result.get("error"),
                            "execution_time": result.get("execution_time", 0)
                        }
                        
                        # Add tool result to conversation
                        conversation.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps({
                                "success": result["success"],
                                "result": result["result"],
                                "error": result.get("error")
                            })
                        })
                    
                    # Continue loop - AI will process tool results
                    continue
                
                # No more tool calls - stream final response
                if assistant_message.content:
                    logger.info("💬 Streaming final AI response")
                    yield {
                        "type": "content",
                        "content": assistant_message.content
                    }
                
                # Exit loop
                break
            
            # Check if we hit max iterations
            if iteration >= max_iterations:
                logger.warning(f"⚠️ Autonomous execution reached max iterations ({max_iterations})")
                yield {
                    "type": "warning",
                    "content": f"⚠️ Reached maximum autonomous execution iterations ({max_iterations}). Stopping for safety."
                }
        
        except Exception as e:
            logger.error(f"❌ Autonomous execution error: {e}")
            yield {
                "type": "error",
                "content": f"❌ Autonomous execution failed: {str(e)}"
            }
        
        finally:
            # Cleanup
            if state_manager:
                state_manager.close()
            logger.info("✅ Autonomous execution complete")

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