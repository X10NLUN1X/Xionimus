"""
Code Review Agent System - MVP Version
2 specialized agents: Code Analysis + Debug Agent
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime, timezone
import json
import re

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
            
            model = 'gpt-4.1' if provider == 'openai' else 'claude-opus-4.1'
            response = ai_manager.generate_response(provider, model, [{"role": "user", "content": prompt}], api_keys)
            
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
            
            provider = 'openai' if api_keys.get('openai') else 'anthropic' if api_keys.get('anthropic') else None
            if not provider:
                return {"success": False, "error": "No API keys", "findings": []}
            
            model = 'gpt-4.1' if provider == 'openai' else 'claude-opus-4.1'
            response = ai_manager.generate_response(provider, model, [{"role": "user", "content": prompt}], api_keys)
            
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


class AgentManager:
    """Coordinates review agents"""
    
    def __init__(self):
        self.agents = {
            "code_analysis": CodeAnalysisAgent(),
            "debug": DebugAgent()
        }
    
    async def coordinate_review(self, code: str, context: Dict[str, Any], 
                               api_keys: Dict[str, str], review_scope: str = "full") -> Dict[str, Any]:
        """Coordinate review agents"""
        logger.info(f"🎯 Starting {review_scope} review")
        
        results = {
            "agents": {},
            "all_findings": [],
            "summary": {},
            "started_at": datetime.now(timezone.utc).isoformat()
        }
        
        agents_to_run = list(self.agents.keys()) if review_scope == "full" else [review_scope]
        
        for agent_name in agents_to_run:
            if agent_name not in self.agents:
                continue
            
            agent = self.agents[agent_name]
            try:
                agent_result = await agent.analyze(code, context, api_keys)
                results["agents"][agent_name] = agent_result
                if agent_result.get("success"):
                    results["all_findings"].extend(agent_result.get("findings", []))
            except Exception as e:
                logger.error(f"Agent {agent_name} failed: {e}")
                results["agents"][agent_name] = {"success": False, "error": str(e)}
        
        all_findings = results["all_findings"]
        results["summary"] = {
            "total_findings": len(all_findings),
            "critical": len([f for f in all_findings if f.get("severity") == "critical"]),
            "high": len([f for f in all_findings if f.get("severity") == "high"]),
            "medium": len([f for f in all_findings if f.get("severity") == "medium"]),
            "low": len([f for f in all_findings if f.get("severity") == "low"])
        }
        results["completed_at"] = datetime.now(timezone.utc).isoformat()
        
        logger.info(f"✅ Review complete: {len(all_findings)} findings")
        return results
