import re
from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentTask, AgentStatus, AgentCapability
import os
from openai import AsyncOpenAI
import sys
import os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from stanton_stations import stanton_system

class ResearchAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Research Agent",
            description="Specialized in DEEP web research, information gathering, and fact-checking using Perplexity AI DEEP RESEARCH ONLY",
            capabilities=[
                AgentCapability.WEB_RESEARCH
            ]
        )
        # CRITICAL: ONLY Deep Research Model allowed - NO standard or simple models
        self.ai_model = "perplexity"
        self.REQUIRED_MODEL = "sonar-deep-research"  # MANDATORY - Never change this
        self.FORBIDDEN_MODELS = [
            "sonar", "sonar-pro", "sonar-medium", "sonar-small", 
            "llama", "codellama", "mixtral", "pplx", "gpt", "claude"
        ]
        
    def can_handle_task(self, task_description: str, context: Dict[str, Any]) -> float:
        """Evaluate if this agent can handle the task"""
        research_keywords = [
            'research', 'find', 'search', 'information', 'data', 'facts', 'analyze',
            'investigate', 'study', 'explore', 'gather', 'collect', 'compare',
            'market research', 'competitive analysis', 'trends', 'statistics',
            'what is', 'how to', 'explain', 'summarize', 'overview', 'latest',
            'current', 'news', 'developments', 'industry', 'market', 'report',
            'station', 'distance', 'stanton', 'distanz', 'station'
        ]
        
        # Simple greeting/smalltalk keywords - reduce confidence for these
        smalltalk_keywords = [
            'hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening',
            'how are you', 'what\'s up', 'how\'s it going', 'nice to meet you',
            'thank you', 'thanks', 'please', 'sorry', 'excuse me', 'goodbye', 'bye',
            'see you', 'have a nice day', 'take care', 'hallo', 'danke', 'bitte',
            'tschüss', 'auf wiedersehen', 'wie geht es', 'guten tag', 'guten morgen'
        ]
        
        # Very simple questions that don't need research
        simple_question_patterns = [
            'wie heißt du', 'what is your name', 'who are you', 'wer bist du',
            'kannst du', 'can you', 'what can you do', 'was kannst du',
            'help', 'hilfe', 'test', 'testing', '1+1', 'simple math'
        ]
        
        description_lower = task_description.lower()
        
        # Check for smalltalk/greetings - significantly reduce confidence
        if any(keyword in description_lower for keyword in smalltalk_keywords):
            return 0.1  # Very low confidence for smalltalk
            
        # Check for simple questions - reduce confidence
        if any(pattern in description_lower for pattern in simple_question_patterns):
            return 0.2  # Low confidence for simple questions
            
        # Check for very short queries (likely not research-worthy)
        if len(task_description.strip()) < 10:
            return 0.15  # Low confidence for very short queries
        
        matches = sum(1 for keyword in research_keywords if keyword in description_lower)
        confidence = min(matches / 3, 1.0)
        
        # Boost confidence for Stanton station queries
        if 'stanton' in description_lower and any(word in description_lower for word in ['station', 'distanz', 'distance', 'entfernung']):
            confidence = max(confidence, 0.9)
        
        # Boost confidence for question-like queries, but only if they're substantial
        if len(task_description.strip()) >= 15:  # Only boost for substantial questions
            if any(description_lower.startswith(q) for q in ['what', 'how', 'why', 'when', 'where', 'who']):
                confidence += 0.3
            if '?' in task_description:
                confidence += 0.2
                
        # Boost for research-specific terms
        if any(term in description_lower for term in ['latest', 'current', 'trends', 'market', 'industry']):
            confidence += 0.3
            
        return min(confidence, 1.0)
    
    async def execute_task(self, task: AgentTask) -> AgentTask:
        """Execute research tasks using Perplexity AI"""
        try:
            task.status = AgentStatus.THINKING
            await self.update_progress(task, 0.1, "Initializing research")
            
            # Check if this is a Stanton station query
            if self._is_stanton_station_query(task.description):
                return await self._handle_stanton_station_query(task)
            
            await self.update_progress(task, 0.2, "Initializing Perplexity research")
            
            # Get Perplexity client
            api_key = os.environ.get('PERPLEXITY_API_KEY')
            if not api_key:
                raise Exception("Perplexity API key not configured")
            
            client = AsyncOpenAI(
                api_key=api_key,
                base_url="https://api.perplexity.ai"
            )
            
            await self.update_progress(task, 0.3, "Analyzing research requirements")
            
            # Determine research type and create enhanced prompt
            task_type = self._identify_research_type(task.description)
            enhanced_prompt = self._create_research_prompt(task.description, task_type, task.input_data.get('language', 'english'))
            
            await self.update_progress(task, 0.5, "Conducting research with Perplexity")
            
            # Make API call to Perplexity with Deep Research capabilities
            response = await client.chat.completions.create(
                model="sonar-deep-research",
                messages=[
                    {"role": "system", "content": "You are a professional research assistant. Provide comprehensive, accurate, and well-sourced information with expert-level analysis."},
                    {"role": "user", "content": enhanced_prompt}
                ],
                max_tokens=4000,
                temperature=0.3,  # Lower temperature for more factual responses
                reasoning_effort="medium",  # Balance between depth and speed
                stream=False
            )
            
            await self.update_progress(task, 0.8, "Processing research results")
            
            content = response.choices[0].message.content
            sources = getattr(response, 'search_results', [])
            
            # Structure the research result
            task.result = {
                "type": task_type,
                "research_content": content,
                "sources": sources,
                "summary": self._extract_summary(content),
                "key_points": self._extract_key_points(content),
                "confidence": 0.9,
                "ai_model_used": "perplexity",
                "tokens_used": response.usage.total_tokens if hasattr(response, 'usage') else None
            }
            
            task.status = AgentStatus.COMPLETED
            await self.update_progress(task, 1.0, "Research completed successfully")
            
        except Exception as e:
            task.status = AgentStatus.ERROR
            task.error_message = f"Research failed: {str(e)}"
            self.logger.error(f"Research agent error: {e}")
            
        return task
    
    def _identify_research_type(self, description: str) -> str:
        """Identify the type of research task"""
        description_lower = description.lower()
        
        if any(word in description_lower for word in ['compare', 'versus', 'vs', 'difference']):
            return "comparative_research"
        elif any(word in description_lower for word in ['trend', 'trending', 'popular', 'growth', 'latest']):
            return "trend_analysis"
        elif any(word in description_lower for word in ['market', 'competitor', 'industry', 'business']):
            return "market_research"
        elif any(word in description_lower for word in ['what is', 'define', 'explain', 'meaning']):
            return "factual_research"
        elif any(word in description_lower for word in ['news', 'current', 'recent', 'today']):
            return "news_research"
        else:
            return "general_research"
    
    def _create_research_prompt(self, description: str, research_type: str, language: str) -> str:
        """Create an enhanced prompt for better research results"""
        language_instructions = {
            'german': "Bitte antworte auf Deutsch und verwende deutsche Quellen wo möglich.",
            'english': "Please respond in English and prioritize English sources.",
            'spanish': "Por favor responde en español y usa fuentes en español cuando sea posible.",
            'french': "Veuillez répondre en français et utiliser des sources françaises si possible.",
            'italian': "Si prega di rispondere in italiano e utilizzare fonti italiane quando possibile."
        }
        
        lang_instruction = language_instructions.get(language, language_instructions['english'])
        
        base_prompt = f"{description}\n\n{lang_instruction}\n\n"
        
        if research_type == "comparative_research":
            base_prompt += "Please provide a detailed comparison with pros and cons, and include recent data and sources."
        elif research_type == "trend_analysis":
            base_prompt += "Focus on current trends, recent developments, and future predictions with supporting data."
        elif research_type == "market_research":
            base_prompt += "Include market size, key players, growth trends, and competitive landscape analysis."
        elif research_type == "factual_research":
            base_prompt += "Provide accurate, well-sourced factual information with multiple authoritative sources."
        elif research_type == "news_research":
            base_prompt += "Focus on the most recent news and developments, including dates and sources."
        else:
            base_prompt += "Provide comprehensive information with multiple authoritative sources and current data."
        
        return base_prompt
    
    def _extract_summary(self, content: str) -> str:
        """Extract a brief summary from the research content"""
        lines = content.split('\n')
        summary_lines = []
        
        for line in lines[:5]:  # Take first 5 lines as summary
            if line.strip() and not line.startswith('#'):
                summary_lines.append(line.strip())
        
        return ' '.join(summary_lines)[:300] + "..." if len(' '.join(summary_lines)) > 300 else ' '.join(summary_lines)
    
    def _extract_key_points(self, content: str) -> List[str]:
        """Extract key points from the research content"""
        key_points = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('•') or line.startswith('-') or line.startswith('*'):
                key_points.append(line[1:].strip())
            elif line.startswith(('1.', '2.', '3.', '4.', '5.')):
                key_points.append(line[2:].strip())
        
        return key_points[:10]  # Return max 10 key points
    
    def _is_stanton_station_query(self, description: str) -> bool:
        """Check if the query is about Stanton stations"""
        description_lower = description.lower()
        stanton_keywords = ['stanton', 'station']
        distance_keywords = ['distance', 'distanz', 'entfernung', 'abstand', 'kilometer', 'km']
        
        has_stanton = any(keyword in description_lower for keyword in stanton_keywords)
        has_distance = any(keyword in description_lower for keyword in distance_keywords)
        
        return has_stanton and (has_distance or 'station' in description_lower)
    
    async def _handle_stanton_station_query(self, task: AgentTask) -> AgentTask:
        """Handle Stanton station distance queries using local data"""
        try:
            await self.update_progress(task, 0.3, "Analyzing Stanton station query")
            
            description_lower = task.description.lower()
            
            # Determine what type of station query this is
            if any(word in description_lower for word in ['alle', 'all', 'list', 'overview']):
                content = self._generate_all_stations_overview()
            elif any(word in description_lower for word in ['distance', 'distanz', 'entfernung']):
                content = self._generate_distance_analysis()
            elif any(word in description_lower for word in ['nearest', 'nächste', 'close']):
                content = self._generate_nearest_stations_analysis()
            else:
                content = self._generate_general_stanton_info()
            
            await self.update_progress(task, 0.8, "Formatting Stanton station results")
            
            task.result = {
                "type": "stanton_station_research",
                "research_content": content,
                "sources": ["Local Stanton Station Database", "Integrated Station System"],
                "summary": self._extract_summary(content),
                "key_points": self._extract_key_points(content),
                "confidence": 1.0,  # High confidence for local data
                "ai_model_used": "local_data",
                "tokens_used": None
            }
            
            task.status = AgentStatus.COMPLETED
            await self.update_progress(task, 1.0, "Stanton station research completed")
            
        except Exception as e:
            task.status = AgentStatus.ERROR
            task.error_message = f"Stanton station research failed: {str(e)}"
            self.logger.error(f"Stanton station research error: {e}")
        
        return task
    
    def _generate_all_stations_overview(self) -> str:
        """Generate overview of all Stanton stations"""
        content = "# Stanton Station Network Overview\n\n"
        
        # Group stations by type
        station_types = {}
        for name, station in stanton_system.get_all_stations().items():
            if station.station_type not in station_types:
                station_types[station.station_type] = []
            station_types[station.station_type].append(station)
        
        for station_type, stations in station_types.items():
            content += f"## {station_type.title()} Stations\n\n"
            for station in stations:
                content += f"- **{station.name}**: {station.description or 'Station'}\n"
                content += f"  - Coordinates: {station.coordinates}\n"
            content += "\n"
        
        content += f"**Total Stations**: {len(stanton_system.get_all_stations())}\n"
        content += f"**Station Types**: {', '.join(station_types.keys())}\n"
        
        return content
    
    def _generate_distance_analysis(self) -> str:
        """Generate distance analysis between stations"""
        content = "# Stanton Station Distance Analysis\n\n"
        
        # Show some example distances for each station type
        station_types = ['space', 'subway', 'rail']
        
        for station_type in station_types:
            stations = stanton_system.get_stations_by_type(station_type)
            if len(stations) < 2:
                continue
                
            content += f"## {station_type.title()} Station Distances\n\n"
            
            station_names = list(stations.keys())
            for i, station1 in enumerate(station_names[:3]):  # Show first 3 stations
                for station2 in station_names[i+1:i+3]:  # Show 2 distances per station
                    distance_obj = stanton_system.get_distance(station1, station2)
                    if distance_obj:
                        content += f"- **{station1}** to **{station2}**: {distance_obj.distance:.2f} {distance_obj.unit}\n"
            content += "\n"
        
        return content
    
    def _generate_nearest_stations_analysis(self) -> str:
        """Generate analysis of nearest stations"""
        content = "# Nearest Stations Analysis\n\n"
        
        # Show nearest stations for a few key stations
        key_stations = ["Port Olisar", "Stanton Central", "Stanton Street"]
        
        for station_name in key_stations:
            if station_name in stanton_system.get_all_stations():
                nearest = stanton_system.find_nearest_stations(station_name, 3)
                content += f"## Nearest stations to {station_name}\n\n"
                for name, distance in nearest:
                    station = stanton_system.get_all_stations()[name]
                    unit = stanton_system._get_unit_for_type(station.station_type)
                    content += f"- **{name}**: {distance:.2f} {unit}\n"
                content += "\n"
        
        return content
    
    def _generate_general_stanton_info(self) -> str:
        """Generate general information about Stanton stations"""
        content = "# Stanton Station System Information\n\n"
        
        all_stations = stanton_system.get_all_stations()
        content += f"Das Stanton-Stationssystem umfasst {len(all_stations)} Stationen verschiedener Typen.\n\n"
        
        # Count by type
        type_counts = {}
        for station in all_stations.values():
            type_counts[station.station_type] = type_counts.get(station.station_type, 0) + 1
        
        content += "## Stationstypen:\n\n"
        for station_type, count in type_counts.items():
            content += f"- **{station_type.title()}**: {count} Stationen\n"
        
        content += "\n## Verfügbare Funktionen:\n\n"
        content += "- Distanzberechnung zwischen beliebigen Stationen\n"
        content += "- Suche nach nächstgelegenen Stationen\n"
        content += "- Routenplanung durch mehrere Stationen\n"
        content += "- Stationssuche nach Name oder Beschreibung\n"
        
        return content