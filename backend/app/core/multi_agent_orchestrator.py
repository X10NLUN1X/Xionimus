"""
Multi-Agent Orchestrator
Koordiniert spezialisierte AI-Agents für Xionimus AI
Hybrid-Ansatz: Emergent.sh Multi-Agent + Xionimus Transparenz
"""
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from enum import Enum

logger = logging.getLogger(__name__)


class AgentType(Enum):
    """Spezialisierte Agent-Typen"""
    ARCHITECT = "architect"
    ENGINEER = "engineer"
    UI_UX = "ui_ux"
    TESTER = "tester"
    DEBUGGER = "debugger"
    DOCUMENTER = "documenter"


class AgentStatus(Enum):
    """Agent Execution Status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class AgentTask:
    """Represents a task for an agent"""
    def __init__(self, agent_type: AgentType, description: str, priority: int = 5):
        self.agent_type = agent_type
        self.description = description
        self.priority = priority
        self.status = AgentStatus.PENDING
        self.result = None
        self.error = None
        self.start_time = None
        self.end_time = None
        self.thinking_steps = []
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for frontend"""
        return {
            "agent_type": self.agent_type.value,
            "description": self.description,
            "status": self.status.value,
            "result": self.result,
            "error": self.error,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration": (self.end_time - self.start_time).total_seconds() if self.start_time and self.end_time else None,
            "thinking_steps": self.thinking_steps
        }


