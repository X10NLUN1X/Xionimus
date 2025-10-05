"""
Auto-Routing Manager für Xionimus AI
Erkennt Unklarheiten/Probleme und leitet automatisch an passende Agenten weiter
Mit Loop-Prevention!
"""
import logging
from typing import Dict, Any, Optional, List, Set
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)

class AutoRoutingManager:
    """Manages automatic routing to specialized agents with loop prevention"""
    
    def __init__(self):
        # Track processed issues to prevent loops
        self.processed_issues: Set[str] = set()
        self.max_routing_depth = 2  # Maximum times to route the same issue
        
    def _get_issue_hash(self, issue_description: str, context: str = "") -> str:
        """Generate unique hash for an issue"""
        content = f"{issue_description}_{context}".lower()
        return hashlib.md5(content.encode(), usedforsecurity=False).hexdigest()[:16]
    
    def should_route_to_agent(
        self, 
        ai_response: str,
        user_request: str,
        session_context: List[Dict[str, str]]
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze if routing to specialized agent is needed
        
        Returns:
            Dict with routing info if routing needed, None otherwise
        """
        # Check for specific patterns that indicate need for specialized help
        routing_decision = self._detect_routing_need(ai_response, user_request)
        
        if not routing_decision:
            return None
        
        # Check if we've already processed this issue (loop prevention)
        issue_hash = self._get_issue_hash(
            routing_decision['reason'],
            user_request[:100]
        )
        
        if issue_hash in self.processed_issues:
            logger.info(f"🔄 Loop prevention: Issue {issue_hash} already processed")
            return None
        
        # Mark as processed
        self.processed_issues.add(issue_hash)
        
        # Add cleanup after 100 issues to prevent memory leak
        if len(self.processed_issues) > 100:
            logger.info("🧹 Cleaning up old processed issues")
            self.processed_issues.clear()
        
        logger.info(f"🎯 Routing decision: {routing_decision['agent']} - {routing_decision['reason']}")
        return routing_decision
    
    def _detect_routing_need(
        self,
        ai_response: str,
        user_request: str
    ) -> Optional[Dict[str, Any]]:
        """
        Detect if specialized agent is needed
        
        Returns:
            Routing info or None
        """
        response_lower = ai_response.lower()
        request_lower = user_request.lower()
        
        # Pattern 1: Testing needs
        if any(keyword in request_lower for keyword in ['test', 'bug', 'fehler', 'error', 'funktioniert nicht']):
            if 'code' in ai_response.lower() or '```' in ai_response:
                return {
                    'agent': 'testing',
                    'reason': 'Code wurde generiert, automatische Tests werden benötigt',
                    'priority': 'high'
                }
        
        # Pattern 2: Code quality/review needs
        if any(keyword in request_lower for keyword in ['review', 'qualität', 'verbessern', 'optimize']):
            return {
                'agent': 'code_review',
                'reason': 'Code-Review und Qualitätsverbesserung angefordert',
                'priority': 'medium'
            }
        
        # Pattern 3: Deployment needs
        if any(keyword in request_lower for keyword in ['deploy', 'docker', 'production', 'live']):
            if '```' in ai_response:  # Has code
                return {
                    'agent': 'deployment',
                    'reason': 'Deployment-Setup benötigt',
                    'priority': 'medium'
                }
        
        # Pattern 4: Documentation needs
        if any(keyword in request_lower for keyword in ['doku', 'readme', 'anleitung', 'documentation']):
            return {
                'agent': 'documentation',
                'reason': 'Dokumentation wird benötigt',
                'priority': 'low'
            }
        
        # Pattern 5: AI detected uncertainties
        uncertainty_indicators = [
            'ich bin nicht sicher',
            'könnte sein',
            'möglicherweise',
            'vielleicht',
            'eventuell',
            'i am not sure',
            'might be',
            'possibly'
        ]
        
        if any(indicator in response_lower for indicator in uncertainty_indicators):
            return {
                'agent': 'clarification',
                'reason': 'AI zeigt Unsicherheit, Klärung benötigt',
                'priority': 'high'
            }
        
        # Pattern 6: Incomplete response
        if len(ai_response) < 100 and '```' not in ai_response:
            return {
                'agent': 'expansion',
                'reason': 'Antwort scheint unvollständig zu sein',
                'priority': 'medium'
            }
        
        # No routing needed
        return None
    
    def get_agent_prompt(self, routing_info: Dict[str, Any], original_request: str) -> str:
        """
        Generate prompt for specialized agent based on routing decision
        """
        agent = routing_info['agent']
        reason = routing_info['reason']
        
        prompts = {
            'testing': f"""Als Testing-Experte:

Original-Anfrage: {original_request}
Grund: {reason}

Deine Aufgabe:
1. Erstelle vollständige automatische Tests (Unit + Integration)
2. Füge Test-Framework-Konfiguration hinzu
3. Stelle sicher, dass alle Edge-Cases getestet werden
4. Gebe konkrete Test-Ergebnisse zurück

Format: Vollständige Test-Dateien mit Erklärung.""",

            'code_review': f"""Als Code-Review-Experte:

Original-Anfrage: {original_request}
Grund: {reason}

Deine Aufgabe:
1. Analysiere Code-Qualität (Performance, Security, Best Practices)
2. Identifiziere Verbesserungspotenziale
3. Gebe konkrete Verbesserungsvorschläge mit Code-Beispielen
4. Priorisiere Änderungen (Critical/High/Medium/Low)""",

            'deployment': f"""Als Deployment-Experte:

Original-Anfrage: {original_request}
Grund: {reason}

Deine Aufgabe:
1. Erstelle Dockerfile und docker-compose.yml
2. Füge CI/CD-Pipeline-Konfiguration hinzu (.github/workflows)
3. Erstelle Deployment-Dokumentation
4. Inkludiere Environment-Variable-Setup""",

            'documentation': f"""Als Dokumentations-Experte:

Original-Anfrage: {original_request}
Grund: {reason}

Deine Aufgabe:
1. Erstelle vollständige README.md
2. API-Dokumentation
3. Setup-Anleitung
4. Verwendungs-Beispiele""",

            'clarification': f"""Als Klarstellungs-Experte:

Original-Anfrage: {original_request}
Grund: {reason}

Deine Aufgabe:
1. Analysiere die Unsicherheit in der vorherigen Antwort
2. Recherchiere und finde die korrekte Information
3. Gebe eine klare, sichere Antwort
4. Erkläre, warum die vorherige Antwort unsicher war""",

            'expansion': f"""Als Erweiterungs-Experte:

Original-Anfrage: {original_request}
Grund: {reason}

Deine Aufgabe:
1. Erweitere die unvollständige Antwort
2. Füge alle fehlenden Details hinzu
3. Gebe eine vollständige, umfassende Antwort
4. Inkludiere Beispiele und Best Practices"""
        }
        
        return prompts.get(agent, f"Original Anfrage: {original_request}\n\nBitte bearbeite diese Anfrage vollständig.")

# Global instance
auto_routing_manager = AutoRoutingManager()
