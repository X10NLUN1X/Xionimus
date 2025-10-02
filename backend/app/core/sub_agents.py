"""
Sub-Agent System - Emergent-Style Specialized Agents
Integration Playbook Expert & Troubleshooting Agent
"""
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class IntegrationPlaybookExpert:
    """
    Expert agent for third-party integrations
    Provides playbooks for common integrations
    """
    
    VERIFIED_PLAYBOOKS = {
        "openai": {
            "type": "AI/LLM",
            "verified": True,
            "api_keys": ["OPENAI_API_KEY"],
            "models": ["gpt-4o", "gpt-4.1", "o1", "o3"],
            "installation": "pip install openai",
            "example_code": """
import openai

client = openai.OpenAI(api_key="YOUR_API_KEY")

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hello!"}]
)
            """,
            "common_issues": [
                "Rate limiting - use exponential backoff",
                "Context length - monitor token usage",
                "API key - store securely in environment variables"
            ]
        },
        "anthropic": {
            "type": "AI/LLM",
            "verified": True,
            "api_keys": ["ANTHROPIC_API_KEY"],
            "models": ["claude-sonnet-4-5-20250929"],
            "installation": "pip install anthropic",
            "example_code": """
import anthropic

client = anthropic.Anthropic(api_key="YOUR_API_KEY")

response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello!"}]
)
            """,
            "common_issues": [
                "Extended thinking - use thinking parameter for complex tasks",
                "Max tokens - adjust based on task complexity"
            ]
        },
        "stripe": {
            "type": "Payment",
            "verified": True,
            "api_keys": ["STRIPE_SECRET_KEY", "STRIPE_PUBLISHABLE_KEY"],
            "installation": "pip install stripe",
            "example_code": """
import stripe

stripe.api_key = "YOUR_SECRET_KEY"

# Create payment intent
intent = stripe.PaymentIntent.create(
    amount=1000,
    currency="usd",
    payment_method_types=["card"]
)
            """,
            "common_issues": [
                "Webhook security - verify signatures",
                "Test mode - use test keys for development"
            ]
        },
        "github": {
            "type": "DevOps",
            "verified": True,
            "api_keys": ["GITHUB_TOKEN or OAuth"],
            "installation": "pip install PyGithub",
            "example_code": """
from github import Github

g = Github("YOUR_TOKEN")

# Get user repos
repos = g.get_user().get_repos()
            """,
            "common_issues": [
                "Rate limiting - check X-RateLimit headers",
                "OAuth scopes - ensure correct permissions"
            ]
        }
    }
    
    def get_playbook(self, integration_name: str) -> Dict[str, Any]:
        """Get integration playbook"""
        integration_name = integration_name.lower()
        
        if integration_name in self.VERIFIED_PLAYBOOKS:
            playbook = self.VERIFIED_PLAYBOOKS[integration_name].copy()
            playbook["status"] = "VERIFIED"
            logger.info(f"📚 Providing VERIFIED playbook for: {integration_name}")
            return playbook
        else:
            logger.warning(f"⚠️ No verified playbook for: {integration_name}")
            return {
                "status": "UNVERIFIED",
                "message": f"No verified playbook available for {integration_name}. Please refer to official documentation."
            }
    
    def list_available_integrations(self) -> List[str]:
        """List all available integrations"""
        return list(self.VERIFIED_PLAYBOOKS.keys())
    
    def search_integrations(self, query: str) -> List[Dict[str, Any]]:
        """Search for integrations by type or name"""
        query = query.lower()
        results = []
        
        for name, details in self.VERIFIED_PLAYBOOKS.items():
            if query in name.lower() or query in details['type'].lower():
                results.append({
                    "name": name,
                    "type": details['type'],
                    "verified": details['verified']
                })
        
        return results