class MultiAgentOrchestrator:
    """
    Orchestriert mehrere spezialisierte AI-Agents
    Inspiriert von Emergent.sh, aber mit Xionimus Transparenz
    """
    
    def __init__(self, ai_manager):
        self.ai_manager = ai_manager
        self.tasks: List[AgentTask] = []
        self.agent_results: Dict[AgentType, Any] = {}
        
    def plan_agents(self, user_request: str, research_data: Optional[str] = None) -> List[AgentTask]:
        """
        Plan which agents need to run based on user request
        Returns list of tasks in execution order
        """
        tasks = []
        
        # Analyze request complexity
        is_full_app = any(word in user_request.lower() for word in 
                         ["app", "application", "platform", "system", "website"])
        has_ui = any(word in user_request.lower() for word in 
                    ["ui", "design", "frontend", "interface", "website"])
        needs_tests = any(word in user_request.lower() for word in 
                         ["test", "testing", "quality"])
        
        # 1. ARCHITECT - Always needed for coding requests
        tasks.append(AgentTask(
            agent_type=AgentType.ARCHITECT,
            description="Design system architecture and plan implementation",
            priority=10
        ))
        
        # 2. ENGINEER - Core coding agent
        tasks.append(AgentTask(
            agent_type=AgentType.ENGINEER,
            description="Implement code based on architecture",
            priority=9
        ))
        
        # 3. UI/UX - If UI/frontend is needed
        if has_ui or is_full_app:
            tasks.append(AgentTask(
                agent_type=AgentType.UI_UX,
                description="Design user interface and experience",
                priority=8
            ))
        
        # 4. TESTER - If tests requested or complex app
        if needs_tests or is_full_app:
            tasks.append(AgentTask(
                agent_type=AgentType.TESTER,
                description="Create comprehensive tests",
                priority=7
            ))
        
        # 5. DEBUGGER - Always analyze and debug code
        tasks.append(AgentTask(
            agent_type=AgentType.DEBUGGER,
            description="Debug, optimize, and find potential issues",
            priority=6
        ))
        
        # 6. DOCUMENTER - Always good to have
        tasks.append(AgentTask(
            agent_type=AgentType.DOCUMENTER,
            description="Generate documentation and README",
            priority=5
        ))
        
        self.tasks = tasks
        logger.info(f"📋 Planned {len(tasks)} agents: {[t.agent_type.value for t in tasks]}")
        return tasks
    
    async def execute_parallel(self, api_keys: Dict[str, str], user_request: str, 
                               research_data: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute agents in parallel where possible
        Returns consolidated results
        """
        logger.info("🚀 Starting parallel agent execution")
        
        # Group tasks by dependency
        # Architect must run first, then others can run parallel
        architect_task = next(t for t in self.tasks if t.agent_type == AgentType.ARCHITECT)
        other_tasks = [t for t in self.tasks if t.agent_type != AgentType.ARCHITECT]
        
        # Execute Architect first
        architect_result = await self._execute_task(architect_task, api_keys, user_request, research_data)
        
        # Execute others in parallel
        parallel_results = await asyncio.gather(
            *[self._execute_task(task, api_keys, user_request, research_data, architect_result) 
              for task in other_tasks],
            return_exceptions=True
        )
        
        # Consolidate results
        consolidated = self._consolidate_results()
        logger.info("✅ Parallel execution completed")
        return consolidated
    
    async def execute_sequential(self, api_keys: Dict[str, str], user_request: str,
                                 research_data: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute agents sequentially (fallback if parallel not possible)
        """
        logger.info("⏭️ Starting sequential agent execution")
        
        previous_result = None
        for task in self.tasks:
            result = await self._execute_task(task, api_keys, user_request, research_data, previous_result)
            previous_result = result
        
        consolidated = self._consolidate_results()
        logger.info("✅ Sequential execution completed")
        return consolidated
    
    async def _execute_task(self, task: AgentTask, api_keys: Dict[str, str], 
                           user_request: str, research_data: Optional[str],
                           previous_result: Optional[Any] = None) -> Any:
        """Execute a single agent task"""
        task.status = AgentStatus.RUNNING
        task.start_time = datetime.now(timezone.utc)
        
        logger.info(f"🤖 Executing {task.agent_type.value} agent: {task.description}")
        
        try:
            # Generate agent-specific prompt
            prompt = self._generate_agent_prompt(
                task.agent_type, user_request, research_data, previous_result
            )
            
            # Add thinking step
            task.thinking_steps.append(f"Analyzing {task.agent_type.value} requirements...")
            
            # Select best AI model for this agent type
            provider, model = self._select_agent_model(task.agent_type)
            logger.info(f"🤖 {task.agent_type.value} using {provider}/{model}")
            
            # Execute with AI Manager
            response = await self.ai_manager.generate_response(
                provider=provider,
                model=model,
                messages=[{"role": "user", "content": prompt}],
                stream=False,
                api_keys=api_keys
            )
            
            task.result = response.get("content", "")
            task.status = AgentStatus.COMPLETED
            task.end_time = datetime.now(timezone.utc)
            
            # Store in results
            self.agent_results[task.agent_type] = task.result
            
            logger.info(f"✅ {task.agent_type.value} agent completed")
            return task.result
            
        except Exception as e:
            task.status = AgentStatus.FAILED
            task.error = str(e)
            task.end_time = datetime.now(timezone.utc)
            logger.error(f"❌ {task.agent_type.value} agent failed: {e}")
            return None
    
    def _select_agent_model(self, agent_type: AgentType) -> tuple[str, str]:
        """
        Select the best AI model for each agent type
        Returns: (provider, model)
        
        RESEARCH-BASED Multi-Provider Strategy (Updated 2025):
        
        - ARCHITECT: Claude Opus 4.1 (BEST for software architecture!)
          * 74.5% SWE-bench score (highest)
          * Superior multi-file coordination
          * Better for complex, agentic design decisions
          * Understands practicality over theoretical perfectionism
        
        - ENGINEER: Claude Sonnet 4-5 (industry-best for clean code)
          * Fastest, most reliable code generation
          * Excellent error handling
          * Best practices built-in
        
        - UI_UX: OpenAI GPT-4o (creative, modern design)
          * Superior Tailwind CSS generation
          * Knows latest design trends
          * Best accessibility implementation
        
        - TESTER: Claude Sonnet 4-5 (fast, thorough testing)
          * Quick test generation
          * Catches edge cases
          * Writes maintainable tests
        
        - DEBUGGER: Claude Opus 4.1 (BEST for debugging!)
          * Deep reasoning for complex bugs
          * Multi-file bug tracking
          * Root cause analysis
          * Performance debugging
        
        - DOCUMENTER: OpenAI GPT-4o (clear, beginner-friendly)
          * Clearest explanations
          * Perfect markdown formatting
          * Great code examples
        
        Why this combination:
        - Provider Diversification: OpenAI + Anthropic + Perplexity
        - Best-in-Class: Each model for its proven strength
        - Cost-Efficiency: Expensive models only where justified
        - Speed: Fast models for parallelizable tasks
        - Redundancy: Works even if one provider fails
        """
        model_mapping = {
            AgentType.ARCHITECT: ("anthropic", "claude-opus-4-1-20250805"),     # BEST for architecture (74.5% SWE-bench)
            AgentType.ENGINEER: ("anthropic", "claude-sonnet-4-5-20250929"),    # BEST for fast, clean coding
            AgentType.UI_UX: ("openai", "gpt-4o"),                              # BEST for creative design
            AgentType.TESTER: ("anthropic", "claude-sonnet-4-5-20250929"),      # FAST thorough testing
            AgentType.DEBUGGER: ("anthropic", "claude-opus-4-1-20250805"),      # BEST for debugging (deep reasoning)
            AgentType.DOCUMENTER: ("openai", "gpt-4o"),                         # BEST for clear docs
        }
        
        return model_mapping.get(agent_type, ("anthropic", "claude-sonnet-4-5-20250929"))
    
    def _generate_agent_prompt(self, agent_type: AgentType, user_request: str,
                              research_data: Optional[str], previous_result: Optional[Any]) -> str:
        """Generate specialized prompt for each agent type"""
        
        base_context = f"""User Request: {user_request}

Research Data: {research_data[:2000] if research_data else 'None'}

Previous Agent Results: {previous_result[:1000] if previous_result else 'None'}
"""
        
        prompts = {
            AgentType.ARCHITECT: f"""{base_context}

Role: System Architect

Your task: Design the system architecture for this request.

Provide:
1. **High-Level Architecture**: Components, services, layers
2. **Technology Stack**: Languages, frameworks, libraries
3. **Data Models**: Database schema, entities
4. **API Endpoints**: Routes and their purposes
5. **File Structure**: Directory layout

Format as structured markdown. Be specific and actionable.""",

            AgentType.ENGINEER: f"""{base_context}

Role: Software Engineer

Your task: Implement the code based on the architecture.

Provide:
1. **Complete Code**: All files with full implementation
2. **Code Comments**: Explain complex logic
3. **Error Handling**: Proper try-catch blocks
4. **Best Practices**: Follow coding standards

Generate production-ready code. Include all necessary files.""",

            AgentType.UI_UX: f"""{base_context}

Role: UI/UX Designer

Your task: Design the user interface and experience.

Provide:
1. **Component Design**: UI components and their structure
2. **Styling**: CSS/Tailwind classes, color scheme
3. **User Flow**: Navigation and interactions
4. **Responsive Design**: Mobile, tablet, desktop
5. **Accessibility**: ARIA labels, keyboard navigation

Focus on modern, beautiful, and intuitive design.""",

            AgentType.TESTER: f"""{base_context}

Role: QA Tester

Your task: Create comprehensive tests.

Provide:
1. **Unit Tests**: Test individual functions
2. **Integration Tests**: Test component interactions
3. **E2E Tests**: Test complete user flows
4. **Test Cases**: Edge cases and error scenarios
5. **Test Setup**: Mock data and fixtures

Use appropriate testing frameworks (Jest, Pytest, etc.).""",

            AgentType.DEBUGGER: f"""{base_context}

Role: Senior Debugger & Code Analyzer

Your task: Deep analysis, debugging, and optimization of the code.

Analyze the code from previous agents and provide:

1. **Bug Detection**: Find potential bugs, race conditions, edge cases
2. **Performance Issues**: Identify bottlenecks, memory leaks, inefficiencies
3. **Security Vulnerabilities**: Check for SQL injection, XSS, CSRF, etc.
4. **Code Quality**: Suggest refactorings, better patterns
5. **Error Handling**: Verify all error cases are handled
6. **Edge Cases**: List scenarios that might break the code
7. **Fixes & Improvements**: Provide concrete code fixes

Use deep reasoning to trace through the code logic. Be thorough and critical.""",

            AgentType.DOCUMENTER: f"""{base_context}

Role: Technical Writer

Your task: Generate comprehensive documentation.

Provide:
1. **README.md**: Overview, setup, usage
2. **API Documentation**: Endpoints, parameters, responses
3. **Code Comments**: Inline documentation
4. **Examples**: Usage examples and tutorials
5. **Troubleshooting**: Common issues and solutions

Make it clear and beginner-friendly."""
        }
        
        return prompts.get(agent_type, base_context)
    
    def _consolidate_results(self) -> Dict[str, Any]:
        """Consolidate all agent results into final output"""
        
        # Combine all agent outputs
        consolidated_code = ""
        consolidated_docs = ""
        
        # Priority order: Architect → Engineer → UI/UX → Tester → Documenter
        for agent_type in [AgentType.ARCHITECT, AgentType.ENGINEER, AgentType.UI_UX, 
                          AgentType.TESTER, AgentType.DOCUMENTER]:
            if agent_type in self.agent_results:
                result = self.agent_results[agent_type]
                
                if agent_type == AgentType.DOCUMENTER:
                    consolidated_docs += f"\n\n{result}"
                else:
                    consolidated_code += f"\n\n## {agent_type.value.upper()} OUTPUT\n\n{result}"
        
        return {
            "code": consolidated_code,
            "documentation": consolidated_docs,
            "agent_tasks": [task.to_dict() for task in self.tasks],
            "success": all(task.status == AgentStatus.COMPLETED for task in self.tasks)
        }
    
    def get_progress_updates(self) -> List[Dict[str, Any]]:
        """Get current progress of all agents for Activity Panel"""
        return [task.to_dict() for task in self.tasks]


# Global orchestrator instance
_orchestrator = None

def get_orchestrator(ai_manager):
    """Get or create orchestrator instance"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = MultiAgentOrchestrator(ai_manager)
    return _orchestrator
