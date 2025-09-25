"""
XIONIMUS AI - Multi-Agent Orchestrator with Adaptive Intelligence
Advanced orchestration system that enables cross-agent collaboration,
dynamic sub-agent creation, and collective intelligence patterns.
"""

import asyncio
import logging
import uuid
import time
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone
from dataclasses import dataclass, field
from enum import Enum
import json

from agents.agent_manager import AgentManager
from agents.base_agent import BaseAgent, AgentTask, AgentStatus
from agents.context_analyzer import EnhancedContextAnalyzer, TaskDomain

class ComplexityLevel(Enum):
    SIMPLE = "simple"      # Single agent, direct task
    MODERATE = "moderate"  # Multiple agents, sequential
    COMPLEX = "complex"    # Agent swarm, parallel processing
    XIONIMUS_AI = "xionimus_ai"  # Dynamic sub-agents, collective intelligence

@dataclass
class XionimusPattern:
    """Represents an adaptive pattern discovered through agent interactions"""
    pattern_id: str
    pattern_type: str
    success_rate: float
    agent_combinations: List[str]
    task_characteristics: Dict[str, Any]
    performance_metrics: Dict[str, float]
    discovered_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    usage_count: int = 0

@dataclass
class AgentSwarmTask:
    """Enhanced task for coordinated agent swarm execution"""
    task_id: str
    primary_task: str
    complexity_score: float
    assigned_agents: List[str]
    sub_agents: List[str] = field(default_factory=list)
    collaboration_type: str = "parallel"
    progress_steps: List[Dict[str, Any]] = field(default_factory=list)
    xionimus_ai_patterns: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

