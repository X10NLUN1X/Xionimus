"""
Code Review Agent System - Complete Pipeline
4 specialized agents: Analysis, Debug, Enhancement, Test
Parallel execution using emergent.sh style coordination
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime, timezone
import json
import re
import asyncio

logger = logging.getLogger(__name__)


class BaseReviewAgent(ABC):
    """Base class for all code review agents"""
    
    def __init__(self, agent_name: str, description: str):
        self.agent_name = agent_name
        self.description = description
    
    @abstractmethod
    async def analyze(self, code: str, context: Dict[str, Any], api_keys: Dict[str, str]) -> Dict[str, Any]:
        """Analyze code and return findings"""
        pass
    
    def create_finding(self, severity: str, category: str, title: str, description: str,
                      file_path: Optional[str] = None, line_number: Optional[int] = None,
                      recommendation: Optional[str] = None, fix_code: Optional[str] = None) -> Dict[str, Any]:
        """Create a standardized finding"""
        return {
            "agent_name": self.agent_name,
            "severity": severity,
            "category": category,
            "title": title,
            "description": description,
            "file_path": file_path,
            "line_number": line_number,
            "recommendation": recommendation,
            "fix_code": fix_code
        }


class CodeAnalysisAgent(BaseReviewAgent):
    """Code Analysis Agent - Quality, architecture, performance"""
    
    def __init__(self):
        super().__init__("code_analysis", "Code quality and architecture analysis")
    
    async def analyze(self, code: str, context: Dict[str, Any], api_keys: Dict[str, str]) -> Dict[str, Any]:
        """Analyze code quality"""
        logger.info(f"🔍 Analyzing {context.get('file_path', 'code')}")
        
        prompt = f"""Analyze this code for quality issues. Return JSON array of findings.

Code ({context.get('language', 'python')}):
```
{code[:3000]}  
```

Find issues in: code quality, architecture, performance, documentation.

Return JSON: [{{"severity": "high", "category": "quality", "title": "Issue", "description": "Details", "line_number": 10, "recommendation": "Fix"}}]"""

        try:
            from .ai_manager import AIManager
            ai_manager = AIManager()
            
            provider = 'openai' if api_keys.get('openai') else 'anthropic' if api_keys.get('anthropic') else None
            if not provider:
                return {"success": False, "error": "No API keys configured", "findings": []}
            
            model = 'gpt-4.1' if provider == 'openai' else 'claude-sonnet-4-5-20250929'
            response = await ai_manager.generate_response(provider, model, [{"role": "user", "content": prompt}], api_keys=api_keys)
            
            findings = []
            text = response.get('content', '')
            
            # Extract JSON
            match = re.search(r'\[.*\]', text, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group(0))
                    for item in data:
                        findings.append(self.create_finding(
                            severity=item.get('severity', 'medium'),
                            category=item.get('category', 'quality'),
                            title=item.get('title', 'Code Issue'),
                            description=item.get('description', ''),
                            file_path=context.get('file_path'),
                            line_number=item.get('line_number'),
                            recommendation=item.get('recommendation'),
                            fix_code=item.get('fix_code')
                        ))
                except:
                    pass
            
            if not findings:
                findings.append(self.create_finding('low', 'quality', 'Analysis Complete', text[:500]))
            
            quality_score = max(0, 100 - len([f for f in findings if f['severity'] in ['critical', 'high']]) * 15)
            
            return {
                "success": True,
                "findings": findings,
                "quality_score": quality_score,
                "summary": f"Found {len(findings)} issues"
            }
        except Exception as e:
            logger.error(f"Analysis error: {e}", exc_info=True)
            return {"success": False, "error": str(e), "findings": []}


class DebugAgent(BaseReviewAgent):
    """Debug Agent - Bug detection and error patterns"""
    
    def __init__(self):
        super().__init__("debug", "Bug detection and error analysis")
    
    async def analyze(self, code: str, context: Dict[str, Any], api_keys: Dict[str, str]) -> Dict[str, Any]:
        """Analyze for bugs"""
        logger.info(f"🐛 Debugging {context.get('file_path', 'code')}")
        
        prompt = f"""Find bugs in this code. Return JSON array.

Code:
```
{code[:3000]}
```

Find: runtime errors, logic bugs, error handling issues, edge cases.

