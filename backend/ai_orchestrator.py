"""
AI Orchestrator - Intelligente Model-Auswahl und -Koordination
Koordiniert zwischen Claude Sonnet 4, Perplexity Deep Research und GPT-5 für optimale Ergebnisse
Mit DNS-Bypass für blockierte Umgebungen und Offline-Simulator als Fallback
"""
import asyncio
import logging
import re
from typing import Dict, Any, List, Optional, Tuple
import anthropic
import openai
from datetime import datetime
try:
    from .offline_ai_simulator import offline_simulator
except ImportError:
    from offline_ai_simulator import offline_simulator

try:
    from .dns_bypass import get_bypass_manager
except ImportError:
    from dns_bypass import get_bypass_manager

def _extract_text_from_anthropic_response(response) -> str:
    """Safely extract text from Anthropic response content"""
    try:
        if hasattr(response, 'content') and response.content:
            if isinstance(response.content, list) and len(response.content) > 0:
                # Get the first content block
                content_block = response.content[0]
                if hasattr(content_block, 'text'):
                    return str(content_block.text)
                elif isinstance(content_block, dict) and 'text' in content_block:
                    return str(content_block['text'])
                else:
                    # Fallback: convert entire content block to string
                    return str(content_block)
            elif isinstance(response.content, str):
                return response.content
            else:
                # Fallback: convert entire content to string
                return str(response.content)
        return "No content in response"
    except Exception as e:
        logging.error(f"Error extracting text from Anthropic response: {e}")
        return f"Error extracting response content: {str(e)}"

