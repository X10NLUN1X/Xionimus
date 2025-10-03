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
   - **WICHTIG: Wenn Research durchgeführt wurde (erkennbar an "✅ Recherche abgeschlossen!"), 
     MUSST du diese Informationen explizit verwenden für:**
     * Aktuelle Best Practices und Patterns aus 2025
     * Framework-Auswahl und Versionen
     * Security-Implementierungen
     * Performance-Optimierungen
     * Aktuelle Trends und Standards

6. BIETE GITHUB-PUSH AN
   "Möchten Sie den Code zu GitHub pushen?"

WICHTIGE REGELN:
- NUR Coding-Themen (keine allgemeinen Fragen)
- Immer vollständige Implementierungen
- Moderne Best Practices (2025)
- Security & Performance beachten
- Deutsche Kommentare im Code
- Englische Variablennamen
- **Research-Ergebnisse im Conversation-History STRIKT befolgen**

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
   🔴 Large (10-15 minutes) - In-depth analysis with current trends
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
    
    def should_offer_research(self, messages: List[Dict[str, str]]) -> bool:
        """
        Check if we should offer research options to the user
        Returns True if:
        - Latest message is a COMPLETE/DETAILED coding request
        - No research choice has been made yet
        - Not already in middle of coding process
        
        WICHTIG: User sollte erst Details nennen, bevor Research angeboten wird
        - "Ich möchte ein Programm entwickeln" → zu vage, kein Research
        - "Ich möchte eine React Todo-App mit TypeScript erstellen" → detailliert, Research anbieten
        """
        if not messages or len(messages) < 1:
            return False
        
        # Get last user message
        last_user_msg = None
        for msg in reversed(messages):
            if msg.get("role") == "user":
                last_user_msg = msg.get("content", "")
                break
        
        if not last_user_msg:
            return False
        
        # Check if it's a coding request
        if not self.is_coding_related(last_user_msg):
            return False
        
        # Check if user already made a research choice
        if self.detect_research_choice(last_user_msg):
            return False
        
        # NEW: Check if the request is DETAILED enough
        # Vage Anfragen (zu kurz oder zu generisch) sollten KEINEN Research-Dialog triggern
        if not self._is_detailed_project_description(last_user_msg):
            return False
        
        # Check if conversation already has assistant responses (already coding)
        has_assistant_response = any(msg.get("role") == "assistant" for msg in messages)
        
        # Offer research only on first coding request (no assistant responses yet)
        return not has_assistant_response
    
    def _is_detailed_project_description(self, user_input: str) -> bool:
        """
        Check if user input contains enough detail about their project
        
        VAGE (kein Research):
        - "ich möchte ein programm entwickeln"
        - "ich will eine app bauen"
        - "erstelle eine website"
        
        DETAILLIERT (Research anbieten):
        - "ich möchte eine react todo-app mit typescript erstellen"
        - "baue mir eine fastapi backend mit mongodb"
        - "erstelle eine e-commerce website mit payment integration"
        """
        input_lower = user_input.lower()
        
        # Zu kurz = nicht detailliert genug
        if len(user_input.strip()) < 30:
            return False
        
        # Zähle spezifische Details (Technologien, Features, etc.)
        detail_indicators = [
            # Technologien/Frameworks
            "react", "vue", "angular", "next", "nuxt", "svelte",
            "python", "javascript", "typescript", "java", "c#", "go", "rust",
            "django", "flask", "fastapi", "express", "spring", "laravel",
            "mongodb", "postgresql", "mysql", "redis", "sqlite",
            "docker", "kubernetes", "aws", "azure", "gcp",
            # Feature-Beschreibungen
            "mit", "und", "authentifizierung", "login", "database", "api",
            "payment", "chat", "dashboard", "admin", "crud", "rest",
            "graphql", "websocket", "real-time", "notification",
            # Konkrete Projekt-Typen
            "todo", "blog", "shop", "e-commerce", "cms", "crm",
            "social", "messaging", "calendar", "booking", "forum"
        ]
        
        detail_count = sum(1 for indicator in detail_indicators if indicator in input_lower)
        
        # Mindestens 2 Details = detailliert genug
        return detail_count >= 2
    
    def generate_research_question(self, language: str = "de") -> Dict[str, Any]:
        """
        Generate the research options question with clickable buttons
        """
        if language == "de":
            return {
                "message": "🔍 **Recherche-Optionen**\n\nMöchten Sie eine aktuelle Recherche zu Ihrer Anfrage durchführen?",
                "options": [
                    {
                        "id": "klein",
                        "title": "🟢 Klein",
                        "description": "5-10 Sek - Schnelle Übersicht, grundlegende Best Practices",
                        "action": "research_small",
                        "duration": "5-10 Sek",
                        "icon": "🟢"
                    },
                    {
                        "id": "mittel",
                        "title": "🟡 Mittel",
                        "description": "15-30 Sek - Standard-Recherche mit Details und Beispielen",
                        "action": "research_medium",
                        "duration": "15-30 Sek",
                        "icon": "🟡"
                    },
                    {
                        "id": "gross",
                        "title": "🔴 Groß",
                        "description": "10-15 Min - Tiefgehende Analyse mit aktuellen Trends",
                        "action": "research_large",
                        "duration": "10-15 Min",
                        "icon": "🔴"
                    },
                    {
                        "id": "keine",
                        "title": "❌ Keine Recherche",
                        "description": "Direkt mit Coding beginnen",
                        "action": "research_none",
                        "duration": "0 Sek",
                        "icon": "❌"
                    }
                ]
            }
        else:
            return {
                "message": "🔍 **Research Options**\n\nWould you like to conduct current research on your request?",
                "options": [
                    {
                        "id": "small",
                        "title": "🟢 Small",
                        "description": "5-10 sec - Quick overview, basic best practices",
                        "action": "research_small",
                        "duration": "5-10 sec",
                        "icon": "🟢"
                    },
                    {
                        "id": "medium",
                        "title": "🟡 Medium",
                        "description": "15-30 sec - Standard research with details and examples",
                        "action": "research_medium",
                        "duration": "15-30 sec",
                        "icon": "🟡"
                    },
                    {
                        "id": "large",
                        "title": "🔴 Large",
                        "description": "10-15 min - In-depth analysis with current trends",
                        "action": "research_large",
                        "duration": "10-15 min",
                        "icon": "🔴"
                    },
                    {
                        "id": "none",
                        "title": "❌ No Research",
                        "description": "Start coding directly",
                        "action": "research_none",
                        "duration": "0 sec",
                        "icon": "❌"
                    }
                ]
            }
    
    def generate_post_code_options(self, language: str = "de") -> Dict[str, Any]:
        """
        Generate post-code options after code generation is complete
        Returns structured data with clickable options
        """
        if language == "de":
            return {
                "message": "✅ **Code-Generierung abgeschlossen!**\n\nWie möchten Sie fortfahren?",
                "options": [
                    {
                        "id": "debugging",
                        "title": "🐛 Debugging",
                        "description": "Detaillierte Code-Analyse durch Claude Opus 4.1",
                        "action": "debug_code",
                        "provider": "anthropic",
                        "model": "claude-opus-4-20250514",
                        "icon": "🐛"
                    },
                    {
                        "id": "improvements",
                        "title": "⚡ Verbesserungsvorschläge",
                        "description": "Optimierungen für Performance, Security und Best Practices",
                        "action": "suggest_improvements",
                        "provider": "anthropic",
                        "model": "claude-sonnet-4-5-20250929",
                        "icon": "⚡"
                    },
                    {
                        "id": "other",
                        "title": "💡 Weitere Schritte",
                        "description": "Testing, Dokumentation oder Deployment-Optionen",
                        "action": "suggest_next_steps",
                        "provider": "anthropic",
                        "model": "claude-sonnet-4-5-20250929",
                        "icon": "💡"
                    }
                ]
            }
        else:
            return {
                "message": "✅ **Code Generation Complete!**\n\nHow would you like to proceed?",
                "options": [
                    {
                        "id": "debugging",
                        "title": "🐛 Debugging",
                        "description": "Detailed code analysis by Claude Opus 4.1",
                        "action": "debug_code",
                        "provider": "anthropic",
                        "model": "claude-opus-4-20250514",
                        "icon": "🐛"
                    },
                    {
                        "id": "improvements",
                        "title": "⚡ Improvement Suggestions",
                        "description": "Optimizations for performance, security and best practices",
                        "action": "suggest_improvements",
                        "provider": "anthropic",
                        "model": "claude-sonnet-4-5-20250929",
                        "icon": "⚡"
                    },
                    {
                        "id": "other",
                        "title": "💡 Next Steps",
                        "description": "Testing, documentation or deployment options",
                        "action": "suggest_next_steps",
                        "provider": "anthropic",
                        "model": "claude-sonnet-4-5-20250929",
                        "icon": "💡"
                    }
                ]
            }
    
    def detect_post_code_choice(self, user_input: str) -> Optional[str]:
        """
        Detect which post-code option the user selected
        Returns: 'debugging', 'improvements', 'other', or None
        """
        input_lower = user_input.lower().strip()
        
        # Debugging keywords
        debugging_keywords = [
            "debugging", "debug", "fehler", "error", "bug", "🐛",
            "1", "option 1", "erste", "first"
        ]
        if any(kw in input_lower for kw in debugging_keywords):
            return "debugging"
        
        # Improvements keywords
        improvement_keywords = [
            "verbesserung", "improvement", "optimierung", "optimization",
            "verbessern", "improve", "optimize", "⚡", "performance",
            "2", "option 2", "zweite", "second"
        ]
        if any(kw in input_lower for kw in improvement_keywords):
            return "improvements"
        
        # Other/Next steps keywords
        other_keywords = [
            "weitere", "next", "nächste", "sonstige", "other", "steps",
            "test", "documentation", "deployment", "💡",
            "3", "option 3", "dritte", "third"
        ]
        if any(kw in input_lower for kw in other_keywords):
            return "other"
        
        return None
    
    def should_offer_post_code_options(self, messages: List[Dict[str, str]]) -> bool:
        """
        Check if we should offer post-code options
        Returns True ONLY if:
        1. Last assistant message contains substantial code blocks
        2. This is NOT the first response to a simple prompt
        3. Conversation has progressed beyond initial request
        """
        if not messages or len(messages) < 3:  # Minimum: user prompt, assistant response, user follow-up
            return False
        
        # Get last assistant message
        last_assistant_msg = None
        for msg in reversed(messages):
            if msg.get("role") == "assistant":
                last_assistant_msg = msg.get("content", "")
                break
        
        if not last_assistant_msg:
            return False
        
        # Check if message contains code blocks (``` markers)
        has_code = "```" in last_assistant_msg
        
        # Check if message is substantial (longer than 1000 chars for code)
        is_substantial = len(last_assistant_msg) > 1000
        
        # Count how many assistant messages we have (should have at least 2)
        assistant_count = sum(1 for msg in messages if msg.get("role") == "assistant")
        
        # Don't offer post-code options on first response
        # This prevents showing debugging options immediately after a simple prompt
        is_not_first_response = assistant_count > 1
        
        # Check if last user message was a post-code choice
        # If yes, don't offer options again (avoid loop)
        last_user_msg = None
        for msg in reversed(messages):
            if msg.get("role") == "user":
                last_user_msg = msg.get("content", "").lower()
                break
        
        if last_user_msg:
            post_code_keywords = ["debugging", "verbesserung", "improvement", "weitere schritte", "next steps"]
            is_post_code_choice = any(kw in last_user_msg for kw in post_code_keywords)
            if is_post_code_choice:
                return False  # Don't offer options after user already chose one
        
        return has_code and is_substantial and is_not_first_response

# Global instance
coding_prompt_manager = CodingAssistantPrompt()
