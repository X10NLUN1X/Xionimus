"""
Enhanced Context Analyzer for Improved Agent Selection
Implements semantic content analysis and better keyword matching
"""

import re
import logging
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from enum import Enum


class TaskDomain(Enum):
    """Task domains for better categorization"""
    CODING = "coding"
    RESEARCH = "research" 
    WRITING = "writing"
    DATA_ANALYSIS = "data_analysis"
    TESTING = "testing"
    FILE_MANAGEMENT = "file_management"
    SESSION_MANAGEMENT = "session_management"
    GITHUB_OPERATIONS = "github_operations"
    GENERAL = "general"


@dataclass
class ContextAnalysis:
    """Results of context analysis"""
    primary_domain: TaskDomain
    secondary_domains: List[TaskDomain]
    confidence_score: float
    semantic_indicators: Dict[str, float]
    content_complexity: float
    requires_specialization: bool
    context_hints: List[str]


class EnhancedContextAnalyzer:
    """
    Enhanced context analyzer that provides better content understanding
    for improved agent selection
    """
    
    def __init__(self):
        self.logger = logging.getLogger("context_analyzer")
        
        # Domain-specific patterns with word boundaries
        self.domain_patterns = {
            TaskDomain.CODING: {
                'exact_keywords': [
                    'function', 'method', 'class', 'variable', 'algorithm',
                    'code', 'programming', 'development', 'implement', 
                    'debug', 'refactor', 'optimize', 'python', 'javascript',
                    'java', 'c++', 'sql', 'api', 'framework'
                ],
                'phrases': [
                    'write code', 'generate code', 'create function', 
                    'fix code', 'code review', 'programming language'
                ],
                'intent_patterns': [
                    r'\b(?:create|write|generate|implement)\s+(?:a\s+)?(?:function|method|class|script|program)',
                    r'\b(?:debug|fix|resolve)\s+(?:this\s+)?(?:code|function|error|bug)',
                    r'\bcalculate\s+(?:the\s+)?(?:fibonacci|factorial|sum|average)'
                ]
            },
            
            TaskDomain.RESEARCH: {
                'exact_keywords': [
                    'research', 'investigate', 'find', 'search', 'analyze',
                    'study', 'explore', 'information', 'data', 'facts',
                    'latest', 'current', 'trends', 'developments', 'news',
                    'market', 'industry', 'compare', 'competitive'
                ],
                'phrases': [
                    'latest developments', 'current trends', 'market research',
                    'find information', 'research about', 'what is'
                ],
                'intent_patterns': [
                    r'\b(?:research|investigate|find)\s+(?:the\s+)?(?:latest|current|recent)',
                    r'\b(?:what|how|why)\s+(?:is|are|do|does)',
                    r'\b(?:compare|contrast|analyze)\s+(?:the\s+)?(?:difference|differences)'
                ]
            },
            
            TaskDomain.WRITING: {
                'exact_keywords': [
                    'write', 'document', 'documentation', 'article', 'essay',
                    'blog', 'content', 'explain', 'describe', 'summarize',
                    'overview', 'guide', 'tutorial', 'manual'
                ],
                'phrases': [
                    'write documentation', 'create article', 'blog post',
                    'content creation', 'write essay', 'explain how'
                ],
                'intent_patterns': [
                    r'\b(?:write|create|draft)\s+(?:an?\s+)?(?:article|essay|blog|post|documentation)',
                    r'\b(?:explain|describe|document)\s+(?:how\s+)?(?:to\s+)?',
                    r'\bcreate\s+(?:a\s+)?(?:guide|tutorial|manual)'
                ]
            },
            
            TaskDomain.DATA_ANALYSIS: {
                'exact_keywords': [
                    'data', 'analyze', 'analysis', 'statistics', 'chart',
                    'visualization', 'csv', 'dataset', 'metrics',
                    'dashboard', 'report', 'insights', 'pandas'
                ],
                'phrases': [
                    'analyze data', 'data analysis', 'create chart',
                    'data visualization', 'analyze dataset'
                ],
                'intent_patterns': [
                    r'\b(?:analyze|examine|process)\s+(?:this\s+)?(?:data|dataset|csv)',
                    r'\bcreate\s+(?:a\s+)?(?:chart|graph|visualization|dashboard)',
                    r'\b(?:statistical|data)\s+analysis'
                ]
            },
            
            TaskDomain.TESTING: {
                'exact_keywords': [
                    'test', 'testing', 'quality', 'assurance', 'validation',
                    'verify', 'check', 'audit', 'inspect', 'evaluate',
                    'bug', 'defect', 'regression', 'automation'
                ],
                'phrases': [
                    'unit test', 'integration test', 'test cases',
                    'quality assurance', 'create test'
                ],
                'intent_patterns': [
                    r'\b(?:create|write|generate)\s+(?:unit\s+)?tests?\b',
                    r'\b(?:test|verify|validate)\s+(?:the\s+)?(?:function|code|application)',
                    r'\bquality\s+assurance\b'
                ],
                # Negative patterns to avoid false matches
                'negative_patterns': [
                    r'\blatest\b',  # "latest" contains "test" but isn't about testing
                    r'\bgreatest\b',
                    r'\bcontest\b'
                ]
            }
        }
    
    def analyze_content(self, message: str, context: Optional[Dict[str, Any]] = None) -> ContextAnalysis:
        """
        Perform comprehensive content analysis
        
        Args:
            message: User input message
            context: Optional context information
            
        Returns:
            ContextAnalysis with detailed insights
        """
        if context is None:
            context = {}
            
        # Normalize message
        message_clean = self._normalize_text(message)
        
        # Calculate domain scores
        domain_scores = self._calculate_domain_scores(message_clean)
        
        # Determine primary and secondary domains
        primary_domain = max(domain_scores, key=domain_scores.get)
        secondary_domains = [
            domain for domain, score in domain_scores.items() 
            if score > 0.3 and domain != primary_domain
        ]
        
        # Calculate overall confidence
        confidence_score = domain_scores[primary_domain]
        
        # Analyze content complexity
        content_complexity = self._analyze_complexity(message_clean, context)
        
        # Extract semantic indicators
        semantic_indicators = self._extract_semantic_indicators(message_clean, context)
        
        # Determine if specialization is needed
        requires_specialization = confidence_score > 0.4 or content_complexity > 0.6
        
        # Generate context hints
        context_hints = self._generate_context_hints(message_clean, domain_scores, context)
        
        return ContextAnalysis(
            primary_domain=primary_domain,
            secondary_domains=secondary_domains,
            confidence_score=confidence_score,
            semantic_indicators=semantic_indicators,
            content_complexity=content_complexity,
            requires_specialization=requires_specialization,
            context_hints=context_hints
        )
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for analysis"""
        # Convert to lowercase, preserve word boundaries
        return text.lower().strip()
    
    def _calculate_domain_scores(self, message: str) -> Dict[TaskDomain, float]:
        """Calculate scores for each domain using enhanced matching"""
        scores = {domain: 0.0 for domain in TaskDomain}
        
        for domain, patterns in self.domain_patterns.items():
            score = 0.0
            
            # Check negative patterns first (for domains like TESTING)
            if 'negative_patterns' in patterns:
                has_negative = any(
                    re.search(pattern, message) 
                    for pattern in patterns['negative_patterns']
                )
                if has_negative:
                    # Check if it's a false positive
                    if not self._has_positive_testing_indicators(message):
                        continue
            
            # Exact keyword matching with word boundaries
            for keyword in patterns.get('exact_keywords', []):
                if re.search(rf'\b{re.escape(keyword)}\b', message):
                    score += 1.0
            
            # Phrase matching
            for phrase in patterns.get('phrases', []):
                if phrase in message:
                    score += 1.5  # Phrases get higher weight
            
            # Intent pattern matching
            for pattern in patterns.get('intent_patterns', []):
                if re.search(pattern, message):
                    score += 2.0  # Intent patterns get highest weight
            
            # Normalize score based on pattern count
            max_possible = len(patterns.get('exact_keywords', [])) + \
                          len(patterns.get('phrases', [])) * 1.5 + \
                          len(patterns.get('intent_patterns', [])) * 2.0
            
            if max_possible > 0:
                scores[domain] = min(1.0, score / max_possible * 3)  # Scale up for sensitivity
        
        return scores
    
    def _has_positive_testing_indicators(self, message: str) -> bool:
        """Check if message has clear testing intent despite negative patterns"""
        positive_indicators = [
            r'\bunit\s+test', r'\btest\s+case', r'\btesting\s+framework',
            r'\btest\s+function', r'\btest\s+method', r'\btest\s+suite'
        ]
        
        return any(re.search(pattern, message) for pattern in positive_indicators)
    
    def _analyze_complexity(self, message: str, context: Dict[str, Any]) -> float:
        """Analyze content complexity"""
        complexity_score = 0.0
        
        # Length-based complexity
        word_count = len(message.split())
        complexity_score += min(word_count / 50, 0.3)
        
        # Technical term density
        technical_terms = [
            'algorithm', 'framework', 'architecture', 'implementation',
            'optimization', 'integration', 'configuration', 'methodology'
        ]
        tech_density = sum(1 for term in technical_terms if term in message) / len(technical_terms)
        complexity_score += tech_density * 0.4
        
        # Multiple requirements indicator
        sentences = len([s for s in re.split(r'[.!?]', message) if s.strip()])
        if sentences > 2:
            complexity_score += 0.2
        
        # Context complexity
        if context:
            context_items = len([v for v in context.values() if v])
            complexity_score += min(context_items / 10, 0.1)
        
        return min(complexity_score, 1.0)
    
    def _extract_semantic_indicators(self, message: str, context: Dict[str, Any]) -> Dict[str, float]:
        """Extract semantic indicators from content"""
        indicators = {}
        
        # Question indicators
        question_words = ['what', 'how', 'why', 'when', 'where', 'who']
        if any(message.startswith(qw) for qw in question_words):
            indicators['is_question'] = 0.8
        if '?' in message:
            indicators['has_question_mark'] = 0.6
        
        # Action indicators
        action_verbs = ['create', 'build', 'implement', 'develop', 'design']
        action_count = sum(1 for verb in action_verbs if verb in message)
        if action_count > 0:
            indicators['requires_action'] = min(action_count / len(action_verbs), 1.0)
        
        # Temporal indicators
        temporal_terms = ['latest', 'current', 'recent', 'new', 'updated']
        temporal_count = sum(1 for term in temporal_terms if term in message)
        if temporal_count > 0:
            indicators['temporal_relevance'] = min(temporal_count / len(temporal_terms), 1.0)
        
        # Specificity indicators
        specific_terms = ['specific', 'detailed', 'comprehensive', 'thorough']
        spec_count = sum(1 for term in specific_terms if term in message)
        if spec_count > 0:
            indicators['requires_detail'] = min(spec_count / len(specific_terms), 1.0)
        
        return indicators
    
    def _generate_context_hints(self, message: str, domain_scores: Dict[TaskDomain, float], 
                               context: Dict[str, Any]) -> List[str]:
        """Generate contextual hints for agent selection"""
        hints = []
        
        # Top domains
        sorted_domains = sorted(domain_scores.items(), key=lambda x: x[1], reverse=True)
        top_domains = [domain.value for domain, score in sorted_domains[:3] if score > 0.2]
        
        if top_domains:
            hints.append(f"Primary domains: {', '.join(top_domains)}")
        
        # Content characteristics
        if len(message.split()) > 20:
            hints.append("Complex request requiring detailed analysis")
        
        if any(re.search(rf'\b{term}\b', message) for term in ['latest', 'current', 'recent']):
            hints.append("Requires up-to-date information")
        
        if re.search(r'\b(?:step\s+by\s+step|detailed|comprehensive)\b', message):
            hints.append("Requires detailed, structured response")
        
        # Context-based hints
        if context.get('conversation_history'):
            hints.append("Has conversation context")
        
        if context.get('file_extension'):
            hints.append(f"File context: {context['file_extension']}")
        
        return hints
    
    def get_agent_recommendations(self, analysis: ContextAnalysis) -> Dict[str, float]:
        """
        Get agent recommendations based on context analysis
        
        Returns:
            Dict mapping agent names to confidence scores
        """
        recommendations = {}
        
        # Domain to agent mapping
        domain_agent_mapping = {
            TaskDomain.CODING: 'Code Agent',
            TaskDomain.RESEARCH: 'Research Agent',
            TaskDomain.WRITING: 'Writing Agent', 
            TaskDomain.DATA_ANALYSIS: 'Data Agent',
            TaskDomain.TESTING: 'QA Agent',
            TaskDomain.FILE_MANAGEMENT: 'File Agent',
            TaskDomain.SESSION_MANAGEMENT: 'Session Agent',
            TaskDomain.GITHUB_OPERATIONS: 'GitHub Agent'
        }
        
        # Primary agent recommendation
        primary_agent = domain_agent_mapping.get(analysis.primary_domain)
        if primary_agent:
            recommendations[primary_agent] = analysis.confidence_score
        
        # Secondary agent recommendations
        for domain in analysis.secondary_domains:
            secondary_agent = domain_agent_mapping.get(domain)
            if secondary_agent and secondary_agent != primary_agent:
                # Secondary agents get reduced confidence
                recommendations[secondary_agent] = analysis.confidence_score * 0.6
        
        # Boost based on semantic indicators
        for agent, confidence in recommendations.items():
            if 'temporal_relevance' in analysis.semantic_indicators and agent == 'Research Agent':
                recommendations[agent] = min(1.0, confidence + 0.2)
            
            if 'requires_action' in analysis.semantic_indicators and agent in ['Code Agent', 'Data Agent']:
                recommendations[agent] = min(1.0, confidence + 0.15)
        
        # Filter out low confidence recommendations
        return {agent: conf for agent, conf in recommendations.items() if conf >= 0.3}