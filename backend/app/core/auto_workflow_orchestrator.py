"""
Auto-Workflow-Orchestrator für Xionimus AI
Automatisiert den kompletten Workflow von Research → Klärung → Code-Generierung
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import re

logger = logging.getLogger(__name__)

class AutoWorkflowOrchestrator:
    """
    Orchestriert automatischen Workflow ohne User-Input
    Research → Auto-Klärungsfragen → Code-Generierung
    """
    
    def __init__(self):
        self.workflow_state: Dict[str, Any] = {}
    
    async def should_auto_continue(
        self,
        ai_response: str,
        conversation_history: List[Dict[str, str]]
    ) -> Optional[Dict[str, Any]]:
        """
        Prüft, ob automatische Fortsetzung nötig ist
        
        Returns:
            Dict mit auto_continue action oder None
        """
        # Check 1: Research abgeschlossen + Klärungsfragen vorhanden
        if self._has_research_and_questions(ai_response):
            logger.info("🎯 Research + Klärungsfragen erkannt → Auto-Continue")
            return {
                'action': 'auto_answer_clarifications',
                'reason': 'Research abgeschlossen mit Klärungsfragen',
                'original_request': self._extract_original_request(conversation_history)
            }
        
        # Check 2: Klärungsfragen beantwortet → Code-Generierung
        if self._questions_answered_waiting_for_code(ai_response):
            logger.info("🎯 Klärungsfragen beantwortet → Auto-Code-Generierung")
            return {
                'action': 'auto_generate_code',
                'reason': 'Klärungsfragen beantwortet, bereit für Code',
                'requirements': self._extract_requirements(conversation_history)
            }
        
        return None
    
    def _has_research_and_questions(self, text: str) -> bool:
        """Prüft ob Research + Klärungsfragen vorhanden"""
        indicators = [
            'recherche abgeschlossen' in text.lower(),
            'research completed' in text.lower(),
            'klärungsfragen' in text.lower(),
            'clarifying questions' in text.lower(),
            'basierend auf dieser recherche' in text.lower()
        ]
        
        # Muss Research + Fragen haben
        has_research = any([
            'recherche' in text.lower(),
            'research' in text.lower()
        ])
        
        has_questions = any([
            '?' in text,
            'frage' in text.lower(),
            'question' in text.lower()
        ])
        
        return has_research and has_questions and any(indicators)
    
    def _questions_answered_waiting_for_code(self, text: str) -> bool:
        """Prüft ob Fragen beantwortet und auf Code wartet"""
        # Noch nicht implementiert - für zukünftige Erweiterung
        return False
    
    def _extract_original_request(self, history: List[Dict[str, str]]) -> str:
        """Extrahiert ursprüngliche Coding-Anfrage"""
        # Suche letzte User-Message vor Research
        for msg in reversed(history):
            if msg.get('role') == 'user':
                content = msg.get('content', '')
                # Skip "fahre fort" oder ähnliche Meta-Commands
                if len(content) > 30 and not any(skip in content.lower() for skip in ['fahre fort', 'continue', 'weiter']):
                    return content
        return ""
    
    def _extract_requirements(self, history: List[Dict[str, str]]) -> Dict[str, Any]:
        """Extrahiert Requirements aus Conversation"""
        requirements = {
            'features': [],
            'tech_stack': [],
            'constraints': []
        }
        # Placeholder für zukünftige Implementierung
        return requirements
    
    async def auto_answer_clarifications(
        self,
        research_content: str,
        clarification_questions: str,
        original_request: str,
        ai_manager
    ) -> str:
        """
        Beantwortet Klärungsfragen automatisch basierend auf Best Practices
        
        Args:
            research_content: Research-Ergebnisse
            clarification_questions: Die gestellten Fragen
            original_request: Ursprüngliche User-Anfrage
            ai_manager: AI Manager für LLM-Calls
            
        Returns:
            Automatisch generierte Antworten
        """
        logger.info("🤖 Generiere automatische Antworten auf Klärungsfragen...")
        
        # Erstelle Prompt für automatische Beantwortung
        auto_answer_prompt = f"""Als Experte für Software-Entwicklung, beantworte die folgenden Klärungsfragen AUTOMATISCH basierend auf Best Practices und modernen Standards.

**Ursprüngliche Anfrage:**
{original_request}

**Research-Ergebnisse:**
{research_content[:1000]}...

**Klärungsfragen:**
{clarification_questions}

**Deine Aufgabe:**
Beantworte ALLE Fragen präzise und praxisorientiert. Wähle moderne, bewährte Technologien und Best Practices.

**Antwort-Format:**
Für jede Frage:
1. [Frage-Nummer] **Kurze Antwort**
   - Begründung in 1-2 Sätzen

**Richtlinien:**
- Wähle moderne Tech-Stack (React 18+, Node.js, TypeScript wenn möglich)
- Bevorzuge populäre, gut dokumentierte Libraries
- Fokus auf Developer Experience und Maintainability
- Setze auf bewährte Patterns (REST API, Component-based)
- Implementiere Best Practices (Error-Handling, Testing, Security)

Gebe NUR die Antworten, keine weitere Erklärung."""

        try:
            # Verwende Claude für intelligente Beantwortung
            response = await ai_manager.generate_response(
                provider="anthropic",
                model="claude-sonnet-4-5-20250929",
                messages=[{"role": "user", "content": auto_answer_prompt}],
                stream=False,
                temperature=0.7
            )
            
            answers = response.get("content", "")
            logger.info(f"✅ Automatische Antworten generiert: {len(answers)} Zeichen")
            return answers
            
        except Exception as e:
            logger.error(f"❌ Fehler bei Auto-Beantwortung: {e}")
            # Fallback: Generische Best-Practice Antworten
            return self._generate_fallback_answers()
    
    def _generate_fallback_answers(self) -> str:
        """Generiert generische Best-Practice Antworten als Fallback"""
        return """Basierend auf modernen Best Practices:

1. **Programmiersprache/Framework**: React 18 mit TypeScript, Node.js Backend
2. **Architektur**: Full-Stack (React Frontend + REST API Backend)
3. **Design**: Material-UI oder Chakra UI für modernes, responsives Design
4. **Authentifizierung**: JWT-basiert mit Refresh Tokens
5. **Datenbank**: MongoDB oder PostgreSQL (basierend auf Anforderungen)
6. **Features**: Vollständige CRUD-Operationen, Real-time Updates, Error-Handling"""
    
    async def execute_auto_workflow(
        self,
        workflow_action: Dict[str, Any],
        ai_manager,
        api_keys: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Führt automatischen Workflow aus
        
        Returns:
            Dict mit Ergebnis und nächster Message
        """
        action = workflow_action['action']
        
        if action == 'auto_answer_clarifications':
            # Schritt 1: Beantworte Fragen automatisch
            # Schritt 2: Generiere Code direkt
            logger.info("🚀 Starte Auto-Workflow: Research → Antworten → Code")
            
            return {
                'success': True,
                'next_message': 'Basierend auf Best Practices starte ich nun automatisch mit der Code-Generierung...',
                'should_generate_code': True
            }
        
        return {
            'success': False,
            'next_message': None
        }

# Global instance
auto_workflow_orchestrator = AutoWorkflowOrchestrator()
