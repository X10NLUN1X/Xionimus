from .base_agent import BaseAgent, AgentCapability
from typing import Dict, Any
import anthropic
import os
import logging

class DataAgent(BaseAgent):
    """Agent specialized in data analysis and processing"""
    
    def __init__(self):
        super().__init__(
            name="Data Agent", 
            description="Data Analysis",
            capabilities=[
                AgentCapability.DATA_ANALYSIS,
                AgentCapability.STATISTICAL_ANALYSIS
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
        data_keywords = [
            "data", "analyze", "statistics", "chart", "graph", "visualization",
            "pandas", "dataframe", "csv", "excel", "dataset", "correlation",
            "trend", "pattern", "insight", "metrics", "dashboard"
        ]
        
        message_lower = message.lower()
        score = 0.0
        
        for keyword in data_keywords:
            if keyword in message_lower:
                if keyword in ["data", "analyze", "statistics", "pandas"]:
                    score += 0.3
                else:
                    score += 0.2
        
        # Boost score for explicit data requests
        if any(phrase in message_lower for phrase in ["analyze data", "data analysis", "create chart"]):
            score += 0.4
        
        return min(score, 1.0)
    
    async def execute_task(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute data analysis task"""
        try:
            client = await self._get_client()
            if not client:
                return {
                    "status": "error",
                    "error": "Anthropic API key not configured"
                }
            
            # Enhanced system message for data tasks
            system_message = """Du bist ein erfahrener Datenanalyst. Du hilfst bei:

- Datenanalyse mit Python und Pandas
- Statistische Auswertungen
- Datenvisualisierung
- Datenbereinigung und -verarbeitung
- Erkenntnisse und Trends identifizieren

Antworte auf Deutsch mit praktischem Code und klaren Erklärungen der Analyseergebnisse."""
            
            # Call Claude API with updated Opus 4.1 model
            response = await client.messages.create(
                model="claude-opus-4-1-20250805",
                max_tokens=4000,
                temperature=0.3,
                system=system_message,
                messages=[
                    {
                        "role": "user",
                        "content": message
                    }
                ]
            )
            
            content = response.content[0].text
            
            # Structure the response for data tasks
            result = {
                "status": "completed",
                "main_code": self._extract_code(content),
                "insights": self._extract_insights(content),
                "analysis_type": self._detect_analysis_type(message),
                "recommendations": self._extract_recommendations(content),
                "tokens_used": response.usage.input_tokens + response.usage.output_tokens if response.usage else None
            }
            
            return result
            
        except Exception as e:
            logging.error(f"Data agent error: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _extract_code(self, content: str) -> str:
        """Extract Python/data analysis code"""
        import re
        
        # Look for code blocks
        code_blocks = re.findall(r'```(?:python)?\n(.*?)\n```', content, re.DOTALL)
        
        if code_blocks:
            # Return the largest code block
            return max(code_blocks, key=len).strip()
        
        return ""
    
    def _extract_insights(self, content: str) -> list:
        """Extract key insights from the analysis"""
        import re
        
        insights = []
        
        # Look for insight indicators
        insight_patterns = [
            r'(?i)erkenn(?:tnis|ung).*?:\s*(.+)',
            r'(?i)wichtig.*?:\s*(.+)',
            r'(?i)fazit.*?:\s*(.+)',
            r'(?i)ergebnis.*?:\s*(.+)'
        ]
        
        for pattern in insight_patterns:
            matches = re.findall(pattern, content)
            insights.extend(matches)
        
        # Also look for bullet points that might be insights
        bullets = re.findall(r'[•\-\*]\s+(.+)', content)
        potential_insights = [b for b in bullets if any(keyword in b.lower() 
                              for keyword in ["zeigt", "deutet", "ergebnis", "trend"])]
        insights.extend(potential_insights)
        
        # Clean and limit insights
        clean_insights = [insight.strip() for insight in insights if insight.strip()]
        return clean_insights[:5]  # Limit to 5 key insights
    
    def _detect_analysis_type(self, message: str) -> str:
        """Detect the type of data analysis requested"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["correlation", "relationship"]):
            return "correlation"
        elif any(word in message_lower for word in ["trend", "time", "temporal"]):
            return "trend"
        elif any(word in message_lower for word in ["distribution", "frequency"]):
            return "distribution"
        elif any(word in message_lower for word in ["comparison", "compare"]):
            return "comparison"
        elif any(word in message_lower for word in ["visualization", "chart", "plot"]):
            return "visualization"
        else:
            return "general"
    
    def _extract_recommendations(self, content: str) -> list:
        """Extract recommendations from the analysis"""
        import re
        
        recommendations = []
        
        # Look for recommendation indicators
        rec_patterns = [
            r'(?i)empfehl(?:ung|e).*?:\s*(.+)',
            r'(?i)vorschlag.*?:\s*(.+)',
            r'(?i)nächste.*?schritte.*?:\s*(.+)'
        ]
        
        for pattern in rec_patterns:
            matches = re.findall(pattern, content)
            recommendations.extend(matches)
        
        # Look for numbered recommendations
        numbered = re.findall(r'\d+\.\s+(.+)', content)
        recommendations.extend(numbered)
        
        # Clean and limit recommendations
        clean_recs = [rec.strip() for rec in recommendations if rec.strip()]
        return clean_recs[:5]  # Limit to 5 recommendations