class XionimusAIOrchestrator:
    """
    XIONIMUS AI Multi-Agent Orchestrator
    
    Implements adaptive AI capabilities including:
    - Adaptive agent creation and specialization
    - Cross-agent learning and pattern recognition
    - Self-organizing workflows
    - Collective intelligence coordination
    """
    
    def __init__(self, agent_manager: AgentManager):
        self.agent_manager = agent_manager
        self.context_analyzer = EnhancedContextAnalyzer()
        self.logger = logging.getLogger("xionimus_orchestrator")
        
        # Adaptive AI components
        self.discovered_patterns: Dict[str, XionimusPattern] = {}
        self.active_swarms: Dict[str, AgentSwarmTask] = {}
        self.performance_history: List[Dict[str, Any]] = []
        self.sub_agents: Dict[str, BaseAgent] = {}
        
        # Learning and adaptation
        self.collaboration_success_rates: Dict[str, float] = {}
        self.agent_specialization_scores: Dict[str, Dict[str, float]] = {}
        
        self.logger.info("🤖 XIONIMUS AI Multi-Agent Orchestrator initialized")
    
    async def analyze_request_complexity(self, request: str, context: Dict[str, Any] = None) -> Tuple[ComplexityLevel, float]:
        """
        Analyze request complexity using adaptive AI patterns
        Returns complexity level and confidence score
        """
        try:
            # Basic complexity indicators
            complexity_indicators = {
                'length': len(request.split()) / 100,  # Normalized word count
                'keywords': self._count_complexity_keywords(request),
                'technical_depth': self._analyze_technical_depth(request),
                'multi_domain': self._detect_multi_domain_requirements(request),
                'context_dependency': self._analyze_context_dependency(request, context)
            }
            
            # Calculate base complexity score
            base_score = sum(complexity_indicators.values()) / len(complexity_indicators)
            
            # Apply adaptive pattern matching
            pattern_boost = self._apply_pattern_matching(request, complexity_indicators)
            
            final_score = min(10.0, base_score * 10 + pattern_boost)
            
            # Determine complexity level
            if final_score >= 8.0:
                level = ComplexityLevel.XIONIMUS_AI
            elif final_score >= 6.0:
                level = ComplexityLevel.COMPLEX
            elif final_score >= 4.0:
                level = ComplexityLevel.MODERATE
            else:
                level = ComplexityLevel.SIMPLE
            
            self.logger.info(f"📊 Request complexity: {level.value} (score: {final_score:.2f})")
            return level, final_score
            
        except Exception as e:
            self.logger.error(f"Error analyzing complexity: {e}")
            return ComplexityLevel.MODERATE, 5.0
    
    async def assemble_agent_swarm(self, request: str, complexity: ComplexityLevel, 
                                  complexity_score: float, context: Dict[str, Any] = None) -> AgentSwarmTask:
        """
        Assemble optimal agent swarm based on complexity and adaptive patterns
        """
        task_id = str(uuid.uuid4())
        
        # Select primary agents based on request analysis
        primary_agents = await self._select_primary_agents(request, context)
        
        # Determine collaboration type
        collaboration_type = self._determine_collaboration_type(complexity, primary_agents)
        
        # Create specialized sub-agents if needed
        sub_agents = []
        if complexity in [ComplexityLevel.COMPLEX, ComplexityLevel.XIONIMUS_AI]:
            sub_agents = await self._create_specialized_sub_agents(request, primary_agents)
        
        # Create swarm task
        swarm_task = AgentSwarmTask(
            task_id=task_id,
            primary_task=request,
            complexity_score=complexity_score,
            assigned_agents=primary_agents,
            sub_agents=sub_agents,
            collaboration_type=collaboration_type
        )
        
        self.active_swarms[task_id] = swarm_task
        
        self.logger.info(f"🎯 Agent swarm assembled: {len(primary_agents)} primary + {len(sub_agents)} sub-agents")
        return swarm_task
    
    async def coordinate_xionimus_workflows(self, swarm_task: AgentSwarmTask, 
                                          context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Coordinate agent workflows using XIONIMUS AI principles
        """
        try:
            start_time = time.time()
            
            # Initialize progress tracking
            progress_steps = [
                {"step": "swarm_assembly", "status": "completed", "timestamp": datetime.now().isoformat()},
                {"step": "task_analysis", "status": "active", "timestamp": datetime.now().isoformat()}
            ]
            
            # Decompose task for parallel processing
            subtasks = await self._decompose_task(swarm_task.primary_task, swarm_task.assigned_agents)
            
            progress_steps.append({
                "step": "parallel_execution", 
                "status": "active", 
                "timestamp": datetime.now().isoformat(),
                "subtasks": len(subtasks)
            })
            
            # Execute tasks in parallel with cross-agent coordination
            agent_results = {}
            coordination_data = {}
            
            if swarm_task.collaboration_type == "parallel":
                # Parallel execution with coordination
                tasks = []
                for agent_name, subtask in subtasks.items():
                    if agent_name in self.agent_manager.agents:
                        agent = self.agent_manager.agents[agent_name]
                        task_context = {**context, "coordination_id": swarm_task.task_id}
                        tasks.append(self._execute_agent_with_coordination(
                            agent, subtask, task_context, coordination_data
                        ))
                
                if tasks:
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    for i, result in enumerate(results):
                        if not isinstance(result, Exception):
                            agent_name = list(subtasks.keys())[i]
                            agent_results[agent_name] = result
            
            else:  # Sequential execution with adaptive learning
                for agent_name, subtask in subtasks.items():
                    if agent_name in self.agent_manager.agents:
                        agent = self.agent_manager.agents[agent_name]
                        enhanced_context = {
                            **context, 
                            "previous_results": agent_results,
                            "coordination_id": swarm_task.task_id
                        }
                        
                        result = await agent.execute_task(subtask, enhanced_context)
                        agent_results[agent_name] = result
            
            progress_steps.append({
                "step": "synthesis", 
                "status": "active", 
                "timestamp": datetime.now().isoformat()
            })
            
            # Synthesize results using collective intelligence
            final_result = await self._synthesize_agent_results(
                agent_results, swarm_task, coordination_data
            )
            
            # Update performance metrics and discover patterns
            execution_time = time.time() - start_time
            await self._update_performance_metrics(swarm_task, agent_results, execution_time)
            await self._discover_xionimus_ai_patterns(swarm_task, agent_results, coordination_data)
            
            progress_steps.append({
                "step": "completion", 
                "status": "completed", 
                "timestamp": datetime.now().isoformat(),
                "execution_time": f"{execution_time:.2f}s"
            })
            
            # Clean up active swarm
            del self.active_swarms[swarm_task.task_id]
            
            return {
                "result": final_result,
                "swarm_coordination": {
                    "agents_used": swarm_task.assigned_agents,
                    "sub_agents_created": swarm_task.sub_agents,
                    "collaboration_type": swarm_task.collaboration_type,
                    "execution_time": execution_time,
                    "progress_steps": progress_steps,
                    "xionimus_ai_patterns": swarm_task.xionimus_ai_patterns
                },
                "xionimus_metadata": {
                    "complexity_score": swarm_task.complexity_score,
                    "collective_intelligence_used": len(agent_results) > 1,
                    "patterns_discovered": len(swarm_task.xionimus_ai_patterns),
                    "coordination_quality": self._assess_coordination_quality(coordination_data)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error coordinating XIONIMUS workflows: {e}")
            return {
                "result": {"status": "error", "error": str(e)},
                "swarm_coordination": {"error": "Coordination failed"},
                "xionimus_metadata": {"error": str(e)}
            }
    
    def _count_complexity_keywords(self, request: str) -> float:
        """Count complexity-indicating keywords"""
        complexity_keywords = [
            'integrate', 'optimize', 'analyze', 'implement', 'design', 'architecture',
            'system', 'platform', 'framework', 'algorithm', 'machine learning', 'ai',
            'database', 'api', 'microservice', 'deployment', 'scalable', 'performance'
        ]
        
        request_lower = request.lower()
        matches = sum(1 for keyword in complexity_keywords if keyword in request_lower)
        return min(1.0, matches / 5)  # Normalize to 0-1
    
    def _analyze_technical_depth(self, request: str) -> float:
        """Analyze technical depth of the request"""
        technical_indicators = [
            'function', 'class', 'method', 'variable', 'algorithm', 'data structure',
            'database', 'sql', 'api', 'rest', 'graphql', 'microservice', 'docker',
            'kubernetes', 'aws', 'cloud', 'server', 'client', 'frontend', 'backend'
        ]
        
        request_lower = request.lower()
        technical_score = sum(1 for indicator in technical_indicators if indicator in request_lower)
        return min(1.0, technical_score / 8)
    
    def _detect_multi_domain_requirements(self, request: str) -> float:
        """Detect if request spans multiple domains"""
        domains = {
            'web': ['web', 'html', 'css', 'javascript', 'react', 'vue', 'angular'],
            'backend': ['backend', 'server', 'api', 'database', 'sql'],
            'ai': ['ai', 'machine learning', 'neural', 'model', 'training'],
            'devops': ['deploy', 'docker', 'kubernetes', 'ci/cd', 'testing'],
            'mobile': ['mobile', 'ios', 'android', 'app'],
            'data': ['data', 'analytics', 'visualization', 'statistics']
        }
        
        request_lower = request.lower()
        domains_detected = 0
        
        for domain, keywords in domains.items():
            if any(keyword in request_lower for keyword in keywords):
                domains_detected += 1
        
        return min(1.0, domains_detected / 3)  # Normalize
    
    def _analyze_context_dependency(self, request: str, context: Dict[str, Any]) -> float:
        """Analyze how much the request depends on context"""
        if not context:
            return 0.1
        
        context_indicators = ['previous', 'based on', 'using', 'with', 'from']
        request_lower = request.lower()
        
        context_score = sum(1 for indicator in context_indicators if indicator in request_lower)
        context_richness = len(context) / 10  # Normalize context richness
        
        return min(1.0, (context_score / 3) + context_richness)
    
    def _apply_pattern_matching(self, request: str, complexity_indicators: Dict[str, float]) -> float:
        """Apply discovered adaptive patterns to boost complexity analysis"""
        if not self.discovered_patterns:
            return 0.0
        
        # Simple pattern matching for now - can be enhanced with ML
        pattern_boost = 0.0
        request_lower = request.lower()
        
        for pattern in self.discovered_patterns.values():
            # Check if request matches pattern characteristics
            characteristic_matches = 0
            total_characteristics = len(pattern.task_characteristics)
            
            if total_characteristics > 0:
                for char_key, char_value in pattern.task_characteristics.items():
                    if char_key in complexity_indicators:
                        if abs(complexity_indicators[char_key] - char_value) < 0.3:
                            characteristic_matches += 1
                
                match_ratio = characteristic_matches / total_characteristics
                if match_ratio > 0.6:  # Good match
                    pattern_boost += pattern.success_rate * 2.0  # Boost based on pattern success
        
        return min(2.0, pattern_boost)  # Cap the boost
    
    async def _select_primary_agents(self, request: str, context: Dict[str, Any] = None) -> List[str]:
        """Select primary agents based on enhanced request analysis and adaptive patterns"""
        try:
            # Use enhanced context analysis for better agent selection
            context_analysis = self.context_analyzer.analyze_content(request, context)
            enhanced_recommendations = self.context_analyzer.get_agent_recommendations(context_analysis)
            
            self.logger.info(f"Enhanced agent selection - Primary domain: {context_analysis.primary_domain.value}, "
                           f"Recommendations: {enhanced_recommendations}")
            
            primary_agents = []
            
            # Add agents based on enhanced analysis
            if enhanced_recommendations:
                # Sort by confidence and take top agents
                sorted_agents = sorted(enhanced_recommendations.items(), key=lambda x: x[1], reverse=True)
                for agent_name, confidence in sorted_agents:
                    if confidence >= 0.4:  # Only high-confidence agents
                        primary_agents.append(agent_name)
            
            # If enhanced analysis doesn't provide good agents, use fallback
            if not primary_agents:
                self.logger.info("Enhanced analysis didn't provide agents, using fallback selection")
                best_agent = self.agent_manager._select_best_agent_fallback(request, context or {})
                if best_agent:
                    primary_agents.append(best_agent.name)
            
            # Add complementary agents based on domain analysis
            request_lower = request.lower()
            
            # Multi-domain detection for additional agents
            if context_analysis.primary_domain == TaskDomain.RESEARCH or \
               any(keyword in request_lower for keyword in ['research', 'information', 'latest', 'current']):
                if 'Research Agent' not in primary_agents:
                    primary_agents.append('Research Agent')
            
            if context_analysis.primary_domain == TaskDomain.WRITING or \
               any(keyword in request_lower for keyword in ['write', 'document', 'explain', 'describe']):
                if 'Writing Agent' not in primary_agents:
                    primary_agents.append('Writing Agent')
            
            if context_analysis.primary_domain == TaskDomain.TESTING or \
               any(keyword in request_lower for keyword in ['test', 'quality', 'validate', 'check']):
                if 'QA Agent' not in primary_agents:
                    primary_agents.append('QA Agent')
            
            if context_analysis.primary_domain == TaskDomain.DATA_ANALYSIS or \
               any(keyword in request_lower for keyword in ['data', 'analyze', 'statistics', 'chart']):
                if 'Data Agent' not in primary_agents:
                    primary_agents.append('Data Agent')
            
            return primary_agents[:4]  # Limit to 4 primary agents for performance
            
        except Exception as e:
            self.logger.error(f"Enhanced agent selection failed: {e}, using original method")
            # Fallback to original implementation
            best_agent = self.agent_manager._select_best_agent_fallback(request, context or {})
            
            primary_agents = []
            if best_agent:
                primary_agents.append(best_agent.name)
            
            return primary_agents
    
    def _determine_collaboration_type(self, complexity: ComplexityLevel, agents: List[str]) -> str:
        """Determine the best collaboration type for the agent swarm"""
        if complexity == ComplexityLevel.SIMPLE or len(agents) <= 1:
            return "sequential"
        elif complexity == ComplexityLevel.XIONIMUS_AI:
            return "xionimus_ai"
        else:
            return "parallel"
    
    async def _create_specialized_sub_agents(self, request: str, primary_agents: List[str]) -> List[str]:
        """Create specialized sub-agents for complex tasks"""
        # For now, return conceptual sub-agent names
        # In a full implementation, these would be dynamically created agent instances
        sub_agents = []
        
        request_lower = request.lower()
        
        if 'ui' in request_lower or 'interface' in request_lower:
            sub_agents.append('UI/UX Specialist Agent')
        
        if 'database' in request_lower or 'data model' in request_lower:
            sub_agents.append('Database Architecture Agent')
        
        if 'integration' in request_lower or 'api' in request_lower:
            sub_agents.append('Integration Specialist Agent')
        
        if 'performance' in request_lower or 'optimization' in request_lower:
            sub_agents.append('Performance Optimization Agent')
        
        return sub_agents[:3]  # Limit sub-agents
    
    async def _decompose_task(self, task: str, agents: List[str]) -> Dict[str, str]:
        """Decompose main task into subtasks for each agent"""
        subtasks = {}
        
        # Simple task decomposition - can be enhanced with AI
        for agent_name in agents:
            if agent_name == 'Code Agent':
                subtasks[agent_name] = f"Generate code implementation for: {task}"
            elif agent_name == 'Research Agent':
                subtasks[agent_name] = f"Research current best practices and technologies for: {task}"
            elif agent_name == 'Writing Agent':
                subtasks[agent_name] = f"Create documentation and explanations for: {task}"
            elif agent_name == 'Data Agent':
                subtasks[agent_name] = f"Analyze data requirements and structure for: {task}"
            elif agent_name == 'QA Agent':
                subtasks[agent_name] = f"Define testing strategy and quality measures for: {task}"
            else:
                subtasks[agent_name] = f"Provide specialized assistance for: {task}"
        
        return subtasks
    
    async def _execute_agent_with_coordination(self, agent: BaseAgent, subtask: str, 
                                             context: Dict[str, Any], 
                                             coordination_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent task with coordination tracking"""
        start_time = time.time()
        
        try:
            result = await agent.execute_task(subtask, context)
            execution_time = time.time() - start_time
            
            # Track coordination data
            coordination_data[agent.name] = {
                "execution_time": execution_time,
                "status": "success",
                "result_quality": self._assess_result_quality(result)
            }
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            coordination_data[agent.name] = {
                "execution_time": execution_time,
                "status": "error",
                "error": str(e)
            }
            raise e
    
    async def _synthesize_agent_results(self, agent_results: Dict[str, Any], 
                                       swarm_task: AgentSwarmTask,
                                       coordination_data: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize results from multiple agents using collective intelligence"""
        if not agent_results:
            return {"status": "error", "error": "No agent results to synthesize"}
        
        # Combine successful results
        successful_results = {}
        errors = []
        
        for agent_name, result in agent_results.items():
            if isinstance(result, dict) and result.get("status") != "error":
                successful_results[agent_name] = result
            else:
                errors.append(f"{agent_name}: {result.get('error', 'Unknown error')}")
        
        if not successful_results:
            return {"status": "error", "errors": errors}
        
        # Create synthesized response
        synthesis = {
            "status": "completed",
            "primary_result": self._select_primary_result(successful_results),
            "supporting_results": {k: v for k, v in successful_results.items()},
            "collective_insights": self._extract_collective_insights(successful_results),
            "synthesis_metadata": {
                "agents_contributed": len(successful_results),
                "total_agents_attempted": len(agent_results),
                "synthesis_quality": self._assess_synthesis_quality(successful_results),
                "xionimus_ai_properties": self._detect_xionimus_ai_properties(successful_results)
            }
        }
        
        if errors:
            synthesis["partial_errors"] = errors
        
        return synthesis
    
    def _select_primary_result(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Select the primary result from multiple agent results"""
        # Prioritize based on agent specialization and result quality
        priority_order = ['Code Agent', 'Research Agent', 'Writing Agent', 'Data Agent']
        
        for agent_name in priority_order:
            if agent_name in results:
                result = results[agent_name]
                if isinstance(result, dict) and result.get("status") == "completed":
                    return result
        
        # Fallback to first successful result
        for result in results.values():
            if isinstance(result, dict) and result.get("status") == "completed":
                return result
        
        return {"status": "error", "error": "No suitable primary result found"}
    
    def _extract_collective_insights(self, results: Dict[str, Any]) -> List[str]:
        """Extract insights that emerge from combining multiple agent results"""
        insights = []
        
        # Look for common themes across results
        content_words = []
        for agent_name, result in results.items():
            if isinstance(result, dict) and "content" in result:
                content = str(result["content"]).lower()
                content_words.extend(content.split())
        
        # Simple insight extraction (can be enhanced with NLP)
        if len(content_words) > 50:
            insights.append("Complex multi-domain solution requiring integrated approach")
        
        if len(results) >= 3:
            insights.append("Multi-agent collaboration produced comprehensive solution")
        
        return insights
    
    def _assess_result_quality(self, result: Dict[str, Any]) -> float:
        """Assess the quality of an individual agent result"""
        if not isinstance(result, dict):
            return 0.1
        
        quality_score = 0.5  # Base score
        
        # Check for completion
        if result.get("status") == "completed":
            quality_score += 0.3
        
        # Check for content richness
        if "content" in result:
            content_length = len(str(result["content"]))
            quality_score += min(0.2, content_length / 1000)  # Normalize content length
        
        return min(1.0, quality_score)
    
    def _assess_synthesis_quality(self, results: Dict[str, Any]) -> float:
        """Assess the quality of the result synthesis"""
        if not results:
            return 0.0
        
        # Base quality from number of successful results
        quality = len(results) / 4  # Assume max 4 agents
        
        # Bonus for diverse agent types
        agent_types = len(set(results.keys()))
        quality += agent_types / 8  # Normalize by max agent types
        
        return min(1.0, quality)
    
    def _detect_xionimus_ai_properties(self, results: Dict[str, Any]) -> List[str]:
        """Detect adaptive properties from agent collaboration"""
        properties = []
        
        if len(results) >= 3:
            properties.append("multi_domain_synthesis")
        
        # Check for complementary results
        has_code = any("code" in str(result).lower() for result in results.values())
        has_research = any("research" in str(result).lower() for result in results.values())
        
        if has_code and has_research:
            properties.append("research_informed_development")
        
        return properties
    
    def _assess_coordination_quality(self, coordination_data: Dict[str, Any]) -> float:
        """Assess the quality of agent coordination"""
        if not coordination_data:
            return 0.0
        
        successful_agents = sum(1 for data in coordination_data.values() if data.get("status") == "success")
        total_agents = len(coordination_data)
        
        success_rate = successful_agents / total_agents if total_agents > 0 else 0
        
        # Consider execution time balance
        execution_times = [data.get("execution_time", 0) for data in coordination_data.values()]
        if execution_times:
            time_variance = max(execution_times) - min(execution_times)
            time_balance = 1.0 - min(1.0, time_variance / 30)  # Penalize large time differences
        else:
            time_balance = 1.0
        
        return (success_rate * 0.7) + (time_balance * 0.3)
    
    async def _update_performance_metrics(self, swarm_task: AgentSwarmTask, 
                                         results: Dict[str, Any], execution_time: float):
        """Update performance metrics and learning data"""
        performance_data = {
            "task_id": swarm_task.task_id,
            "complexity_score": swarm_task.complexity_score,
            "agents_used": swarm_task.assigned_agents,
            "execution_time": execution_time,
            "success_rate": len([r for r in results.values() if isinstance(r, dict) and r.get("status") == "completed"]) / len(results) if results else 0,
            "timestamp": datetime.now(timezone.utc)
        }
        
        self.performance_history.append(performance_data)
        
        # Update collaboration success rates
        agent_combination = tuple(sorted(swarm_task.assigned_agents))
        if agent_combination not in self.collaboration_success_rates:
            self.collaboration_success_rates[agent_combination] = []
        
        self.collaboration_success_rates[agent_combination].append(performance_data["success_rate"])
        
        # Keep only recent history
        if len(self.performance_history) > 100:
            self.performance_history = self.performance_history[-100:]
    
    async def _discover_xionimus_ai_patterns(self, swarm_task: AgentSwarmTask, 
                                         results: Dict[str, Any], coordination_data: Dict[str, Any]):
        """Discover and record adaptive patterns from successful collaborations"""
        if len(results) < 2:  # Need multiple agents for patterns
            return
        
        success_rate = sum(1 for r in results.values() if isinstance(r, dict) and r.get("status") == "completed") / len(results)
        
        if success_rate >= 0.8:  # High success rate indicates good pattern
            pattern_id = str(uuid.uuid4())
            
            # Extract task characteristics
            task_characteristics = {
                "complexity_score": swarm_task.complexity_score,
                "agent_count": len(swarm_task.assigned_agents),
                "has_sub_agents": len(swarm_task.sub_agents) > 0,
                "collaboration_type": swarm_task.collaboration_type
            }
            
            # Calculate performance metrics
            avg_execution_time = sum(data.get("execution_time", 0) for data in coordination_data.values()) / len(coordination_data)
            performance_metrics = {
                "success_rate": success_rate,
                "avg_execution_time": avg_execution_time,
                "coordination_quality": self._assess_coordination_quality(coordination_data)
            }
            
            pattern = XionimusPattern(
                pattern_id=pattern_id,
                pattern_type="collaboration_success",
                success_rate=success_rate,
                agent_combinations=swarm_task.assigned_agents,
                task_characteristics=task_characteristics,
                performance_metrics=performance_metrics
            )
            
            self.discovered_patterns[pattern_id] = pattern
            swarm_task.xionimus_ai_patterns.append(pattern_id)
            
            self.logger.info(f"🌟 New adaptive pattern discovered: {pattern_id} (success rate: {success_rate:.2f})")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status including adaptive properties"""
        return {
            "active_swarms": len(self.active_swarms),
            "discovered_patterns": len(self.discovered_patterns),
            "performance_history_length": len(self.performance_history),
            "collaboration_combinations": len(self.collaboration_success_rates),
            "average_success_rate": sum(self.performance_history[-10:], key=lambda x: x["success_rate"]) / 10 if len(self.performance_history) >= 10 else 0,
            "xionimus_ai_capabilities": {
                "pattern_matching": len(self.discovered_patterns) > 0,
                "adaptive_routing": len(self.collaboration_success_rates) > 0,
                "collective_intelligence": any(len(swarm.assigned_agents) > 2 for swarm in self.active_swarms.values())
            },
            "system_evolution": {
                "patterns_discovered_today": len([p for p in self.discovered_patterns.values() 
                                                if (datetime.now(timezone.utc) - p.discovered_at).days == 0]),
                "most_successful_combination": max(self.collaboration_success_rates.items(), 
                                                 key=lambda x: sum(x[1])/len(x[1])) if self.collaboration_success_rates else None
            }
        }