class TroubleshootingAgent:
    """
    Expert agent for debugging and root cause analysis
    """
    
    COMMON_ISSUES = {
        "connection_refused": {
            "symptom": "Connection refused",
            "possible_causes": [
                "Service not running",
                "Wrong port",
                "Firewall blocking connection",
                "Service crashed"
            ],
            "solutions": [
                "Check if service is running: sudo supervisorctl status",
                "Verify port configuration in .env",
                "Check firewall rules",
                "Review service logs: tail -n 50 /var/log/supervisor/*.log"
            ]
        },
        "import_error": {
            "symptom": "ImportError or ModuleNotFoundError",
            "possible_causes": [
                "Package not installed",
                "Wrong virtual environment",
                "Package name mismatch",
                "Circular import"
            ],
            "solutions": [
                "Install package: pip install <package>",
                "Verify virtual environment is activated",
                "Check package name spelling",
                "Restructure imports to avoid circular dependencies"
            ]
        },
        "api_key_error": {
            "symptom": "Authentication failed or API key invalid",
            "possible_causes": [
                "API key not set",
                "API key expired",
                "Wrong environment variable name",
                "API key has wrong permissions"
            ],
            "solutions": [
                "Set API key in .env file",
                "Regenerate API key from provider dashboard",
                "Check environment variable name matches code",
                "Verify API key permissions/scopes"
            ]
        },
        "database_error": {
            "symptom": "Database connection error",
            "possible_causes": [
                "MongoDB not running",
                "Wrong connection string",
                "Authentication failed",
                "Network issue"
            ],
            "solutions": [
                "Check MongoDB status: sudo supervisorctl status mongodb",
                "Verify MONGO_URL in .env",
                "Check MongoDB credentials",
                "Test connection: mongo <connection_string>"
            ]
        }
    }
    
    def analyze_error(self, error_message: str, component: str) -> Dict[str, Any]:
        """
        Analyze error message and provide troubleshooting guidance
        """
        error_lower = error_message.lower()
        
        # Match against common issues
        matched_issue = None
        for issue_key, issue_data in self.COMMON_ISSUES.items():
            if any(keyword in error_lower for keyword in issue_data['symptom'].lower().split()):
                matched_issue = issue_data.copy()
                matched_issue['issue_type'] = issue_key
                break
        
        if matched_issue:
            logger.info(f"🔍 Matched common issue: {matched_issue['issue_type']}")
            return {
                "status": "analyzed",
                "component": component,
                "error": error_message,
                "diagnosis": matched_issue,
                "timestamp": datetime.now().isoformat()
            }
        else:
            logger.info(f"🔍 No match for error, providing general guidance")
            return {
                "status": "analyzed",
                "component": component,
                "error": error_message,
                "diagnosis": {
                    "symptom": "Unknown error",
                    "possible_causes": ["Check logs for detailed error message"],
                    "solutions": [
                        f"Review {component} logs",
                        "Search error message online",
                        "Check recent code changes"
                    ]
                },
                "timestamp": datetime.now().isoformat()
            }
    
    def generate_rca_report(self, analysis: Dict[str, Any]) -> str:
        """Generate Root Cause Analysis report"""
        lines = ["# 🔍 Root Cause Analysis Report\n"]
        
        lines.append(f"**Component**: {analysis['component']}")
        lines.append(f"**Error**: {analysis['error']}\n")
        
        diagnosis = analysis['diagnosis']
        
        lines.append("## Symptom")
        lines.append(diagnosis.get('symptom', 'Unknown'))
        
        lines.append("\n## Possible Causes")
        for cause in diagnosis.get('possible_causes', []):
            lines.append(f"- {cause}")
        
        lines.append("\n## Recommended Solutions")
        for i, solution in enumerate(diagnosis.get('solutions', []), 1):
            lines.append(f"{i}. {solution}")
        
        return "\n".join(lines)


class SubAgentManager:
    """Manager for all sub-agents"""
    
    def __init__(self):
        self.integration_expert = IntegrationPlaybookExpert()
        self.troubleshooting_agent = TroubleshootingAgent()
    
    def call_integration_expert(self, integration_name: str) -> Dict[str, Any]:
        """Call integration playbook expert"""
        logger.info(f"📞 Calling Integration Expert for: {integration_name}")
        return self.integration_expert.get_playbook(integration_name)
    
    def call_troubleshooting_agent(self, error: str, component: str) -> Dict[str, Any]:
        """Call troubleshooting agent"""
        logger.info(f"📞 Calling Troubleshooting Agent for: {component}")
        analysis = self.troubleshooting_agent.analyze_error(error, component)
        report = self.troubleshooting_agent.generate_rca_report(analysis)
        analysis['report'] = report
        return analysis
    
    def list_available_agents(self) -> List[Dict[str, str]]:
        """List all available sub-agents"""
        return [
            {
                "name": "Integration Playbook Expert",
                "endpoint": "/api/agents/integration",
                "description": "Provides verified integration playbooks for third-party services"
            },
            {
                "name": "Troubleshooting Agent",
                "endpoint": "/api/agents/troubleshoot",
                "description": "Analyzes errors and provides root cause analysis"
            },
            {
                "name": "Testing Agent",
                "endpoint": "/api/testing/run",
                "description": "Runs automated backend and frontend tests"
            },
            {
                "name": "Edit Agent",
                "endpoint": "/api/edit",
                "description": "Automatically edits existing code files based on bug fixes, improvements, or user requests"
            }
        ]


# Global instance
sub_agent_manager = SubAgentManager()
