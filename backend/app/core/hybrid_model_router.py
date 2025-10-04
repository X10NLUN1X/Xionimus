"""
Hybrid Model Router - Smart Cost-Quality Optimization
Automatically selects the optimal model based on task complexity
"""
from typing import Dict, Any, Optional, List
from enum import Enum
import logging
import re

logger = logging.getLogger(__name__)

class TaskComplexity(Enum):
    """Task complexity levels"""
    SIMPLE = "simple"      # Use cheap models
    MODERATE = "moderate"  # Use mid-tier models
    COMPLEX = "complex"    # Use premium models

class TaskCategory(Enum):
    """Task categories"""
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    CODE_GENERATION = "code_generation"
    RESEARCH = "research"
    DEBUGGING = "debugging"
    GENERAL_CHAT = "general_chat"

class HybridModelRouter:
    """
    Smart model router that optimizes cost vs quality
    
    Strategy:
    - Documentation: 80% GPT-4o-mini, 20% Claude Sonnet
    - Tests: 40% Claude Haiku, 60% Claude Sonnet
    - Code: Based on complexity
    """
    
    def __init__(self):
        # Model configurations for different complexity levels
        self.model_configs = {
            TaskCategory.DOCUMENTATION: {
                TaskComplexity.SIMPLE: {
                    "provider": "openai",
                    "model": "gpt-4o-mini",
                    "cost_per_1m": 0.38,
                    "quality": 85,
                    "reason": "Simple docs: README, comments, tutorials"
                },
                TaskComplexity.MODERATE: {
                    "provider": "openai",
                    "model": "gpt-4o-mini",
                    "cost_per_1m": 0.38,
                    "quality": 85,
                    "reason": "Standard API docs"
                },
                TaskComplexity.COMPLEX: {
                    "provider": "anthropic",
                    "model": "claude-sonnet-4-5-20250929",
                    "cost_per_1m": 9.00,
                    "quality": 93,
                    "reason": "Complex system architecture, security docs"
                }
            },
            TaskCategory.TESTING: {
                TaskComplexity.SIMPLE: {
                    "provider": "anthropic",
                    "model": "claude-haiku-3.5-20241022",
                    "cost_per_1m": 2.40,
                    "quality": 76,
                    "reason": "Simple CRUD tests, utilities"
                },
                TaskComplexity.MODERATE: {
                    "provider": "anthropic",
                    "model": "claude-haiku-3.5-20241022",
                    "cost_per_1m": 2.40,
                    "quality": 76,
                    "reason": "Standard unit tests"
                },
                TaskComplexity.COMPLEX: {
                    "provider": "anthropic",
                    "model": "claude-sonnet-4-5-20250929",
                    "cost_per_1m": 9.00,
                    "quality": 94,
                    "reason": "Security, payment, integration tests"
                }
            },
            TaskCategory.CODE_GENERATION: {
                TaskComplexity.SIMPLE: {
                    "provider": "openai",
                    "model": "gpt-4o-mini",
                    "cost_per_1m": 0.38,
                    "quality": 82,
                    "reason": "Simple components, utilities"
                },
                TaskComplexity.MODERATE: {
                    "provider": "anthropic",
                    "model": "claude-haiku-3.5-20241022",
                    "cost_per_1m": 2.40,
                    "quality": 80,
                    "reason": "Standard features"
                },
                TaskComplexity.COMPLEX: {
                    "provider": "anthropic",
                    "model": "claude-sonnet-4-5-20250929",
                    "cost_per_1m": 9.00,
                    "quality": 92,
                    "reason": "Complex business logic, architecture"
                }
            },
            TaskCategory.RESEARCH: {
                TaskComplexity.SIMPLE: {
                    "provider": "perplexity",
                    "model": "sonar",
                    "cost_per_1m": 0.20,
                    "quality": 85,
                    "reason": "Quick facts, basic info"
                },
                TaskComplexity.MODERATE: {
                    "provider": "perplexity",
                    "model": "sonar",
                    "cost_per_1m": 0.20,
                    "quality": 85,
                    "reason": "Standard research"
                },
                TaskComplexity.COMPLEX: {
                    "provider": "perplexity",
                    "model": "sonar-pro",
                    "cost_per_1m": 9.00,
                    "quality": 95,
                    "reason": "Deep analysis, multiple sources"
                }
            },
            TaskCategory.DEBUGGING: {
                TaskComplexity.SIMPLE: {
                    "provider": "openai",
                    "model": "gpt-4o-mini",
                    "cost_per_1m": 0.38,
                    "quality": 75,
                    "reason": "Simple syntax errors"
                },
                TaskComplexity.MODERATE: {
                    "provider": "anthropic",
                    "model": "claude-sonnet-4-5-20250929",
                    "cost_per_1m": 9.00,
                    "quality": 90,
                    "reason": "Logic bugs"
                },
                TaskComplexity.COMPLEX: {
                    "provider": "anthropic",
                    "model": "claude-opus-4-1-20250805",
                    "cost_per_1m": 15.00,
                    "quality": 95,
                    "reason": "Critical bugs, security issues"
                }
            },
            TaskCategory.GENERAL_CHAT: {
                TaskComplexity.SIMPLE: {
                    "provider": "openai",
                    "model": "gpt-4o-mini",
                    "cost_per_1m": 0.38,
                    "quality": 85,
                    "reason": "Standard conversations"
                },
                TaskComplexity.MODERATE: {
                    "provider": "openai",
                    "model": "gpt-4o-mini",
                    "cost_per_1m": 0.38,
                    "quality": 85,
                    "reason": "Standard conversations"
                },
                TaskComplexity.COMPLEX: {
                    "provider": "openai",
                    "model": "gpt-4o",
                    "cost_per_1m": 6.25,
                    "quality": 95,
                    "reason": "Complex reasoning needed"
                }
            }
        }
    
    def detect_documentation_complexity(self, prompt: str, context: Optional[Dict] = None) -> TaskComplexity:
        """
        Detect if documentation task is simple or complex
        
        SIMPLE (80% of cases):
        - README, getting started
        - Code comments
        - Simple tutorials
        - FAQ
        
        COMPLEX (20% of cases):
        - API reference documentation
        - System architecture docs
        - Security guidelines
        - Integration guides
        """
        prompt_lower = prompt.lower()
        
        # Complex documentation indicators
        complex_indicators = [
            "architecture", "system design", "security",
            "api reference", "api documentation", "openapi",
            "swagger", "integration guide", "deployment guide",
            "production", "scalability", "performance optimization",
            "microservice", "distributed system", "infrastructure"
        ]
        
        # Simple documentation indicators
        simple_indicators = [
            "readme", "getting started", "tutorial", "comment",
            "faq", "how to", "quick start", "example",
            "basic", "simple", "introduction"
        ]
        
        complex_count = sum(1 for indicator in complex_indicators if indicator in prompt_lower)
        simple_count = sum(1 for indicator in simple_indicators if indicator in prompt_lower)
        
        if complex_count >= 2 or (complex_count > 0 and simple_count == 0):
            logger.info(f"📊 Documentation: COMPLEX (Sonnet) - {complex_count} complex indicators")
            return TaskComplexity.COMPLEX
        
        logger.info(f"📊 Documentation: SIMPLE (GPT-4o-mini) - {simple_count} simple indicators")
        return TaskComplexity.SIMPLE
    
    def detect_testing_complexity(self, prompt: str, context: Optional[Dict] = None) -> TaskComplexity:
        """
        Detect if testing task is simple or complex
        
        SIMPLE (40% of cases):
        - Basic CRUD tests
        - Simple utility tests
        - Frontend component tests
        - Validation tests
        
        COMPLEX (60% of cases):
        - Security-critical tests (auth, payment)
        - Integration tests
        - Complex business logic tests
        - Performance tests
        """
        prompt_lower = prompt.lower()
        
        # Critical/Complex test indicators
        complex_indicators = [
            # Security & Payment
            "authentication", "auth", "login", "password", "token",
            "payment", "transaction", "stripe", "paypal",
            "security", "encryption", "authorization", "permission",
            # Complex types
            "integration test", "e2e", "end-to-end",
            "performance test", "load test", "stress test",
            "security test", "penetration test",
            # Business logic
            "business logic", "workflow", "state machine",
            "complex", "critical", "core logic"
        ]
        
        # Simple test indicators
        simple_indicators = [
            "crud", "create", "read", "update", "delete",
            "utility", "helper", "format", "validate",
            "simple", "basic", "component test",
            "frontend test", "ui test"
        ]
        
        # Check for function/file being tested
        if context and "function_name" in context:
            func_name = context["function_name"].lower()
            # Critical function names
            if any(word in func_name for word in ["auth", "login", "payment", "security", "admin"]):
                logger.info(f"🧪 Testing: COMPLEX (Sonnet) - Critical function: {func_name}")
                return TaskComplexity.COMPLEX
        
        complex_count = sum(1 for indicator in complex_indicators if indicator in prompt_lower)
        simple_count = sum(1 for indicator in simple_indicators if indicator in prompt_lower)
        
        # Default to complex if unsure (tests are critical)
        if complex_count > 0 or simple_count == 0:
            logger.info(f"🧪 Testing: COMPLEX (Sonnet) - {complex_count} complex indicators")
            return TaskComplexity.COMPLEX
        
        logger.info(f"🧪 Testing: SIMPLE (Haiku) - {simple_count} simple indicators")
        return TaskComplexity.SIMPLE
    
    def detect_code_complexity(self, prompt: str, context: Optional[Dict] = None) -> TaskComplexity:
        """
        Detect code generation complexity
        """
        prompt_lower = prompt.lower()
        
        # Count complexity indicators
        complexity_score = 0
        
        # Complex patterns
        if any(word in prompt_lower for word in [
            "architecture", "microservice", "distributed", "scalable",
            "security", "authentication", "payment", "optimization"
        ]):
            complexity_score += 3
        
        # Moderate patterns
        if any(word in prompt_lower for word in [
            "api", "database", "backend", "integration",
            "async", "websocket", "real-time"
        ]):
            complexity_score += 2
        
        # Simple patterns
        if any(word in prompt_lower for word in [
            "simple", "basic", "button", "component",
            "utility", "helper", "format"
        ]):
            complexity_score += 0
        
        # Check prompt length (longer = usually more complex)
        if len(prompt) > 500:
            complexity_score += 1
        
        if complexity_score >= 4:
            return TaskComplexity.COMPLEX
        elif complexity_score >= 2:
            return TaskComplexity.MODERATE
        else:
            return TaskComplexity.SIMPLE
    
    def detect_research_complexity(self, prompt: str, context: Optional[Dict] = None) -> TaskComplexity:
        """
        Detect research complexity
        
        SIMPLE (80% of cases):
        - "What is X?"
        - "How to use X?"
        - Basic questions
        - Simple comparisons
        
        COMPLEX (20% of cases):
        - "Compare X vs Y vs Z with performance metrics"
        - "Deep analysis of..."
        - "Security implications of..."
        - "Production-ready patterns for..."
        """
        prompt_lower = prompt.lower()
        
        # Complex research indicators
        complex_indicators = [
            # Deep analysis
            "deep analysis", "comprehensive", "in-depth", "detailed analysis",
            "compare", "comparison", "benchmark", "performance",
            "vs", "versus", "unterschied", "vergleich",
            # Production/Security
            "production", "production-ready", "scalability", "scale",
            "security", "vulnerabilities", "best practices",
            "optimization", "optimize", "performance tuning",
            # Multiple aspects
            "pros and cons", "advantages disadvantages",
            "trade-offs", "architecture", "system design",
            # Advanced topics
            "migration", "integration", "deployment strategy"
        ]
        
        # Simple research indicators
        simple_indicators = [
            "what is", "was ist", "how to", "wie",
            "explain", "erkläre", "overview", "überblick",
            "introduction", "einführung", "basics", "grundlagen",
            "simple", "einfach", "quick", "schnell",
            "tutorial", "getting started", "beispiel", "example"
        ]
        
        complex_count = sum(1 for indicator in complex_indicators if indicator in prompt_lower)
        simple_count = sum(1 for indicator in simple_indicators if indicator in prompt_lower)
        
        # Check for multiple technologies (complex research)
        # Count mentions of different technologies
        tech_keywords = ["react", "vue", "angular", "python", "java", "node", "django", "flask", 
                        "mongodb", "postgresql", "mysql", "redis", "docker", "kubernetes"]
        tech_count = sum(1 for tech in tech_keywords if tech in prompt_lower)
        
        # Length check
        word_count = len(prompt.split())
        
        # Scoring
        complexity_score = 0
        complexity_score += complex_count * 2
        complexity_score -= simple_count * 1
        
        if tech_count >= 3:  # Comparing multiple technologies
            complexity_score += 3
        
        if word_count > 100:  # Long, detailed question
            complexity_score += 2
        
        if complexity_score >= 5:
            logger.info(f"🔍 Research: COMPLEX (Sonar Pro) - Score: {complexity_score}")
            return TaskComplexity.COMPLEX
        elif complexity_score >= 2:
            logger.info(f"🔍 Research: MODERATE (Sonar) - Score: {complexity_score}")
            return TaskComplexity.MODERATE
        else:
            logger.info(f"🔍 Research: SIMPLE (Sonar) - Score: {complexity_score}")
            return TaskComplexity.SIMPLE
    
    def route_model(
        self, 
        task_category: TaskCategory, 
        prompt: str,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Main routing function - returns optimal model based on task and complexity
        
        Returns:
            {
                "provider": "openai",
                "model": "gpt-4o-mini",
                "cost_per_1m": 0.38,
                "quality": 85,
                "reason": "Simple documentation task",
                "complexity": "simple"
            }
        """
        # Detect complexity based on task category
        if task_category == TaskCategory.DOCUMENTATION:
            complexity = self.detect_documentation_complexity(prompt, context)
        elif task_category == TaskCategory.TESTING:
            complexity = self.detect_testing_complexity(prompt, context)
        elif task_category == TaskCategory.CODE_GENERATION:
            complexity = self.detect_code_complexity(prompt, context)
        else:
            # For other categories, default to moderate
            complexity = TaskComplexity.MODERATE
        
        # Get model configuration
        config = self.model_configs.get(task_category, {}).get(
            complexity,
            self.model_configs[TaskCategory.GENERAL_CHAT][TaskComplexity.SIMPLE]
        )
        
        result = {
            **config,
            "complexity": complexity.value,
            "task_category": task_category.value
        }
        
        logger.info(
            f"🎯 Hybrid Router: {task_category.value} → "
            f"{complexity.value} → {result['model']} "
            f"(${result['cost_per_1m']}/1M, {result['quality']}% quality)"
        )
        
        return result
    
    def get_model_for_documentation(self, prompt: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Convenience method for documentation tasks"""
        return self.route_model(TaskCategory.DOCUMENTATION, prompt, context)
    
    def get_model_for_testing(self, prompt: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Convenience method for testing tasks"""
        return self.route_model(TaskCategory.TESTING, prompt, context)
    
    def get_model_for_code(self, prompt: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Convenience method for code generation"""
        return self.route_model(TaskCategory.CODE_GENERATION, prompt, context)
    
    def get_model_for_research(self, prompt: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Convenience method for research tasks"""
        return self.route_model(TaskCategory.RESEARCH, prompt, context)
    
    def get_cost_savings_report(self) -> Dict[str, Any]:
        """Generate a report showing cost savings from hybrid routing"""
        return {
            "documentation": {
                "simple_model": "gpt-4o-mini ($0.38/1M)",
                "complex_model": "claude-sonnet ($9.00/1M)",
                "distribution": "80% simple, 20% complex",
                "avg_cost": "$2.10/1M",
                "savings_vs_all_premium": "77%"
            },
            "testing": {
                "simple_model": "claude-haiku ($2.40/1M)",
                "complex_model": "claude-sonnet ($9.00/1M)",
                "distribution": "40% simple, 60% complex",
                "avg_cost": "$6.36/1M",
                "savings_vs_all_premium": "29%"
            },
            "overall": {
                "avg_cost": "$4.23/1M",
                "savings_vs_premium": "53%",
                "quality_loss": "~8%"
            }
        }
