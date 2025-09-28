from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from core.ai_orchestrator import orchestrator
from core.database import get_database
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Agent definitions
AGENTS = [
    {
        "id": "code",
        "name": "Code Agent",
        "description": "Specialized in code generation, analysis, and debugging",
        "capabilities": ["Code Generation", "Code Analysis", "Debugging", "Code Review"],
        "models": ["gpt-4o", "gpt-4o-mini", "claude-3-5-sonnet"],
        "icon": "Code"
    },
    {
        "id": "research",
        "name": "Research Agent",
        "description": "Specialized in deep web research and information gathering",
        "capabilities": ["Web Research", "Fact Checking", "Information Analysis"],
        "models": ["perplexity-sonar", "gpt-4o", "claude-3-5-sonnet"],
        "icon": "Search"
    },
    {
        "id": "writing",
        "name": "Writing Agent",
        "description": "Specialized in content creation and documentation",
        "capabilities": ["Content Creation", "Documentation", "Copywriting"],
        "models": ["gpt-4o", "claude-3-5-sonnet", "gpt-4o-mini"],
        "icon": "Edit"
    },
    {
        "id": "data",
        "name": "Data Agent",
        "description": "Specialized in data analysis and statistical insights",
        "capabilities": ["Data Analysis", "Statistical Analysis", "Data Visualization"],
        "models": ["gpt-4o", "claude-3-5-sonnet"],
        "icon": "BarChart"
    },
    {
        "id": "qa",
        "name": "QA Agent",
        "description": "Specialized in testing and quality assurance",
        "capabilities": ["Testing", "Quality Assurance", "Validation"],
        "models": ["gpt-4o", "perplexity-sonar", "claude-3-5-sonnet"],
        "icon": "CheckCircle"
    },
    {
        "id": "github",
        "name": "GitHub Agent",
        "description": "Specialized in repository management and version control",
        "capabilities": ["Repository Management", "Version Control", "Code Collaboration"],
        "models": ["gpt-4o", "claude-3-5-sonnet"],
        "icon": "GitBranch"
    },
    {
        "id": "file",
        "name": "File Agent",
        "description": "Specialized in file management and organization",
        "capabilities": ["File Management", "Organization", "Data Processing"],
        "models": ["gpt-4o", "claude-3-5-sonnet"],
        "icon": "FileText"
    },
    {
        "id": "session",
        "name": "Session Agent",
        "description": "Specialized in conversation management and state",
        "capabilities": ["Session Management", "State Management", "User Experience"],
        "models": ["gpt-4o", "claude-3-5-sonnet"],
        "icon": "MessageSquare"
    },
    {
        "id": "experimental",
        "name": "Experimental Agent",
        "description": "Advanced AI features and experimental capabilities",
        "capabilities": ["Advanced AI", "Experimental Features", "Innovation"],
        "models": ["gpt-4o", "claude-3-5-sonnet"],
        "icon": "Zap"
    }
]

@router.get("/")
async def get_agents() -> Dict[str, Any]:
    """Get all available agents"""
    services = orchestrator.get_available_services()
    
    return {
        "agents": AGENTS,
        "total_agents": len(AGENTS),
        "available_services": services,
        "status": "active"
    }

@router.get("/{agent_id}")
async def get_agent(agent_id: str) -> Dict[str, Any]:
    """Get specific agent information"""
    agent = next((a for a in AGENTS if a["id"] == agent_id), None)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return agent