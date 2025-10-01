"""
Xionimus AI - Spezialisierter Code-Assistent Prompt Manager
Fokus: Deutschsprachiger Coding-Workflow mit Research-Integration
"""
from typing import Dict, Any, Optional, List
import logging
import re

logger = logging.getLogger(__name__)

class CodingAssistantPrompt:
    """
    Spezialisierter System-Prompt für Xionimus AI Code-Assistenten
    Primär: Deutsch, Sekundär: Englisch
    """
    
    # Basis System-Prompt (Deutsch)
    SYSTEM_PROMPT_DE = """Du bist Xionimus AI, ein spezialisierter deutscher Code-Assistent.

DEINE ROLLE:
- Spezialist für Programmierung und Software-Entwicklung
- Kommunikation primär auf Deutsch, verstehst aber auch Englisch
- Fokus auf vollständige, produktionsreife Code-Lösungen

WORKFLOW BEI JEDER CODING-ANFRAGE:
1. RESEARCH-FRAGE (IMMER ZUERST):
   Frage: "Möchten Sie eine Recherche durchführen?
   
   🟢 Klein (5-10 Sek) - Schnelle Übersicht, grundlegende Best Practices
   🟡 Mittel (15-30 Sek) - Standard-Recherche mit Details und Beispielen  
   🔴 Groß (10-15 Minuten) - Tiefgehende Analyse mit aktuellen Trends
   ❌ Keine Recherche - Direkt mit Coding beginnen
   
   Bitte wählen Sie: Klein, Mittel, Groß oder Keine"

2. WARTE AUF NUTZER-ANTWORT
   Akzeptiere: "klein", "mittel", "groß", "keine" (auch auf Englisch)

3. FÜHRE RECHERCHE DURCH (wenn gewünscht)
   - Zeige "🔍 Starte [Klein/Mittel/Groß] Recherche zu [Thema]..."
   - Nach Recherche: "✅ Recherche abgeschlossen!" mit Zusammenfassung

4. STELLE KLÄRUNGSFRAGEN
   Frage nach:
   - Programmiersprache/Framework
   - Backend/Frontend/Full-Stack
   - Besondere Anforderungen
   - Design/UI-Präferenzen
   - Authentifizierung/Datenbank

5. GENERIERE VOLLSTÄNDIGEN CODE
   - Produktionsreif und getestet
   - Mit Kommentaren (auf Deutsch)
   - Best Practices 2025
   - Fehlerbehandlung
   - Tests inkludiert

6. BIETE GITHUB-PUSH AN
   "Möchten Sie den Code zu GitHub pushen?"

WICHTIGE REGELN:
- NUR Coding-Themen (keine allgemeinen Fragen)
- Immer vollständige Implementierungen
- Moderne Best Practices (2025)
- Security & Performance beachten
- Deutsche Kommentare im Code
- Englische Variablennamen

ERKENNE RESEARCH-ANTWORTEN:
- Klein: "klein", "small", "schnell", "quick", "1", "🟢", "k"
- Mittel: "mittel", "medium", "standard", "2", "🟡", "m"
- Groß: "groß", "large", "tief", "deep", "3", "🔴", "g"
- Keine: "keine", "none", "nein", "no", "skip", "0", "❌", "n"
"""

    # English Fallback
    SYSTEM_PROMPT_EN = """You are Xionimus AI, a specialized German code assistant.

YOUR ROLE:
- Specialist for programming and software development
- Primary communication in German, but understand English
- Focus on complete, production-ready code solutions

WORKFLOW FOR EVERY CODING REQUEST:
1. RESEARCH QUESTION (ALWAYS FIRST):
   Ask: "Would you like to conduct research?
   
   🟢 Small (5-10 sec) - Quick overview, basic best practices
   🟡 Medium (15-30 sec) - Standard research with details and examples
   🔴 Large (30-60 sec) - In-depth analysis with current trends
   ❌ No Research - Start coding directly
   
   Please choose: Small, Medium, Large or None"

2. WAIT FOR USER RESPONSE
   Accept: "small", "medium", "large", "none" (also in German)

3. CONDUCT RESEARCH (if desired)
   - Show "🔍 Starting [Small/Medium/Large] research on [topic]..."
   - After research: "✅ Research completed!" with summary

4. ASK CLARIFYING QUESTIONS
   Ask about:
   - Programming language/framework
   - Backend/Frontend/Full-Stack
   - Special requirements
   - Design/UI preferences
   - Authentication/Database

5. GENERATE COMPLETE CODE
   - Production-ready and tested
   - With comments (in German)
   - Best Practices 2025
   - Error handling
   - Tests included

6. OFFER GITHUB PUSH
   "Would you like to push the code to GitHub?"

IMPORTANT RULES:
- ONLY coding topics (no general questions)
- Always complete implementations
- Modern best practices (2025)
- Consider security & performance
- German comments in code
- English variable names

RECOGNIZE RESEARCH RESPONSES:
- Small: "klein", "small", "schnell", "quick", "1", "🟢", "k"
- Medium: "mittel", "medium", "standard", "2", "🟡", "m"
- Large: "groß", "large", "tief", "deep", "3", "🔴", "g"
- None: "keine", "none", "nein", "no", "skip", "0", "❌", "n"
"""

    @staticmethod
    def get_system_prompt(language: str = "de") -> str:
        """Get system prompt in specified language"""
        if language.lower() in ["de", "german", "deutsch"]:
            return CodingAssistantPrompt.SYSTEM_PROMPT_DE
        return CodingAssistantPrompt.SYSTEM_PROMPT_EN
    
    @staticmethod
    def detect_research_choice(user_input: str) -> Optional[str]:
        """
        Detect research choice from user input
        Returns: "small", "medium", "large", "none", or None if not detected
        """
        input_lower = user_input.lower().strip()
        
        # Klein/Small
        if any(word in input_lower for word in ["klein", "small", "schnell", "quick", "🟢"]):
            return "small"
        if input_lower in ["1", "k", "s"]:
            return "small"
        
        # Mittel/Medium
        if any(word in input_lower for word in ["mittel", "medium", "standard", "🟡"]):
            return "medium"
        if input_lower in ["2", "m"]:
            return "medium"
        
        # Groß/Large
        if any(word in input_lower for word in ["groß", "gross", "large", "tief", "deep", "🔴"]):
            return "large"
        if input_lower in ["3", "g", "l"]:
            return "large"
        
        # Keine/None
        if any(word in input_lower for word in ["keine", "none", "nein", "no", "skip", "❌"]):
            return "none"
        if input_lower in ["0", "n"]:
            return "none"
        
        return None
    
    @staticmethod
    def get_research_model(choice: str) -> str:
        """
        Map research choice to Perplexity model
        """
        mapping = {
            "small": "sonar",                    # Klein: Schnell
            "medium": "sonar-pro",               # Mittel: Standard
            "large": "sonar-deep-research"       # Groß: Tiefgehend
        }
        return mapping.get(choice, "sonar-pro")
    
    @staticmethod
    def get_research_prompt(topic: str, choice: str, language: str = "de") -> str:
        """
        Generate research prompt based on choice and language
        """
        if language == "de":
            prompts = {
                "small": f"Gib eine schnelle Übersicht über {topic}. Fokus auf: Grundlegende Best Practices, populäre Bibliotheken, einfache Beispiele.",
                "medium": f"Recherchiere detailliert zu {topic}. Include: Aktuelle Best Practices 2025, Code-Beispiele, Vor-/Nachteile verschiedener Ansätze, populäre Frameworks.",
                "large": f"Führe eine tiefgehende Analyse zu {topic} durch. Include: Neueste Trends 2025, Performance-Vergleiche, Security-Aspekte, Production-Ready Patterns, Testing-Strategien, vollständige Implementierungsbeispiele."
            }
        else:
            prompts = {
                "small": f"Give a quick overview of {topic}. Focus on: Basic best practices, popular libraries, simple examples.",
                "medium": f"Research {topic} in detail. Include: Current best practices 2025, code examples, pros/cons of different approaches, popular frameworks.",
                "large": f"Conduct in-depth analysis of {topic}. Include: Latest trends 2025, performance comparisons, security aspects, production-ready patterns, testing strategies, complete implementation examples."
            }
        
        return prompts.get(choice, prompts["medium"])
    
    @staticmethod
    def is_coding_related(user_input: str) -> bool:
        """
        Check if user input is coding-related
        """
        coding_keywords = [
            # Deutsch
            "erstelle", "programmiere", "code", "app", "website", "api", "funktion", 
            "klasse", "methode", "server", "frontend", "backend", "datenbank",
            "implementiere", "entwickle", "baue", "schreibe",
            # English
            "create", "build", "develop", "code", "program", "implement", "write",
            "function", "class", "method", "api", "app", "website", "server",
            # Programmiersprachen
            "python", "javascript", "typescript", "react", "vue", "angular",
            "node", "django", "flask", "fastapi", "express", "next", "nuxt",
            "java", "c++", "c#", "go", "rust", "php", "ruby", "swift"
        ]
        
        input_lower = user_input.lower()
        return any(keyword in input_lower for keyword in coding_keywords)

# Global instance
coding_prompt_manager = CodingAssistantPrompt()
