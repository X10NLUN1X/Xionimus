"""
Experimental AI Agent for advanced features:
- AI Code Review
- Predictive Coding  
- Auto-Refactoring
- Performance Profiling
- Smart Suggestions
"""

from .base_agent import BaseAgent, AgentCapability
from typing import Dict, Any, List, Optional
import anthropic
import ast
import re
import os
import logging
import json
import time
import traceback

class ExperimentalAgent(BaseAgent):
    """Agent for experimental AI features"""
    
    def __init__(self):
        super().__init__(
            name="Experimental Agent",
            description="AI Code Review, Predictive Coding, Auto-Refactoring, Performance Profiling, Smart Suggestions",
            capabilities=[
                AgentCapability.AI_CODE_REVIEW,
                AgentCapability.PREDICTIVE_CODING,
                AgentCapability.AUTO_REFACTORING,
                AgentCapability.PERFORMANCE_PROFILING,
                AgentCapability.SMART_SUGGESTIONS,
                AgentCapability.CODE_ANALYSIS,
                AgentCapability.CODE_GENERATION
            ]
        )
        self.client = None
        self.ai_model = "claude"
        
    async def _get_client(self):
        """Get or create Anthropic client"""
        if self.client is None:
            api_key = os.environ.get('ANTHROPIC_API_KEY')
            if api_key:
                self.client = anthropic.AsyncAnthropic(api_key=api_key)
        return self.client

    def can_handle_task(self, message: str, context: Dict[str, Any] = None) -> float:
        """Determine if this agent can handle the task"""
        experimental_keywords = [
            # AI Code Review keywords
            "code review", "review code", "analyse code", "code quality", "code analysis",
            "code inspection", "static analysis", "code audit", "review this code",
            
            # Predictive Coding keywords  
            "predict", "next step", "suggest next", "what next", "continue code",
            "complete code", "predictive", "auto complete", "suggest code",
            
            # Auto-Refactoring keywords
            "refactor", "optimize", "improve code", "clean code", "restructure",
            "auto refactor", "code optimization", "performance", "efficiency",
            
            # Performance Profiling keywords
            "profile", "performance", "benchmark", "timing", "speed analysis",
            "bottleneck", "optimization", "memory usage", "cpu usage",
            
            # Smart Suggestions keywords
            "suggest", "recommendation", "smart", "intelligent", "context aware",
            "best practices", "improve", "enhancement", "tip"
        ]
        
        message_lower = message.lower()
        score = 0.0
        
        # High priority experimental phrases
        high_priority_phrases = [
            "ai code review", "code review analysis", "predict next steps",
            "auto refactor", "refactor this code", "performance profile",
            "smart suggestions", "intelligent suggestions", "context suggestions"
        ]
        
        # Check for high priority phrases first  
        for phrase in high_priority_phrases:
            if phrase in message_lower:
                score += 0.8
                break
                
        # Add points for individual keywords
        for keyword in experimental_keywords:
            if keyword in message_lower:
                if keyword in ["review", "predict", "refactor", "profile", "suggest"]:
                    score += 0.4
                else:
                    score += 0.3
                    
        # Boost score if code context is provided
        if context and ("code" in str(context).lower() or "file" in str(context).lower()):
            score += 0.2
            
        return min(score, 1.0)

    async def execute_task(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute experimental AI task"""
        try:
            client = await self._get_client()
            if not client:
                return {
                    "status": "error",
                    "error": "Anthropic API key not configured"
                }
            
            # Detect which experimental feature is requested
            feature_type = self._detect_feature_type(message)
            
            if feature_type == "ai_code_review":
                return await self._ai_code_review(message, context, client)
            elif feature_type == "predictive_coding":
                return await self._predictive_coding(message, context, client)
            elif feature_type == "auto_refactoring":
                return await self._auto_refactoring(message, context, client)
            elif feature_type == "performance_profiling":
                return await self._performance_profiling(message, context, client)
            elif feature_type == "smart_suggestions":
                return await self._smart_suggestions(message, context, client)
            else:
                # Default to smart suggestions for general requests
                return await self._smart_suggestions(message, context, client)
                
        except Exception as e:
            logging.error(f"Experimental agent error: {e}")
            return {
                "status": "error",
                "error": str(e),
                "traceback": traceback.format_exc()
            }

    def _detect_feature_type(self, message: str) -> str:
        """Detect which experimental feature is being requested"""
        message_lower = message.lower()
        
        if any(keyword in message_lower for keyword in ["review", "analyse", "quality", "audit", "inspection"]):
            return "ai_code_review"
        elif any(keyword in message_lower for keyword in ["predict", "next", "continue", "complete", "suggest next"]):
            return "predictive_coding"  
        elif any(keyword in message_lower for keyword in ["refactor", "optimize", "restructure", "improve"]):
            return "auto_refactoring"
        elif any(keyword in message_lower for keyword in ["profile", "performance", "benchmark", "timing", "bottleneck"]):
            return "performance_profiling"
        elif any(keyword in message_lower for keyword in ["suggest", "recommendation", "smart", "tip", "best practice"]):
            return "smart_suggestions"
        else:
            return "smart_suggestions"  # Default

    async def _ai_code_review(self, message: str, context: Dict[str, Any], client) -> Dict[str, Any]:
        """🧪 AI Code Review - Vollautomatische Code-Qualitäts-Analyse"""
        
        system_message = """Du bist ein erfahrener Senior Software Engineer und Code Reviewer. 
        
Führe eine umfassende Code-Analyse durch und bewerte:

🔍 CODE QUALITÄT:
- Lesbarkeit und Klarheit
- Architektur und Design-Patterns
- Namenskonventionen
- Code-Struktur

🛡️ SICHERHEIT & BEST PRACTICES:
- Sicherheitslücken identifizieren
- Performance-Probleme
- Potentielle Bugs
- Best Practice Violations

📊 BEWERTUNG:
- Gesamtnote (1-10)
- Kritische Issues (High Priority)
- Verbesserungsvorschläge
- Code-Metriken

Antworte strukturiert auf Deutsch mit konkreten Verbesserungsvorschlägen."""

        # Extract code from message or context
        code_to_review = self._extract_code_from_input(message, context)
        
        if not code_to_review:
            return {
                "status": "error",
                "error": "Kein Code zum Review gefunden. Bitte Code bereitstellen."
            }
            
        review_prompt = f"""
VOLLSTÄNDIGE CODE-REVIEW ANALYSE:

{message}

CODE ZUM REVIEW:
```
{code_to_review}
```

Bitte führe eine umfassende Analyse durch und gib eine strukturierte Bewertung zurück.
"""

        try:
            response = await client.messages.create(
                model="claude-opus-4-1-20250805",
                max_tokens=4000,
                temperature=0.1,  # Low temperature for consistent reviews
                system=system_message,
                messages=[{
                    "role": "user",
                    "content": review_prompt
                }]
            )
            
            content = response.content[0].text
            
            # Parse and structure the review results
            review_results = self._parse_code_review_results(content)
            
            return {
                "status": "completed",
                "feature": "ai_code_review",
                "review_results": review_results,
                "full_review": content,
                "code_analyzed": len(code_to_review.split('\n')),
                "tokens_used": response.usage.input_tokens + response.usage.output_tokens if response.usage else None,
                "timestamp": time.time()
            }
            
        except Exception as e:
            return {
                "status": "error", 
                "error": f"Code Review Fehler: {str(e)}"
            }

    async def _predictive_coding(self, message: str, context: Dict[str, Any], client) -> Dict[str, Any]:
        """🎯 Predictive Coding - AI schlägt nächste Code-Schritte vor"""
        
        system_message = """Du bist ein intelligenter Coding Assistant mit predictive capabilities.

🎯 DEINE AUFGABE:
- Analysiere vorhandenen Code-Kontext
- Verstehe die Entwicklungsrichtung
- Schlage die logisch nächsten Schritte vor
- Berücksichtige Best Practices und Patterns

🧠 PREDICTIVE FEATURES:
- Funktionen die fehlen könnten
- Logische Code-Erweiterungen  
- Nötige Imports/Dependencies
- Test-Cases die geschrieben werden sollten
- Refactoring-Möglichkeiten

Antworte auf Deutsch mit konkreten, ausführbaren Vorschlägen."""

        current_code = self._extract_code_from_input(message, context)
        
        prediction_prompt = f"""
PREDICTIVE CODING ANALYSE:

{message}

AKTUELLER CODE-KONTEXT:
```
{current_code or 'Kein spezifischer Code-Kontext gefunden.'}
```

Analysiere den Kontext und schlage die nächsten logischen Entwicklungsschritte vor.
"""

        try:
            response = await client.messages.create(
                model="claude-opus-4-1-20250805", 
                max_tokens=3500,
                temperature=0.3,  # Some creativity for predictions
                system=system_message,
                messages=[{
                    "role": "user",
                    "content": prediction_prompt
                }]
            )
            
            content = response.content[0].text
            
            # Parse predictions into structured format
            predictions = self._parse_predictions(content)
            
            return {
                "status": "completed",
                "feature": "predictive_coding",
                "predictions": predictions,
                "full_analysis": content,
                "context_analyzed": bool(current_code),
                "tokens_used": response.usage.input_tokens + response.usage.output_tokens if response.usage else None,
                "timestamp": time.time()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Predictive Coding Fehler: {str(e)}"
            }

    async def _auto_refactoring(self, message: str, context: Dict[str, Any], client) -> Dict[str, Any]:
        """🔄 Auto-Refactoring - Intelligente Code-Optimierung"""
        
        system_message = """Du bist ein Experte für Code-Refactoring und Optimierung.

🔄 REFACTORING ZIELE:
- Code-Klarheit verbessern
- Performance optimieren
- Design Patterns anwenden
- DRY Principle befolgen
- SOLID Principles einhalten

⚡ OPTIMIERUNGEN:
- Komplexität reduzieren
- Redundanz eliminieren  
- Lesbarkeit erhöhen
- Wartbarkeit verbessern
- Security Fixes

Liefere sowohl den refactored Code als auch eine Erklärung der Verbesserungen auf Deutsch."""

        code_to_refactor = self._extract_code_from_input(message, context)
        
        if not code_to_refactor:
            return {
                "status": "error", 
                "error": "Kein Code zum Refactoring gefunden."
            }
            
        refactor_prompt = f"""
AUTO-REFACTORING ANALYSE:

{message}

CODE ZUM REFACTORING:
```
{code_to_refactor}
```

Führe eine intelligente Code-Optimierung durch und liefere:
1. Refactored Code
2. Liste der Verbesserungen
3. Performance-Implikationen
4. Erklärung der Änderungen
"""

        try:
            response = await client.messages.create(
                model="claude-opus-4-1-20250805",
                max_tokens=4000,
                temperature=0.2,  # Low temperature for consistent refactoring
                system=system_message,
                messages=[{
                    "role": "user", 
                    "content": refactor_prompt
                }]
            )
            
            content = response.content[0].text
            
            # Parse refactoring results
            refactoring_results = self._parse_refactoring_results(content)
            
            return {
                "status": "completed",
                "feature": "auto_refactoring", 
                "refactored_code": refactoring_results.get("refactored_code", ""),
                "improvements": refactoring_results.get("improvements", []),
                "performance_notes": refactoring_results.get("performance", ""),
                "full_analysis": content,
                "original_lines": len(code_to_refactor.split('\n')),
                "tokens_used": response.usage.input_tokens + response.usage.output_tokens if response.usage else None,
                "timestamp": time.time()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Auto-Refactoring Fehler: {str(e)}"
            }

    async def _performance_profiling(self, message: str, context: Dict[str, Any], client) -> Dict[str, Any]:
        """📈 Performance Profiling - Real-time Performance-Analyse"""
        
        system_message = """Du bist ein Performance-Experte für Software-Optimierung.

📈 PERFORMANCE ANALYSE:
- Time Complexity Analysis (Big O)
- Space Complexity Analysis  
- Bottleneck Identification
- Memory Usage Patterns
- CPU Usage Prediction

🔧 OPTIMIERUNGSVORSCHLÄGE:
- Algorithmus-Verbesserungen
- Caching-Strategien
- Database Query Optimization
- Memory Management
- Parallelisierung

Liefere detaillierte Performance-Metriken und konkrete Optimierungsvorschläge auf Deutsch."""

        code_to_profile = self._extract_code_from_input(message, context)
        
        profile_prompt = f"""
PERFORMANCE PROFILING ANALYSE:

{message}

CODE ZUR PERFORMANCE-ANALYSE:
```
{code_to_profile or 'Allgemeine Performance-Analyse ohne spezifischen Code.'}
```

Führe eine umfassende Performance-Analyse durch:
1. Time/Space Complexity
2. Potentielle Bottlenecks
3. Performance-Metriken
4. Optimierungsvorschläge
5. Benchmarking-Empfehlungen
"""

        try:
            response = await client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=3500,
                temperature=0.1,  # Very low for consistent analysis
                system=system_message,
                messages=[{
                    "role": "user",
                    "content": profile_prompt
                }]
            )
            
            content = response.content[0].text
            
            # Parse performance analysis
            performance_results = self._parse_performance_results(content)
            
            return {
                "status": "completed",
                "feature": "performance_profiling",
                "complexity_analysis": performance_results.get("complexity", {}),
                "bottlenecks": performance_results.get("bottlenecks", []),
                "optimizations": performance_results.get("optimizations", []),
                "benchmarking": performance_results.get("benchmarking", ""),
                "full_analysis": content,
                "has_code": bool(code_to_profile),
                "tokens_used": response.usage.input_tokens + response.usage.output_tokens if response.usage else None,
                "timestamp": time.time()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Performance Profiling Fehler: {str(e)}"
            }

    async def _smart_suggestions(self, message: str, context: Dict[str, Any], client) -> Dict[str, Any]:
        """🌟 Smart Suggestions - Kontext-bewusste Entwicklung"""
        
        system_message = """Du bist ein intelligenter Development Assistant mit kontextueller Awareness.

🌟 SMART SUGGESTIONS:
- Kontext-bewusste Empfehlungen
- Best Practice Guidelines  
- Tool/Library Empfehlungen
- Architecture Suggestions
- Development Workflow Tips

🎯 INTELLIGENTE FEATURES:
- Code-Pattern Recognition
- Framework-spezifische Tipps
- Security Recommendations
- Performance Hints
- Testing Strategies

Liefere personalisierte, kontext-bewusste Empfehlungen auf Deutsch."""

        # Analyze context for intelligent suggestions
        context_info = self._analyze_context(message, context)
        
        suggestions_prompt = f"""
SMART SUGGESTIONS ANALYSE:

ANFRAGE: {message}

KONTEXT-INFORMATION:
{json.dumps(context_info, indent=2, ensure_ascii=False)}

Erstelle intelligente, kontext-bewusste Entwicklungsvorschläge:
1. Sofortige Verbesserungen
2. Langfristige Optimierungen  
3. Tool/Framework Empfehlungen
4. Best Practice Guidelines
5. Nächste Schritte
"""

        try:
            response = await client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=3500,
                temperature=0.4,  # Moderate creativity for suggestions
                system=system_message,
                messages=[{
                    "role": "user",
                    "content": suggestions_prompt
                }]
            )
            
            content = response.content[0].text
            
            # Parse smart suggestions
            suggestions = self._parse_smart_suggestions(content)
            
            return {
                "status": "completed",
                "feature": "smart_suggestions",
                "immediate_suggestions": suggestions.get("immediate", []),
                "long_term_suggestions": suggestions.get("long_term", []),
                "tool_recommendations": suggestions.get("tools", []),
                "best_practices": suggestions.get("best_practices", []),
                "next_steps": suggestions.get("next_steps", []),
                "full_suggestions": content,
                "context_analyzed": context_info,
                "tokens_used": response.usage.input_tokens + response.usage.output_tokens if response.usage else None,
                "timestamp": time.time()
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Smart Suggestions Fehler: {str(e)}"
            }

    # Helper methods for parsing and analysis

    def _extract_code_from_input(self, message: str, context: Dict[str, Any]) -> str:
        """Extract code from message or context"""
        code = ""
        
        # Try to extract from message first
        code_blocks = re.findall(r'```[\w]*\n(.*?)\n```', message, re.DOTALL)
        if code_blocks:
            code = '\n'.join(code_blocks)
            
        # Try to get from context
        if not code and context:
            if 'code' in context:
                code = context['code']
            elif 'content' in context:
                code = context['content']
            elif 'file_content' in context:
                code = context['file_content']
                
        return code.strip()

    def _analyze_context(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze context for intelligent suggestions"""
        analysis = {
            "message_length": len(message),
            "has_code": bool(self._extract_code_from_input(message, context)),
            "context_keys": list(context.keys()) if context else [],
            "detected_languages": [],
            "detected_frameworks": [],
            "complexity_level": "medium"
        }
        
        # Detect programming languages
        languages = ["python", "javascript", "java", "react", "typescript", "html", "css"]
        for lang in languages:
            if lang in message.lower():
                analysis["detected_languages"].append(lang)
                
        # Detect frameworks/tools
        frameworks = ["react", "vue", "angular", "flask", "django", "fastapi", "express", "node"]
        for framework in frameworks:
            if framework in message.lower():
                analysis["detected_frameworks"].append(framework)
                
        return analysis

    def _parse_code_review_results(self, content: str) -> Dict[str, Any]:
        """Parse code review results into structured format"""
        results = {
            "overall_score": 7,  # Default
            "critical_issues": [],
            "improvements": [],
            "security_notes": [],
            "performance_notes": []
        }
        
        # Try to extract score
        score_match = re.search(r'(?:note|score|bewertung)[^\d]*(\d+)', content.lower())
        if score_match:
            results["overall_score"] = int(score_match.group(1))
            
        # Extract sections (simplified parsing)
        lines = content.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in ["kritisch", "critical", "problem"]):
                if line not in results["critical_issues"]:
                    results["critical_issues"].append(line)
            elif any(keyword in line.lower() for keyword in ["verbesser", "improve", "empfehlung"]):
                if line not in results["improvements"]:
                    results["improvements"].append(line)
                    
        return results

    def _parse_predictions(self, content: str) -> Dict[str, Any]:
        """Parse predictive coding results"""
        predictions = {
            "next_functions": [],
            "missing_imports": [],
            "suggested_tests": [],
            "code_extensions": []
        }
        
        # Simple parsing - could be enhanced
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('def ') or 'function' in line.lower():
                predictions["next_functions"].append(line)
            elif line.startswith('import ') or line.startswith('from '):
                predictions["missing_imports"].append(line)
            elif 'test' in line.lower():
                predictions["suggested_tests"].append(line)
                
        return predictions

    def _parse_refactoring_results(self, content: str) -> Dict[str, Any]:
        """Parse refactoring results"""
        results = {
            "refactored_code": "",
            "improvements": [],
            "performance": ""
        }
        
        # Extract refactored code
        code_blocks = re.findall(r'```[\w]*\n(.*?)\n```', content, re.DOTALL)
        if code_blocks:
            results["refactored_code"] = code_blocks[0]
            
        # Extract improvements (simplified)
        lines = content.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in ["verbesser", "improve", "optimier"]):
                results["improvements"].append(line.strip())
                
        return results

    def _parse_performance_results(self, content: str) -> Dict[str, Any]:
        """Parse performance profiling results"""
        results = {
            "complexity": {"time": "O(?)", "space": "O(?)"},
            "bottlenecks": [],
            "optimizations": [],
            "benchmarking": ""
        }
        
        # Extract complexity info
        if "O(" in content:
            complexity_matches = re.findall(r'O\([^)]+\)', content)
            if complexity_matches:
                results["complexity"]["time"] = complexity_matches[0]
                
        # Extract bottlenecks and optimizations (simplified)
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if any(keyword in line.lower() for keyword in ["bottleneck", "engpass", "langsam"]):
                results["bottlenecks"].append(line)
            elif any(keyword in line.lower() for keyword in ["optimier", "verbesser", "schneller"]):
                results["optimizations"].append(line)
                
        return results

    def _parse_smart_suggestions(self, content: str) -> Dict[str, Any]:
        """Parse smart suggestions"""
        suggestions = {
            "immediate": [],
            "long_term": [],
            "tools": [],
            "best_practices": [],
            "next_steps": []
        }
        
        # Simple categorization based on keywords
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if any(keyword in line.lower() for keyword in ["sofort", "immediate", "jetzt"]):
                suggestions["immediate"].append(line)
            elif any(keyword in line.lower() for keyword in ["langfrist", "long-term", "zukunft"]):
                suggestions["long_term"].append(line)
            elif any(keyword in line.lower() for keyword in ["tool", "framework", "library"]):
                suggestions["tools"].append(line)
            elif any(keyword in line.lower() for keyword in ["best practice", "empfehlung", "regel"]):
                suggestions["best_practices"].append(line)
            elif any(keyword in line.lower() for keyword in ["nächst", "next", "schritt"]):
                suggestions["next_steps"].append(line)
            else:
                # Default to immediate suggestions
                suggestions["immediate"].append(line)
                
        return suggestions