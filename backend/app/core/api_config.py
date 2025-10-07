"""
API Configuration for Multi-Agent System
Defines timeout and rate limit settings for all integrated APIs
"""
from pydantic import BaseModel
from typing import Optional


class APITimeouts(BaseModel):
    """Timeout configurations for each API provider"""
    
    # Perplexity API Timeouts
    PERPLEXITY_BASIC_TIMEOUT: int = 30  # seconds for basic queries
    PERPLEXITY_DEEP_RESEARCH_TIMEOUT: int = 300  # 5 minutes for deep research
    PERPLEXITY_CONNECTION_TIMEOUT: int = 10  # connection establishment timeout
    
    # OpenAI API Timeouts
    OPENAI_STANDARD_TIMEOUT: int = 60  # standard chat completions
    OPENAI_STREAMING_TIMEOUT: int = 120  # streaming responses
    OPENAI_FUNCTION_CALLING_TIMEOUT: int = 90  # function calling operations
    
    # Claude API Timeouts
    CLAUDE_STANDARD_TIMEOUT: int = 60  # standard messages
    CLAUDE_STREAMING_TIMEOUT: int = 120  # streaming responses
    CLAUDE_LONG_CONTEXT_TIMEOUT: int = 180  # for large context windows
    
    # GitHub API Timeouts
    GITHUB_STANDARD_TIMEOUT: int = 30  # most operations
    GITHUB_SEARCH_TIMEOUT: int = 60  # search operations
    GITHUB_CLONE_TIMEOUT: int = 300  # repository cloning


class APIRateLimits(BaseModel):
    """Rate limit configurations for each API provider"""
    
    # Perplexity Rate Limits
    PERPLEXITY_RPM: int = 50  # requests per minute
    PERPLEXITY_BURST: int = 10  # burst capacity
    
    # OpenAI Rate Limits (default tier)
    OPENAI_RPM: int = 500  # requests per minute
    OPENAI_TPM: int = 200000  # tokens per minute
    
    # Claude Rate Limits
    CLAUDE_RPM: int = 1000  # requests per minute
    CLAUDE_TPM: int = 100000  # tokens per minute
    
    # GitHub Rate Limits
    GITHUB_RPH: int = 5000  # requests per hour (authenticated)


class ModelConfiguration(BaseModel):
    """Default model configurations for each provider"""
    
    # Perplexity Models
    PERPLEXITY_DEFAULT_MODEL: str = "sonar"
    PERPLEXITY_RESEARCH_MODEL: str = "sonar-deep-research"
    
    # OpenAI Models
    OPENAI_DEFAULT_MODEL: str = "gpt-4o-mini"
    OPENAI_ADVANCED_MODEL: str = "gpt-4o"
    OPENAI_REASONING_MODEL: str = "o1-mini"
    
    # Claude Models
    CLAUDE_DEFAULT_MODEL: str = "claude-sonnet-4-20250514"
    CLAUDE_ADVANCED_MODEL: str = "claude-opus-4-20250514"
    CLAUDE_FAST_MODEL: str = "claude-3-7-sonnet-20250219"


class AgentAPIMapping(BaseModel):
    """Maps each agent to its preferred API provider and model"""
    
    # Research Agent - Perplexity
    RESEARCH_AGENT_PROVIDER: str = "perplexity"
    RESEARCH_AGENT_MODEL: str = "sonar-deep-research"
    RESEARCH_AGENT_TIMEOUT: int = 300  # 5 minutes
    
    # Code Review Agent - Claude (better for code analysis)
    CODE_REVIEW_PROVIDER: str = "claude"
    CODE_REVIEW_MODEL: str = "claude-sonnet-4-20250514"
    CODE_REVIEW_TIMEOUT: int = 60
    
    # Testing Agent - OpenAI (good for structured output)
    TESTING_AGENT_PROVIDER: str = "openai"
    TESTING_AGENT_MODEL: str = "gpt-4o-mini"
    TESTING_AGENT_TIMEOUT: int = 60
    
    # Documentation Agent - Claude (excellent for documentation)
    DOCUMENTATION_PROVIDER: str = "claude"
    DOCUMENTATION_MODEL: str = "claude-sonnet-4-20250514"
    DOCUMENTATION_TIMEOUT: int = 60
    
    # Debugging Agent - Claude (strong reasoning)
    DEBUGGING_PROVIDER: str = "claude"
    DEBUGGING_MODEL: str = "claude-sonnet-4-20250514"
    DEBUGGING_TIMEOUT: int = 90
    
    # Security Agent - OpenAI (with function calling)
    SECURITY_PROVIDER: str = "openai"
    SECURITY_MODEL: str = "gpt-4o-mini"
    SECURITY_TIMEOUT: int = 90
    
    # Performance Agent - OpenAI
    PERFORMANCE_PROVIDER: str = "openai"
    PERFORMANCE_MODEL: str = "gpt-4o-mini"
    PERFORMANCE_TIMEOUT: int = 60
    
    # Fork Agent - GitHub
    FORK_AGENT_PROVIDER: str = "github"
    FORK_AGENT_TIMEOUT: int = 60