Return JSON: [{{"severity": "critical", "title": "Bug", "description": "Details", "line_number": 10, "recommendation": "Fix"}}]"""

        try:
            from .ai_manager import AIManager
            ai_manager = AIManager()
            
            # Use Claude Opus 4.1 for debugging
            provider = 'anthropic' if api_keys.get('anthropic') else 'openai' if api_keys.get('openai') else None
            if not provider:
                return {"success": False, "error": "No API keys", "findings": []}
            
            model = 'claude-opus-4-1-20250805' if provider == 'anthropic' else 'gpt-4.1'
            response = await ai_manager.generate_response(provider, model, [{"role": "user", "content": prompt}], api_keys=api_keys)
            
            findings = []
            text = response.get('content', '')
            
            match = re.search(r'\[.*\]', text, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group(0))
                    for item in data:
                        findings.append(self.create_finding(
                            severity=item.get('severity', 'medium'),
                            category='bug',
                            title=item.get('title', 'Potential Bug'),
                            description=item.get('description', ''),
                            file_path=context.get('file_path'),
                            line_number=item.get('line_number'),
                            recommendation=item.get('recommendation')
                        ))
                except:
                    pass
            
            if not findings:
                findings.append(self.create_finding('low', 'bug', 'Debug Complete', text[:500]))
            
            return {
                "success": True,
                "findings": findings,
                "bugs_found": len(findings),
                "summary": f"Found {len(findings)} potential bugs"
            }
        except Exception as e:
            logger.error(f"Debug error: {e}", exc_info=True)
            return {"success": False, "error": str(e), "findings": []}


class EnhancementAgent(BaseReviewAgent):
    """Enhancement Agent - Code improvement and refactoring suggestions"""
    
    def __init__(self):
        super().__init__("enhancement", "Code enhancement and best practices")
    
    async def analyze(self, code: str, context: Dict[str, Any], api_keys: Dict[str, str]) -> Dict[str, Any]:
        """Analyze for enhancement opportunities"""
        logger.info(f"✨ Enhancing {context.get('file_path', 'code')}")
        
        prompt = f"""Suggest code improvements and enhancements. Return JSON array.

Code ({context.get('language', 'python')}):
```
{code[:3000]}
```

Find opportunities for: code readability, performance optimization, best practices, modern patterns, refactoring.

Return JSON: [{{"severity": "medium", "category": "enhancement", "title": "Improvement", "description": "Details", "line_number": 10, "recommendation": "Better approach", "fix_code": "improved code"}}]"""

        try:
            from .ai_manager import AIManager
            ai_manager = AIManager()
            
            # Use Claude for enhancement (best for code improvement)
            provider = 'anthropic' if api_keys.get('anthropic') else 'openai' if api_keys.get('openai') else None
            if not provider:
                return {"success": False, "error": "No API keys", "findings": []}
            
            model = 'claude-sonnet-4-5-20250929' if provider == 'anthropic' else 'gpt-4.1'
            response = await ai_manager.generate_response(provider, model, [{"role": "user", "content": prompt}], api_keys=api_keys)
            
            findings = []
            text = response.get('content', '')
            
            match = re.search(r'\[.*\]', text, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group(0))
                    for item in data:
                        findings.append(self.create_finding(
                            severity=item.get('severity', 'medium'),
                            category=item.get('category', 'enhancement'),
                            title=item.get('title', 'Enhancement Opportunity'),
                            description=item.get('description', ''),
                            file_path=context.get('file_path'),
                            line_number=item.get('line_number'),
                            recommendation=item.get('recommendation'),
                            fix_code=item.get('fix_code')
                        ))
                except:
                    pass
            
            if not findings:
                findings.append(self.create_finding('low', 'enhancement', 'Enhancement Analysis Complete', text[:500]))
            
            return {
                "success": True,
                "findings": findings,
                "enhancements_found": len(findings),
                "summary": f"Found {len(findings)} enhancement opportunities"
            }
        except Exception as e:
            logger.error(f"Enhancement error: {e}", exc_info=True)
            return {"success": False, "error": str(e), "findings": []}


class TestAgent(BaseReviewAgent):
    """Test Agent - Test coverage and test case recommendations"""
    
    def __init__(self):
        super().__init__("test", "Test coverage and test recommendations")
    
    async def analyze(self, code: str, context: Dict[str, Any], api_keys: Dict[str, str]) -> Dict[str, Any]:
        """Analyze test coverage needs"""
        logger.info(f"🧪 Testing analysis for {context.get('file_path', 'code')}")
        
        prompt = f"""Analyze this code for testing needs. Return JSON array of test recommendations.

Code ({context.get('language', 'python')}):
```
{code[:3000]}
```

Identify: missing test cases, edge cases to test, test structure recommendations, coverage gaps, unit test suggestions.

