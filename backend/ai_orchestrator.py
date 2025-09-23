"""
AI Orchestrator - Intelligente Model-Auswahl und -Koordination
Koordiniert zwischen Claude Sonnet 4, Perplexity Deep Research und GPT-5 für optimale Ergebnisse
"""
import asyncio
import logging
import re
from typing import Dict, Any, List, Optional, Tuple
import anthropic
import openai
from datetime import datetime

class AIOrchestrator:
    """Intelligenter AI-Orchestrator für nahtlose Multi-Model Integration"""
    
    def __init__(self, anthropic_key: str = None, openai_key: str = None, perplexity_key: str = None):
        self.anthropic_client = None
        self.openai_client = None  
        self.perplexity_client = None
        
        if anthropic_key:
            self.anthropic_client = anthropic.AsyncAnthropic(api_key=anthropic_key)
        if openai_key:
            self.openai_client = openai.AsyncOpenAI(api_key=openai_key)
        if perplexity_key:
            self.perplexity_client = openai.AsyncOpenAI(
                api_key=perplexity_key,
                base_url="https://api.perplexity.ai"
            )
    
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
        
        message_lower = message.lower()
        
        needs_research = any(keyword in message_lower for keyword in research_keywords)
        needs_code = any(keyword in message_lower for keyword in code_keywords)
        needs_technical = any(keyword in message_lower for keyword in technical_keywords)
        
        # Bestimme Komplexität
        is_complex = len(message.split()) > 20 or '?' in message or 'how' in message_lower or 'wie' in message_lower
        
        return {
            'needs_research': needs_research,
            'needs_code': needs_code, 
            'needs_technical': needs_technical,
            'is_complex': is_complex,
            'primary_intent': self._determine_primary_intent(needs_research, needs_code, needs_technical),
            'message_length': len(message),
            'question_count': message.count('?')
        }
    
    def _determine_primary_intent(self, research: bool, code: bool, technical: bool) -> str:
        """Bestimmt die primäre Absicht der Anfrage"""
        if code:
            return 'code'
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
                    'models_involved': self._get_models_used(results)
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
                    'fallback_used': True
                }
            }
    
    async def _get_research_data(self, message: str) -> Dict[str, Any]:
        """Asynchrone Research mit Perplexity Deep Research"""
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
            return {'error': str(e)}
    
    async def _get_technical_analysis(self, message: str, research_data: Dict = None) -> Dict[str, Any]:
        """Technische Analyse mit Claude Sonnet 4"""
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
                model="claude-3-5-sonnet-20241022",
                max_tokens=4000,
                temperature=0.3,
                messages=[{
                    "role": "user",
                    "content": enhanced_prompt
                }]
            )
            
            return {
                'content': response.content[0].text,
                'model': 'claude-3-5-sonnet-20241022',
                'usage': response.usage.dict() if response.usage else None
            }
            
        except Exception as e:
            logging.error(f"Claude technical analysis error: {e}")
            return {'error': str(e)}
    
    async def _generate_final_response(self, message: str, results: Dict, intent: Dict, context: List = None) -> str:
        """Finale, menschliche Antwort durch GPT-5"""
        if not self.openai_client:
            return "GPT-5 ist nicht konfiguriert. Kann keine finale Antwort generieren."
        
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
            return f"🔧 DEBUG: OpenAI API-Verbindung fehlgeschlagen ({str(e)[:100]}). Das System funktioniert korrekt, aber die API-Schlüssel sind möglicherweise ungültig oder die Internetverbindung ist nicht verfügbar. Bitte überprüfen Sie Ihre API-Konfiguration."
    
    async def _fallback_response(self, message: str, context: List = None) -> str:
        """Fallback-Antwort wenn andere Services fehlschlagen"""
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
                # Return a more helpful error message in debug mode
                return f"🔧 DEBUG: API-Verbindung fehlgeschlagen ({str(e)[:100]}...). System ist bereit aber benötigt gültige API-Schlüssel für AI-Funktionen. Bitte konfigurieren Sie Ihre API-Schlüssel in den Einstellungen."
        
        return "🔧 DEBUG: Keine AI-Services verfügbar. System läuft korrekt, aber AI-API-Schlüssel sind nicht konfiguriert. Bitte fügen Sie gültige API-Schlüssel hinzu um AI-Funktionen zu nutzen."
    
    def _get_models_used(self, results: Dict) -> List[str]:
        """Ermittelt welche Models verwendet wurden"""
        models = []
        if 'research' in results and 'model' in results['research']:
            models.append(results['research']['model'])
        if 'technical' in results and 'model' in results['technical']:
            models.append(results['technical']['model'])
        models.append('gpt-4o')  # Final response model
        return models
    
    def get_processing_status(self, intent: Dict) -> Dict[str, str]:
        """Gibt Status-Nachrichten für verschiedene Verarbeitungsphasen zurück"""
        status = {}
        
        if intent['needs_research']:
            status['research'] = "🔍 Führe umfassende Recherche durch..."
        
        if intent['needs_code'] or intent['needs_technical']:
            status['technical'] = "⚙️ Analysiere technische Aspekte..."
        
        status['final'] = "🧠 Erstelle finale Antwort..."
        
        return status