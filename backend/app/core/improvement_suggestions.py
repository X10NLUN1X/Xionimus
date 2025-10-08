"""
Improvement Suggestions Generator für Xionimus AI
Generiert automatische Verbesserungsvorschläge nach jeder Antwort
"""
import logging
from typing import List, Dict, Any, Optional
import re

logger = logging.getLogger(__name__)

class ImprovementSuggestionsGenerator:
    """Generates improvement suggestions based on AI response"""
    
    def __init__(self):
        pass
    
    def generate_suggestions(
        self, 
        ai_response: str, 
        user_request: str,
        code_blocks_count: int = 0
    ) -> str:
        """
        Generate 2-3 concrete improvement suggestions
        
        Args:
            ai_response: The AI's response content
            user_request: The user's original request
            code_blocks_count: Number of code blocks generated
            
        Returns:
            Formatted suggestions string
        """
        suggestions = []
        
        # Analyze what was done
        has_code = code_blocks_count > 0
        has_explanation = len(ai_response) > 200
        is_coding_request = self._is_coding_related(user_request)
        
        # Generate contextual suggestions
        if has_code:
            suggestions.extend(self._code_related_suggestions(code_blocks_count))
        
        if is_coding_request and not has_code:
            suggestions.append({
                "title": "💡 Code-Generierung",
                "description": "Soll ich vollständigen, lauffähigen Code mit Best Practices erstellen?"
            })
        
        # Always suggest testing if code was generated
        if has_code:
            suggestions.append({
                "title": "🧪 Testing & Qualität",
                "description": "Soll ich automatische Tests erstellen und die Code-Qualität prüfen?"
            })
        
        # Suggest improvements based on response length
        if has_explanation and has_code:
            suggestions.append({
                "title": "📚 Dokumentation",
                "description": "Möchten Sie eine README.md mit Setup-Anleitung und API-Dokumentation?"
            })
        
        # Performance suggestions
        if has_code:
            suggestions.append({
                "title": "⚡ Performance-Optimierung",
                "description": "Soll ich Performance-Bottlenecks analysieren und Optimierungen vorschlagen?"
            })
        
        # Security suggestions
        if has_code:
            suggestions.append({
                "title": "🔒 Security-Audit",
                "description": "Möchten Sie ein automatisches Security-Audit mit Schwachstellen-Analyse?"
            })
        
        # Deployment suggestions
        if has_code and code_blocks_count > 2:
            suggestions.append({
                "title": "🚀 Deployment-Setup",
                "description": "Soll ich Docker-Container, CI/CD-Pipeline und Deployment-Konfiguration erstellen?"
            })
        
        # Take top 3 most relevant
        top_suggestions = suggestions[:3]
        
        if not top_suggestions:
            # Fallback: generic suggestions
            return self._generic_suggestions()
        
        # Format suggestions
        formatted = "\n\n---\n\n## 💡 Nächste Schritte - Verbesserungsvorschläge\n\n"
        formatted += "Ich kann Ihr Projekt weiter verbessern:\n\n"
        
        for i, suggestion in enumerate(top_suggestions, 1):
            formatted += f"**{i}. {suggestion['title']}**\n"
            formatted += f"   {suggestion['description']}\n\n"
        
        formatted += "*Teilen Sie mir einfach mit, welche Verbesserung Sie wünschen, oder stellen Sie eine neue Frage!*"
        
        return formatted
    
    def _is_coding_related(self, text: str) -> bool:
        """Check if request is coding-related"""
        coding_keywords = [
            'code', 'function', 'class', 'app', 'website', 'api', 
            'script', 'program', 'entwickle', 'erstelle', 'programmiere',
            'build', 'create', 'implement', 'backend', 'frontend'
        ]
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in coding_keywords)
    
    def _code_related_suggestions(self, code_blocks_count: int) -> List[Dict[str, str]]:
        """Generate code-specific suggestions"""
        suggestions = []
        
        if code_blocks_count == 1:
            suggestions.append({
                "title": "📦 Projekt-Struktur",
                "description": "Soll ich eine vollständige Projekt-Struktur mit allen notwendigen Komponenten erstellen?"
            })
        
        if code_blocks_count >= 2:
            suggestions.append({
                "title": "🎨 UI/UX Verbesserung",
                "description": "Möchten Sie ein modernes Design mit Animationen und responsivem Layout?"
            })
        
        return suggestions
    
    def _generic_suggestions(self) -> str:
        """Generic suggestions if nothing specific found"""
        return """

---

## 💡 Wie kann ich weiterhelfen?

**1. 🔍 Vertiefte Erklärung**
   Möchten Sie eine detailliertere Erklärung mit Beispielen?

**2. 🎯 Praktische Anwendung**
   Soll ich zeigen, wie Sie dies in einem konkreten Projekt nutzen können?

**3. 📚 Weiterführende Themen**
   Interessieren Sie sich für verwandte Themen oder erweiterte Konzepte?

*Stellen Sie einfach Ihre nächste Frage!*
"""

# Global instance
improvement_suggestions_generator = ImprovementSuggestionsGenerator()