Return JSON: [{{"severity": "medium", "category": "testing", "title": "Test Case Needed", "description": "Details", "recommendation": "Test approach", "fix_code": "test code example"}}]"""

        try:
            from .ai_manager import AIManager
            ai_manager = AIManager()
            
            # Use GPT for testing (excellent at test generation)
            provider = 'openai' if api_keys.get('openai') else 'anthropic' if api_keys.get('anthropic') else None
            if not provider:
                return {"success": False, "error": "No API keys", "findings": []}
            
            model = 'gpt-4.1' if provider == 'openai' else 'claude-sonnet-4-5-20250929'
            response = await ai_manager.generate_response(provider, model, [{"role": "user", "content": prompt}], api_keys=api_keys)
            
            findings = []
            text = response.get('content', '')
            
            match = re.search(r'\[.*\]', text, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group(0))
                    for item in data:
                        findings.append(self.create_finding(
                            severity=item.get('severity', 'medium'),
                            category=item.get('category', 'testing'),
                            title=item.get('title', 'Test Recommendation'),
                            description=item.get('description', ''),
                            file_path=context.get('file_path'),
                            line_number=item.get('line_number'),
                            recommendation=item.get('recommendation'),
                            fix_code=item.get('fix_code')
                        ))
                except:
                    pass
            
            if not findings:
                findings.append(self.create_finding('low', 'testing', 'Test Analysis Complete', text[:500]))
            
            return {
                "success": True,
                "findings": findings,
                "test_recommendations": len(findings),
                "summary": f"Found {len(findings)} test recommendations"
            }
        except Exception as e:
            logger.error(f"Test analysis error: {e}", exc_info=True)
            return {"success": False, "error": str(e), "findings": []}


class AgentManager:
    """Coordinates review agents with parallel execution (emergent.sh style)"""
    
    def __init__(self):
        self.agents = {
            "code_analysis": CodeAnalysisAgent(),
            "debug": DebugAgent(),
            "enhancement": EnhancementAgent(),
            "test": TestAgent()
        }
    
    async def coordinate_review(self, code: str, context: Dict[str, Any], 
                               api_keys: Dict[str, str], review_scope: str = "full") -> Dict[str, Any]:
        """Coordinate review agents with parallel execution (emergent.sh style)"""
        logger.info(f"🎯 Starting {review_scope} review with parallel agent execution")
        
        results = {
            "agents": {},
            "all_findings": [],
            "summary": {},
            "started_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Determine which agents to run
        agents_to_run = list(self.agents.keys()) if review_scope == "full" else [review_scope]
        
        # Filter valid agents
        valid_agents = [(name, self.agents[name]) for name in agents_to_run if name in self.agents]
        
        if not valid_agents:
            logger.warning(f"No valid agents found for scope: {review_scope}")
            return results
        
        # Run agents in parallel (emergent.sh style) using asyncio.gather
        import asyncio
        
        async def run_agent(agent_name: str, agent: BaseReviewAgent):
            """Run single agent and handle errors"""
            try:
                logger.info(f"🚀 Running {agent_name} agent...")
                agent_result = await agent.analyze(code, context, api_keys)
                return agent_name, agent_result
            except Exception as e:
                logger.error(f"Agent {agent_name} failed: {e}", exc_info=True)
                return agent_name, {"success": False, "error": str(e), "findings": []}
        
        # Execute all agents in parallel
        agent_tasks = [run_agent(name, agent) for name, agent in valid_agents]
        agent_results = await asyncio.gather(*agent_tasks, return_exceptions=True)
        
        # Process results
        for result in agent_results:
            if isinstance(result, Exception):
                logger.error(f"Agent execution exception: {result}")
                continue
            
            agent_name, agent_result = result
            results["agents"][agent_name] = agent_result
            
            # Collect findings from successful agents
            if agent_result.get("success"):
                findings = agent_result.get("findings", [])
                results["all_findings"].extend(findings)
                logger.info(f"✅ {agent_name}: {len(findings)} findings")
            else:
                logger.warning(f"⚠️ {agent_name}: {agent_result.get('error', 'Unknown error')}")
        
        # Generate summary
        all_findings = results["all_findings"]
        results["summary"] = {
            "total_findings": len(all_findings),
            "critical": len([f for f in all_findings if f.get("severity") == "critical"]),
            "high": len([f for f in all_findings if f.get("severity") == "high"]),
            "medium": len([f for f in all_findings if f.get("severity") == "medium"]),
            "low": len([f for f in all_findings if f.get("severity") == "low"]),
            "agents_run": len(valid_agents),
            "agents_succeeded": len([r for r in results["agents"].values() if r.get("success")])
        }
        results["completed_at"] = datetime.now(timezone.utc).isoformat()
        
        logger.info(f"✅ Review complete: {len(all_findings)} findings from {results['summary']['agents_succeeded']}/{results['summary']['agents_run']} agents")
        return results