# Global configuration instances
timeouts = APITimeouts()
rate_limits = APIRateLimits()
models = ModelConfiguration()
agent_mapping = AgentAPIMapping()


def get_agent_config(agent_type: str) -> dict:
    """
    Get configuration for a specific agent type
    
    Args:
        agent_type: One of: research, code_review, testing, documentation, 
                    debugging, security, performance, fork
    
    Returns:
        Dictionary with provider, model, and timeout settings
    """
    agent_configs = {
        "research": {
            "provider": agent_mapping.RESEARCH_AGENT_PROVIDER,
            "model": agent_mapping.RESEARCH_AGENT_MODEL,
            "timeout": agent_mapping.RESEARCH_AGENT_TIMEOUT
        },
        "code_review": {
            "provider": agent_mapping.CODE_REVIEW_PROVIDER,
            "model": agent_mapping.CODE_REVIEW_MODEL,
            "timeout": agent_mapping.CODE_REVIEW_TIMEOUT
        },
        "testing": {
            "provider": agent_mapping.TESTING_AGENT_PROVIDER,
            "model": agent_mapping.TESTING_AGENT_MODEL,
            "timeout": agent_mapping.TESTING_AGENT_TIMEOUT
        },
        "documentation": {
            "provider": agent_mapping.DOCUMENTATION_PROVIDER,
            "model": agent_mapping.DOCUMENTATION_MODEL,
            "timeout": agent_mapping.DOCUMENTATION_TIMEOUT
        },
        "debugging": {
            "provider": agent_mapping.DEBUGGING_PROVIDER,
            "model": agent_mapping.DEBUGGING_MODEL,
            "timeout": agent_mapping.DEBUGGING_TIMEOUT
        },
        "security": {
            "provider": agent_mapping.SECURITY_PROVIDER,
            "model": agent_mapping.SECURITY_MODEL,
            "timeout": agent_mapping.SECURITY_TIMEOUT
        },
        "performance": {
            "provider": agent_mapping.PERFORMANCE_PROVIDER,
            "model": agent_mapping.PERFORMANCE_MODEL,
            "timeout": agent_mapping.PERFORMANCE_TIMEOUT
        },
        "fork": {
            "provider": agent_mapping.FORK_AGENT_PROVIDER,
            "model": None,  # GitHub doesn't use LLM models
            "timeout": agent_mapping.FORK_AGENT_TIMEOUT
        }
    }
    
    return agent_configs.get(agent_type, {
        "provider": "openai",
        "model": "gpt-4o-mini",
        "timeout": 60
    })


def get_timeout_for_provider(provider: str, operation: str = "standard") -> int:
    """
    Get timeout for a specific provider and operation type
    
    Args:
        provider: API provider name (perplexity, openai, claude, github)
        operation: Operation type (standard, streaming, deep_research, etc.)
    
    Returns:
        Timeout in seconds
    """
    timeout_map = {
        "perplexity": {
            "standard": timeouts.PERPLEXITY_BASIC_TIMEOUT,
            "deep_research": timeouts.PERPLEXITY_DEEP_RESEARCH_TIMEOUT,
            "connection": timeouts.PERPLEXITY_CONNECTION_TIMEOUT
        },
        "openai": {
            "standard": timeouts.OPENAI_STANDARD_TIMEOUT,
            "streaming": timeouts.OPENAI_STREAMING_TIMEOUT,
            "function_calling": timeouts.OPENAI_FUNCTION_CALLING_TIMEOUT
        },
        "claude": {
            "standard": timeouts.CLAUDE_STANDARD_TIMEOUT,
            "streaming": timeouts.CLAUDE_STREAMING_TIMEOUT,
            "long_context": timeouts.CLAUDE_LONG_CONTEXT_TIMEOUT
        },
        "github": {
            "standard": timeouts.GITHUB_STANDARD_TIMEOUT,
            "search": timeouts.GITHUB_SEARCH_TIMEOUT,
            "clone": timeouts.GITHUB_CLONE_TIMEOUT
        }
    }
    
    provider_timeouts = timeout_map.get(provider, {})
    return provider_timeouts.get(operation, 60)  # default 60 seconds


# Example usage
if __name__ == "__main__":
    print("API Configuration Summary")
    print("=" * 70)
    print()
    
    print("Timeouts Configuration:")
    print(f"  Perplexity Deep Research: {timeouts.PERPLEXITY_DEEP_RESEARCH_TIMEOUT}s (5 minutes)")
    print(f"  Perplexity Basic: {timeouts.PERPLEXITY_BASIC_TIMEOUT}s")
    print(f"  OpenAI Standard: {timeouts.OPENAI_STANDARD_TIMEOUT}s")
    print(f"  Claude Standard: {timeouts.CLAUDE_STANDARD_TIMEOUT}s")
    print(f"  GitHub Standard: {timeouts.GITHUB_STANDARD_TIMEOUT}s")
    print()
    
    print("Agent Configurations:")
    for agent_type in ["research", "code_review", "testing", "documentation", 
                       "debugging", "security", "performance", "fork"]:
        config = get_agent_config(agent_type)
        print(f"  {agent_type.title()}: {config['provider']} / {config['model']} / {config['timeout']}s")