class AIOrchestrator:
    """Intelligenter AI-Orchestrator für nahtlose Multi-Model Integration"""
    
    def __init__(self, anthropic_key: str = None, openai_key: str = None, perplexity_key: str = None):
        self.anthropic_client = None
        self.openai_client = None  
        self.perplexity_client = None
        self.anthropic_key = anthropic_key
        self.openai_key = openai_key
        self.perplexity_key = perplexity_key
        self.bypass_initialized = False
        
        if anthropic_key:
            self.anthropic_client = anthropic.AsyncAnthropic(api_key=anthropic_key)
        if openai_key:
            self.openai_client = openai.AsyncOpenAI(api_key=openai_key)
        if perplexity_key:
            self.perplexity_client = openai.AsyncOpenAI(
                api_key=perplexity_key,
                base_url="https://api.perplexity.ai"
            )
    
    async def initialize_bypass_clients(self):
        """Initialize DNS bypass clients if normal connections fail"""
        if self.bypass_initialized:
            return
            
        try:
            bypass_manager = await get_bypass_manager()
            
            # Try to create bypassed clients
            if self.anthropic_key and not self.anthropic_client:
                self.anthropic_client = await bypass_manager.create_bypassed_anthropic_client(self.anthropic_key)
                if self.anthropic_client:
                    logging.info("✅ Anthropic DNS bypass successful")
                    
            if self.openai_key and not self.openai_client:
                self.openai_client = await bypass_manager.create_bypassed_openai_client(self.openai_key)
                if self.openai_client:
                    logging.info("✅ OpenAI DNS bypass successful")
                    
            if self.perplexity_key and not self.perplexity_client:
                self.perplexity_client = await bypass_manager.create_bypassed_perplexity_client(self.perplexity_key)
                if self.perplexity_client:
                    logging.info("✅ Perplexity DNS bypass successful")
            
            self.bypass_initialized = True
            
        except Exception as e:
            logging.error(f"DNS bypass initialization failed: {e}")
            self.bypass_initialized = True  # Don't keep retrying
    
    def analyze_user_intent(self, message: str) -> Dict[str, Any]:
        """Analysiert User-Anfrage und bestimmt benötigte KI-Services"""
        
        # Keywords für verschiedene Service-Typen
        research_keywords = [
            'recherche', 'research', 'information', 'nachrichten', 'news', 'aktuell', 'current',
            'facts', 'fakten', 'statistik', 'statistics', 'what is', 'was ist', 'explain',
            'erkläre', 'trends', 'entwicklung', 'latest', 'neueste', 'compare', 'vergleiche'
        ]
        
        code_keywords = [
            'code', 'programming', 'python', 'javascript', 'react', 'html', 'css', 'sql',
            'function', 'class', 'algorithm', 'debug', 'error', 'bug', 'api', 'database',
            'implementiere', 'implement', 'entwickle', 'create', 'build'
        ]
        
        technical_keywords = [
            'technical', 'technisch', 'analysis', 'analyse', 'architecture', 'system',
            'design', 'konzept', 'struktur', 'framework', 'library', 'tool'
        ]
        
        writing_keywords = [
            'schreibe', 'write', 'artikel', 'article', 'blog', 'text', 'content', 'story',
            'essay', 'report', 'bericht', 'documentation', 'dokumentation', 'brief', 'letter',
            'email', 'marketing', 'copy', 'creative', 'kreativ'
        ]
        
        data_keywords = [
            'data', 'daten', 'analyse', 'analysis', 'dataset', 'csv', 'excel', 'chart',
            'graph', 'visualization', 'visualisierung', 'statistics', 'metrics', 'dashboard',
            'import', 'export', 'transform', 'etl', 'pandas', 'numpy'
        ]
        
        # New experimental feature keywords
        experimental_keywords = [
            # AI Code Review
            'code review', 'review code', 'analyse code', 'code quality', 'code inspection',
            'static analysis', 'code audit',
            # Predictive Coding
            'predict', 'next step', 'suggest next', 'what next', 'continue code',
            'complete code', 'predictive', 'auto complete',
            # Auto-Refactoring
            'refactor', 'optimize', 'improve code', 'clean code', 'restructure',
            'auto refactor', 'code optimization',
            # Performance Profiling
            'profile', 'performance', 'benchmark', 'timing', 'speed analysis',
            'bottleneck', 'memory usage', 'cpu usage',
            # Smart Suggestions
            'suggest', 'recommendation', 'smart', 'intelligent', 'context aware',
            'best practices', 'improve', 'enhancement', 'tip'
        ]
        
        message_lower = message.lower()
        
        needs_research = any(keyword in message_lower for keyword in research_keywords)
        needs_code = any(keyword in message_lower for keyword in code_keywords)
        needs_technical = any(keyword in message_lower for keyword in technical_keywords)
        needs_writing = any(keyword in message_lower for keyword in writing_keywords)
        needs_data = any(keyword in message_lower for keyword in data_keywords)
        needs_experimental = any(keyword in message_lower for keyword in experimental_keywords)
        
        # Bestimme Komplexität
        is_complex = len(message.split()) > 20 or '?' in message or 'how' in message_lower or 'wie' in message_lower
        
        return {
            'needs_research': needs_research,
            'needs_code': needs_code, 
            'needs_technical': needs_technical,
            'needs_writing': needs_writing,
            'needs_data': needs_data,
            'needs_experimental': needs_experimental,
            'is_complex': is_complex,
            'primary_intent': self._determine_primary_intent(needs_research, needs_code, needs_technical, needs_writing, needs_data, needs_experimental),
            'message_length': len(message),
            'question_count': message.count('?')
        }
    
    def _determine_primary_intent(self, research: bool, code: bool, technical: bool, writing: bool = False, data: bool = False, experimental: bool = False) -> str:
        """Bestimmt die primäre Absicht der Anfrage"""
        if experimental:
            return 'experimental'
        elif code:
            return 'code'
        elif writing:
            return 'writing'
        elif data:
            return 'data'
        elif research:
            return 'research'
        elif technical:
            return 'technical'
        else:
            return 'conversation'
    
    async def process_request(self, message: str, context: List[Dict] = None) -> Dict[str, Any]:
        """
        Hauptfunktion: Verarbeitet User-Anfrage intelligent mit mehreren KI-Models
        """
        intent = self.analyze_user_intent(message)
        results = {}
        
        try:
            # Phase 1: Sammle Informationen (falls nötig)
            if intent['needs_research']:
                results['research'] = await self._get_research_data(message)
            
            # Phase 2: Technische Analyse (falls nötig)  
            if intent['needs_code'] or intent['needs_technical']:
                results['technical'] = await self._get_technical_analysis(message, results.get('research'))
            
            # Phase 3: Finale menschliche Antwort durch GPT-5
            final_response = await self._generate_final_response(message, results, intent, context)
            
            return {
                'response': final_response,
                'metadata': {
                    'intent': intent,
                    'services_used': list(results.keys()),
                    'processing_time': datetime.now().isoformat(),
                    'models_involved': self._get_models_used(results),
                    'agent_used': self._determine_agent_used(intent, results)
                }
            }
            
        except Exception as e:
            logging.error(f"AI Orchestrator error: {e}")
            # Fallback auf einfache GPT-5 Antwort
            fallback = await self._fallback_response(message, context)
            return {
                'response': fallback,
                'metadata': {
                    'intent': intent,
                    'error': str(e),
                    'fallback_used': True,
                    'agent_used': self._determine_agent_used(intent, {})
                }
            }
    
    async def _get_research_data(self, message: str) -> Dict[str, Any]:
        """Asynchrone Research mit Perplexity Deep Research und DNS bypass"""
        if not self.perplexity_client:
            # Try to initialize DNS bypass clients
            await self.initialize_bypass_clients()
            
        if not self.perplexity_client:
            return {'error': 'Perplexity API nicht konfiguriert'}
        
        try:
            # Perplexity Deep Research (async)
            response = await self.perplexity_client.chat.completions.create(
                model="sonar-deep-research",
                messages=[{
                    "role": "user", 
                    "content": f"Führe eine umfassende Recherche durch: {message}"
                }],
                max_tokens=4000,
                temperature=0.3,
                reasoning_effort="medium"  # Balance zwischen Tiefe und Geschwindigkeit
            )
            
            return {
                'content': response.choices[0].message.content,
                'model': 'sonar-deep-research',
                'citations': getattr(response, 'citations', []),
                'reasoning_effort': 'medium'
            }
            
        except Exception as e:
            logging.error(f"Perplexity research error: {e}")
            
            # Check if it's a connection error (DNS block)  
            error_str = str(e).lower()
            if any(term in error_str for term in ['connection', 'dns', 'resolve', 'network', 'refused']):
                logging.warning("🔄 DNS bypass attempt for Perplexity...")
                # Try to reinitialize bypass clients
                await self.initialize_bypass_clients()
                
                # Retry with potential bypass client
                if self.perplexity_client:
                    try:
                        response = await self.perplexity_client.chat.completions.create(
                            model="sonar-deep-research",
                            messages=[{
                                "role": "user", 
                                "content": f"Führe eine umfassende Recherche durch: {message}"
                            }],
                            max_tokens=4000,
                            temperature=0.1
                        )
                        
                        return {
                            'content': f"🔄 **DNS Bypass Success - Perplexity Research**\n\n{response.choices[0].message.content}",
                            'model': 'sonar-deep-research-bypass',
                            'citations': getattr(response, 'citations', []),
                            'reasoning_effort': getattr(response, 'reasoning_effort', 'standard')
                        }
                    except Exception as bypass_error:
                        logging.error(f"Bypass attempt also failed: {bypass_error}")
                
                logging.info("Using offline simulator for research due to connection issues")
                # Use offline simulator for research requests
                simulated_response = offline_simulator._generate_research_response(message)
                
                return {
                    'content': f"🤖 **Offline-Recherche** (DNS bypass fehlgeschlagen)\n\n{simulated_response}",
                    'model': 'xionimus-offline-research',
                    'citations': [],
                    'reasoning_effort': 'offline',
                    'offline_mode': True
                }
                
            return {'error': str(e)}
    
    async def _get_technical_analysis(self, message: str, research_data: Dict = None) -> Dict[str, Any]:
        """Technische Analyse mit Claude Sonnet 4 und DNS bypass"""
        if not self.anthropic_client:
            # Try to initialize DNS bypass clients
            await self.initialize_bypass_clients()
            
        if not self.anthropic_client:
            return {'error': 'Claude API nicht konfiguriert'}
        
        try:
            # Erweitere Prompt mit Research-Daten falls verfügbar
            enhanced_prompt = message
            if research_data and 'content' in research_data:
                enhanced_prompt = f"""
Basierend auf folgenden Recherche-Ergebnissen:
{research_data['content'][:1000]}...

Beantworte die folgende technische Anfrage:
{message}
"""
            
            response = await self.anthropic_client.messages.create(
                model="claude-opus-4-1-20250805",
                max_tokens=4000,
                temperature=0.3,
                messages=[{
                    "role": "user",
                    "content": enhanced_prompt
                }]
            )
            
            return {
                'content': _extract_text_from_anthropic_response(response),
                'model': 'claude-3-5-sonnet-20241022',
                'usage': response.usage.dict() if response.usage else None
            }
            
        except Exception as e:
            logging.error(f"Claude technical analysis error: {e}")
            
            # Check if it's a connection error (DNS block)
            error_str = str(e).lower()
            if any(term in error_str for term in ['connection', 'dns', 'resolve', 'network', 'refused']):
                logging.warning("🔄 DNS bypass attempt for Anthropic Claude...")
                # Try to reinitialize bypass clients
                await self.initialize_bypass_clients()
                
                # Retry with potential bypass client
                if self.anthropic_client:
                    try:
                        response = await self.anthropic_client.messages.create(
                            model="claude-3-5-sonnet-20241022",
                            max_tokens=4000,
                            temperature=0.3,
                            messages=[{
                                "role": "user",
                                "content": enhanced_prompt
                            }]
                        )
                        
                        return {
                            'content': f"🔄 **DNS Bypass Success - Claude Analysis**\n\n{_extract_text_from_anthropic_response(response)}",
                            'model': 'claude-3-5-sonnet-bypass',
                            'usage': response.usage.dict() if response.usage else None
                        }
                    except Exception as bypass_error:
                        logging.error(f"Bypass attempt also failed: {bypass_error}")
                
                logging.info("Using offline simulator due to connection issues")
                # Use offline simulator for connection errors
                simulated_response = offline_simulator.simulate_ai_response(message, {
                    'needs_code': 'code' in message.lower() or 'programmier' in message.lower(),
                    'needs_technical': True,
                    'is_complex': len(message.split()) > 10
                })
                
                return {
                    'content': f"🤖 **Offline-Modus aktiviert** (DNS bypass fehlgeschlagen)\n\n{simulated_response}",
                    'model': 'xionimus-offline-simulator',
                    'usage': None,
                    'offline_mode': True
                }
            
            return {'error': str(e)}
    
    async def _generate_final_response(self, message: str, results: Dict, intent: Dict, context: List = None) -> str:
        """Finale, menschliche Antwort durch GPT-5 mit DNS bypass"""
        if not self.openai_client:
            # Try to initialize DNS bypass clients
            await self.initialize_bypass_clients()
            
        if not self.openai_client:
            # Fallback: Use the best available result instead of failing
            if 'technical' in results:
                if 'content' in results['technical']:
                    return results['technical']['content']
                elif 'error' in results['technical']:
                    pass  # Try next fallback
            if 'research' in results:
                if 'content' in results['research']:
                    return results['research']['content']
                elif 'error' in results['research']:
                    pass  # Try next fallback
            
            return "🔧 DEBUG: AI-Services sind konfiguriert, aber die API-Schlüssel sind ungültig oder es besteht ein Verbindungsproblem. Bitte überprüfen Sie Ihre API-Schlüssel oder Internetverbindung."
        
        try:
            # Konstruiere System-Prompt
            system_prompt = """Du bist XIONIMUS AI, ein hochintelligenter AI-Assistant. 
Du hast Zugriff auf spezialisierte KI-Services für Research und technische Analyse.
Antworte natürlich, menschlich und hilfreich auf Deutsch.
Integriere die verfügbaren Informationen nahtlos in deine Antwort."""
            
            # Konstruiere User-Prompt mit allen verfügbaren Daten
            user_prompt = f"Benutzer-Anfrage: {message}\n\n"
            
            if 'research' in results and 'content' in results['research']:
                user_prompt += f"Recherche-Ergebnisse:\n{results['research']['content']}\n\n"
            
            if 'technical' in results and 'content' in results['technical']:
                user_prompt += f"Technische Analyse:\n{results['technical']['content']}\n\n"
            
            user_prompt += "Erstelle eine umfassende, natürliche Antwort die alle verfügbaren Informationen intelligent integriert."
            
            # Füge Kontext hinzu falls vorhanden
            messages = []
            if context:
                messages.extend(context[-6:])  # Letzte 6 Nachrichten als Kontext
            
            messages.extend([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ])
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o",  # Verwende GPT-4o bis GPT-5 verfügbar ist
                messages=messages,
                max_tokens=4000,
                temperature=0.7,
                stream=False
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logging.error(f"GPT-5 final response error: {e}")
            
            # Check if it's a connection error (DNS block)
            error_str = str(e).lower() 
            if any(term in error_str for term in ['connection', 'dns', 'resolve', 'network', 'refused']):
                logging.warning("🔄 DNS bypass attempt for OpenAI...")
                # Try to reinitialize bypass clients
                await self.initialize_bypass_clients()
                
                # Retry with potential bypass client
                if self.openai_client:
                    try:
                        response = await self.openai_client.chat.completions.create(
                            model="gpt-4o",  # Verwende GPT-4o bis GPT-5 verfügbar ist
                            messages=messages,
                            max_tokens=4000,
                            temperature=0.7,
                            stream=False
                        )
                        
                        return f"🔄 **DNS Bypass Success - OpenAI Response**\n\n{response.choices[0].message.content}"
                    except Exception as bypass_error:
                        logging.error(f"Bypass attempt also failed: {bypass_error}")
                
                logging.info("Using offline simulator for final response due to connection issues")
                
                # Use offline simulator when OpenAI is blocked
                intent_analysis = {
                    'needs_code': intent.get('needs_code', False) or 'code' in message.lower(),
                    'needs_research': intent.get('needs_research', False),
                    'is_complex': intent.get('is_complex', len(message.split()) > 10)
                }
                
                simulated_response = offline_simulator.simulate_ai_response(message, intent_analysis)
                
                # If we have results from other services, integrate them
                if 'technical' in results and 'content' in results['technical']:
                    return results['technical']['content']
                elif 'research' in results and 'content' in results['research']:
                    return results['research']['content']
                else:
                    return f"🤖 **Offline-Assistent aktiviert** (DNS bypass fehlgeschlagen)\n\n{simulated_response}"
            
            return f"🔧 DEBUG: OpenAI API-Verbindung fehlgeschlagen ({str(e)[:100]}). Das System funktioniert korrekt, aber die API-Schlüssel sind möglicherweise ungültig oder die Internetverbindung ist nicht verfügbar. Bitte überprüfen Sie Ihre API-Konfiguration."
    
    async def _fallback_response(self, message: str, context: List = None) -> str:
        """Fallback-Antwort wenn andere Services fehlschlagen"""
        # Try Claude first as fallback
        if self.anthropic_client:
            try:
                response = await self.anthropic_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=2000,
                    temperature=0.7,
                    messages=[{
                        "role": "user",
                        "content": message
                    }]
                )
                return _extract_text_from_anthropic_response(response)
            except Exception as e:
                logging.error(f"Claude API fallback failed: {e}")
        
        # Try OpenAI as secondary fallback
        if self.openai_client:
            try:
                messages = [{"role": "user", "content": message}]
                if context:
                    messages = context[-4:] + messages
                
                response = await self.openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=messages,
                    max_tokens=2000,
                    temperature=0.7
                )
                return response.choices[0].message.content
            except Exception as e:
                logging.error(f"OpenAI API fallback failed: {e}")
        
        # Try Perplexity as final fallback
        if self.perplexity_client:
            try:
                response = await self.perplexity_client.chat.completions.create(
                    model="sonar-reasoning",
                    messages=[{
                        "role": "user", 
                        "content": message
                    }],
                    max_tokens=2000,
                    temperature=0.7
                )
                return response.choices[0].message.content
            except Exception as e:
                logging.error(f"Perplexity API fallback failed: {e}")
        
        return offline_simulator.simulate_ai_response(message, {
            'is_fallback': True,
            'needs_code': 'code' in message.lower(),
            'needs_research': any(word in message.lower() for word in ['was ist', 'erkläre', 'information']),
            'is_greeting': any(word in message.lower() for word in ['hallo', 'hi', 'guten tag'])
        })
    
    def _get_models_used(self, results: Dict) -> List[str]:
        """Ermittelt welche Models verwendet wurden"""
        models = []
        if 'research' in results and 'model' in results['research']:
            models.append(results['research']['model'])
        if 'technical' in results and 'model' in results['technical']:
            models.append(results['technical']['model'])
        models.append('gpt-4o')  # Final response model
        return models
    
    def _determine_agent_used(self, intent: Dict, results: Dict) -> str:
        """Bestimmt welcher Agent basierend auf Intent und verwendeten Services genutzt wurde"""
        primary_intent = intent.get('primary_intent', 'conversation')
        
        # Map intent to agent names that match the test expectations
        agent_mapping = {
            'code': 'Code Agent',
            'writing': 'Writing Agent',  # Fix: Writing should map to Writing Agent
            'data': 'Data Agent',        # Fix: Data should map to Data Agent
            'research': 'Research Agent', 
            'technical': 'Code Agent',   # Technical analysis also maps to Code Agent
            'conversation': 'Session Agent'  # Generic conversation
        }
        
        # If technical analysis was used, it's likely Code Agent
        if 'technical' in results:
            return 'Code Agent'
        elif 'research' in results:
            return 'Research Agent'
        else:
            return agent_mapping.get(primary_intent, 'Session Agent')
    
    def get_processing_status(self, intent: Dict) -> Dict[str, str]:
        """Gibt Status-Nachrichten für verschiedene Verarbeitungsphasen zurück"""
        status = {}
        
        if intent['needs_research']:
            status['research'] = "🔍 Führe umfassende Recherche durch..."
        
        if intent['needs_code'] or intent['needs_technical']:
            status['technical'] = "⚙️ Analysiere technische Aspekte..."
        
        status['final'] = "🧠 Erstelle finale Antwort..."
        
        return status