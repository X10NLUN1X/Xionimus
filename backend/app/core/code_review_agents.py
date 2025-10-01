"""
Code Review Agent System - Part 1
Base agent and Code Analysis Agent
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
        self.findings: List[Dict[str, Any]] = []
    
    @abstractmethod
    async def analyze(self, code: str, context: Dict[str, Any], api_keys: Dict[str, str]) -> Dict[str, Any]:
        """Analyze code and return findings"""
        pass
    
    def create_finding(
        self,
        severity: str,
        category: str,
        title: str,
        description: str,
        file_path: Optional[str] = None,
        line_number: Optional[int] = None,
        code_snippet: Optional[str] = None,
        recommendation: Optional[str] = None,
        fix_suggestion: Optional[str] = None,
        fix_code: Optional[str] = None,
        impact: Optional[str] = None,
        effort: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a standardized finding"""
        return {
            "agent_name": self.agent_name,
            "severity": severity,
            "category": category,
            "title": title,
            "description": description,
            "file_path": file_path,
            "line_number": line_number,
            "code_snippet": code_snippet,
            "recommendation": recommendation,
            "fix_suggestion": fix_suggestion,
            "fix_code": fix_code,
            "impact": impact,
            "effort": effort
        }


# Import specialized agents will be added below
from .code_review_agents_impl import (
    CodeAnalysisAgent,
    DebugAgent,
    EnhancementAgent,
    TestEnhancementAgent,
    AgentManager
)

__all__ = [
    'BaseReviewAgent',
    'CodeAnalysisAgent',
    'DebugAgent',
    'EnhancementAgent',
    'TestEnhancementAgent',
    'AgentManager'
]
