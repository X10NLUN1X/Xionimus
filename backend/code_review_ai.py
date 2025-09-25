#!/usr/bin/env python3
"""
Code Review AI Service for XIONIMUS AI v2.1
Intelligent code review with improvement suggestions
"""

import logging
import re
import ast
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timezone
from dataclasses import dataclass
from enum import Enum

@dataclass
class CodeIssue:
    """Represents a code issue found during review"""
    id: str
    severity: str  # 'critical', 'major', 'minor', 'info'
    category: str  # 'security', 'performance', 'maintainability', 'style', 'bug'
    title: str
    description: str
    file_path: Optional[str]
    line_number: Optional[int]
    column: Optional[int]
    suggestion: str
    example_fix: Optional[str] = None
    confidence: float = 1.0  # 0.0 to 1.0

@dataclass
class CodeMetrics:
    """Code quality metrics"""
    complexity: int
    maintainability_index: float
    lines_of_code: int
    code_duplication: float
    test_coverage: float
    security_score: float
    performance_score: float
    documentation_coverage: float

@dataclass
class CodeReviewResult:
    """Complete code review result"""
    overall_score: float  # 0-100
    grade: str  # A+, A, B+, B, C+, C, D, F
    issues: List[CodeIssue]
    metrics: CodeMetrics
    suggestions: List[str]
    positive_aspects: List[str]
    generated_at: datetime
    review_summary: str

class CodeReviewAI:
    """
    AI-powered code review service that analyzes code quality,
    identifies issues, and provides improvement suggestions
    """
    
    def __init__(self, ai_client=None):
        self.ai_client = ai_client
        self.logger = logging.getLogger("code_review_ai")
        self.issue_patterns = self._load_issue_patterns()
        self.language_rules = self._load_language_rules()
        self.logger.info("📝 Code Review AI Service initialized")
    
    async def review_code(self, 
                         code: str, 
                         language: str,
                         file_path: Optional[str] = None,
                         context: Optional[Dict[str, Any]] = None) -> CodeReviewResult:
        """
        Perform comprehensive code review
        
        Args:
            code: Source code to review
            language: Programming language
            file_path: Path to the file (optional)
            context: Additional context (project info, etc.)
            
        Returns:
            CodeReviewResult with complete analysis
        """
        try:
            self.logger.info(f"📝 Starting code review for {language} code")
            
            # Analyze code structure and metrics
            metrics = await self._analyze_code_metrics(code, language)
            
            # Find issues using pattern matching
            pattern_issues = await self._find_pattern_issues(code, language, file_path)
            
            # Find issues using AI analysis (if available)
            ai_issues = await self._find_ai_issues(code, language, context)
            
            # Combine and deduplicate issues
            all_issues = self._combine_and_deduplicate_issues(pattern_issues + ai_issues)
            
            # Calculate overall score
            overall_score = self._calculate_overall_score(metrics, all_issues)
            grade = self._score_to_grade(overall_score)
            
            # Generate suggestions
            suggestions = await self._generate_suggestions(code, language, all_issues, metrics)
            
            # Identify positive aspects
            positive_aspects = self._identify_positive_aspects(code, language, metrics)
            
            # Generate review summary
            review_summary = await self._generate_review_summary(
                overall_score, metrics, all_issues, suggestions
            )
            
            result = CodeReviewResult(
                overall_score=overall_score,
                grade=grade,
                issues=all_issues,
                metrics=metrics,
                suggestions=suggestions,
                positive_aspects=positive_aspects,
                generated_at=datetime.now(timezone.utc),
                review_summary=review_summary
            )
            
            self.logger.info(f"✅ Code review completed - Score: {overall_score:.1f} ({grade})")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Code review error: {str(e)}")
            # Return minimal result on error
            return CodeReviewResult(
                overall_score=0.0,
                grade="F",
                issues=[],
                metrics=CodeMetrics(0, 0.0, 0, 0.0, 0.0, 0.0, 0.0, 0.0),
                suggestions=[],
                positive_aspects=[],
                generated_at=datetime.now(timezone.utc),
                review_summary="Code review failed due to an error."
            )
    
    async def _analyze_code_metrics(self, code: str, language: str) -> CodeMetrics:
        """Analyze code metrics"""
        metrics = CodeMetrics(
            complexity=0,
            maintainability_index=0.0,
            lines_of_code=len(code.splitlines()),
            code_duplication=0.0,
            test_coverage=0.0,
            security_score=70.0,  # Default neutral score
            performance_score=70.0,
            documentation_coverage=0.0
        )
        
        try:
            if language.lower() == 'python':
                metrics = await self._analyze_python_metrics(code)
            elif language.lower() in ['javascript', 'typescript']:
                metrics = await self._analyze_javascript_metrics(code)
            else:
                metrics = await self._analyze_generic_metrics(code)
                
        except Exception as e:
            self.logger.error(f"❌ Metrics analysis error: {str(e)}")
        
        return metrics
    
    async def _analyze_python_metrics(self, code: str) -> CodeMetrics:
        """Analyze Python-specific metrics"""
        lines = code.splitlines()
        loc = len([line for line in lines if line.strip() and not line.strip().startswith('#')])
        
        complexity = 1  # Base complexity
        doc_lines = 0
        
        try:
            tree = ast.parse(code)
            
            # Calculate cyclomatic complexity
            for node in ast.walk(tree):
                if isinstance(node, (ast.If, ast.While, ast.For, ast.Try, ast.With)):
                    complexity += 1
                elif isinstance(node, ast.BoolOp):
                    complexity += len(node.values) - 1
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if ast.get_docstring(node):
                        doc_lines += len(ast.get_docstring(node).split('\n'))
                elif isinstance(node, ast.ClassDef):
                    if ast.get_docstring(node):
                        doc_lines += len(ast.get_docstring(node).split('\n'))
            
            # Documentation coverage
            doc_coverage = (doc_lines / loc * 100) if loc > 0 else 0
            
            # Maintainability index (simplified)
            maintainability = max(0, 100 - complexity * 2)
            
            # Code duplication (simplified check for repeated patterns)
            duplication = self._calculate_duplication(code)
            
            return CodeMetrics(
                complexity=complexity,
                maintainability_index=maintainability,
                lines_of_code=loc,
                code_duplication=duplication,
                test_coverage=0.0,  # Would need separate analysis
                security_score=self._calculate_security_score(code, 'python'),
                performance_score=self._calculate_performance_score(code, 'python'),
                documentation_coverage=min(doc_coverage, 100.0)
            )
            
        except Exception as e:
            self.logger.error(f"❌ Python metrics error: {str(e)}")
            return CodeMetrics(0, 0.0, loc, 0.0, 0.0, 70.0, 70.0, 0.0)
    
    async def _analyze_javascript_metrics(self, code: str) -> CodeMetrics:
        """Analyze JavaScript/TypeScript metrics"""
        lines = code.splitlines()
        loc = len([line for line in lines if line.strip() and not line.strip().startswith('//')])
        
        # Simple complexity calculation for JavaScript
        complexity_patterns = [r'\bif\b', r'\bwhile\b', r'\bfor\b', r'\bswitch\b', r'\bcatch\b', r'\?\s*\w+\s*:']
        complexity = 1
        for pattern in complexity_patterns:
            complexity += len(re.findall(pattern, code))
        
        # Documentation (comments)
        comment_lines = len([line for line in lines if line.strip().startswith('//') or line.strip().startswith('/*')])
        doc_coverage = (comment_lines / loc * 100) if loc > 0 else 0
        
        maintainability = max(0, 100 - complexity * 1.5)
        duplication = self._calculate_duplication(code)
        
        return CodeMetrics(
            complexity=complexity,
            maintainability_index=maintainability,
            lines_of_code=loc,
            code_duplication=duplication,
            test_coverage=0.0,
            security_score=self._calculate_security_score(code, 'javascript'),
            performance_score=self._calculate_performance_score(code, 'javascript'),
            documentation_coverage=min(doc_coverage, 100.0)
        )
    
    async def _analyze_generic_metrics(self, code: str) -> CodeMetrics:
        """Generic metrics for unsupported languages"""
        lines = code.splitlines()
        loc = len([line for line in lines if line.strip()])
        
        # Basic complexity estimation
        complexity = max(1, loc // 20)  # Rough estimate
        maintainability = max(0, 100 - complexity)
        
        return CodeMetrics(
            complexity=complexity,
            maintainability_index=maintainability,
            lines_of_code=loc,
            code_duplication=0.0,
            test_coverage=0.0,
            security_score=70.0,
            performance_score=70.0,
            documentation_coverage=0.0
        )
    
    def _calculate_duplication(self, code: str) -> float:
        """Calculate code duplication percentage"""
        lines = [line.strip() for line in code.splitlines() if line.strip()]
        if len(lines) < 4:
            return 0.0
        
        duplicates = 0
        for i in range(len(lines) - 3):
            chunk = ' '.join(lines[i:i+4])
            for j in range(i + 4, len(lines) - 3):
                other_chunk = ' '.join(lines[j:j+4])
                if chunk == other_chunk and len(chunk) > 20:
                    duplicates += 1
                    break
        
        return min((duplicates / len(lines)) * 100, 100.0)
    
    def _calculate_security_score(self, code: str, language: str) -> float:
        """Calculate security score based on common vulnerabilities"""
        score = 100.0
        
        security_issues = {
            'python': [
                (r'eval\s*\(', 20, 'Use of eval() can be dangerous'),
                (r'exec\s*\(', 20, 'Use of exec() can be dangerous'),
                (r'import\s+os.*system', 15, 'Direct system calls can be risky'),
                (r'subprocess\.call\s*\(', 10, 'Subprocess calls need validation'),
                (r'pickle\.loads?\s*\(', 15, 'Pickle can execute arbitrary code'),
                (r'input\s*\(', 5, 'User input needs validation'),
            ],
            'javascript': [
                (r'eval\s*\(', 20, 'Use of eval() is dangerous'),
                (r'innerHTML\s*=', 10, 'innerHTML can cause XSS'),
                (r'document\.write\s*\(', 15, 'document.write can be unsafe'),
                (r'setTimeout\s*\(\s*["\']', 10, 'String-based setTimeout is risky'),
                (r'localStorage\.', 5, 'LocalStorage needs validation'),
            ]
        }
        
        patterns = security_issues.get(language.lower(), [])
        for pattern, penalty, _ in patterns:
            if re.search(pattern, code):
                score -= penalty
        
        return max(0.0, score)
    
    def _calculate_performance_score(self, code: str, language: str) -> float:
        """Calculate performance score"""
        score = 100.0
        
        performance_issues = {
            'python': [
                (r'for\s+\w+\s+in\s+range\s*\(\s*len\s*\(', 10, 'Use enumerate instead of range(len())'),
                (r'\.append\s*\([^)]+\)\s*for', 5, 'Consider list comprehension'),
                (r'global\s+\w+', 5, 'Global variables can impact performance'),
            ],
            'javascript': [
                (r'document\.getElementById', 5, 'Consider caching DOM queries'),
                (r'innerHTML\s*\+=', 10, 'Use DocumentFragment for multiple DOM updates'),
                (r'for\s*\(\s*var\s+\w+\s*=\s*0', 5, 'Consider forEach or modern loops'),
            ]
        }
        
        patterns = performance_issues.get(language.lower(), [])
        for pattern, penalty, _ in patterns:
            matches = len(re.findall(pattern, code))
            score -= penalty * matches
        
        return max(0.0, score)
    
    async def _find_pattern_issues(self, code: str, language: str, file_path: Optional[str]) -> List[CodeIssue]:
        """Find issues using pattern matching"""
        issues = []
        
        # Load patterns for the language
        patterns = self.issue_patterns.get(language.lower(), [])
        
        lines = code.splitlines()
        for line_num, line in enumerate(lines, 1):
            for pattern_info in patterns:
                if re.search(pattern_info['pattern'], line):
                    issue = CodeIssue(
                        id=f"pattern_{line_num}_{hash(pattern_info['pattern']) % 1000}",
                        severity=pattern_info['severity'],
                        category=pattern_info['category'],
                        title=pattern_info['title'],
                        description=pattern_info['description'],
                        file_path=file_path,
                        line_number=line_num,
                        column=line.find(re.search(pattern_info['pattern'], line).group()) if re.search(pattern_info['pattern'], line) else 0,
                        suggestion=pattern_info['suggestion'],
                        example_fix=pattern_info.get('example_fix'),
                        confidence=pattern_info.get('confidence', 0.8)
                    )
                    issues.append(issue)
        
        return issues
    
    async def _find_ai_issues(self, code: str, language: str, context: Optional[Dict[str, Any]]) -> List[CodeIssue]:
        """Find issues using AI analysis"""
        if not self.ai_client:
            return []
        
        try:
            # This would call AI service for deeper analysis
            # For now, return empty list
            return []
        except Exception as e:
            self.logger.error(f"❌ AI issue detection error: {str(e)}")
            return []
    
    def _combine_and_deduplicate_issues(self, issues: List[CodeIssue]) -> List[CodeIssue]:
        """Combine and deduplicate similar issues"""
        if not issues:
            return []
        
        # Simple deduplication based on line number and category
        seen = set()
        deduplicated = []
        
        for issue in issues:
            key = (issue.line_number, issue.category, issue.title[:50])
            if key not in seen:
                seen.add(key)
                deduplicated.append(issue)
        
        # Sort by severity and line number
        severity_order = {'critical': 0, 'major': 1, 'minor': 2, 'info': 3}
        deduplicated.sort(key=lambda x: (severity_order.get(x.severity, 4), x.line_number or 0))
        
        return deduplicated
    
    def _calculate_overall_score(self, metrics: CodeMetrics, issues: List[CodeIssue]) -> float:
        """Calculate overall code quality score"""
        base_score = metrics.maintainability_index
        
        # Deduct points for issues
        for issue in issues:
            if issue.severity == 'critical':
                base_score -= 15
            elif issue.severity == 'major':
                base_score -= 10
            elif issue.severity == 'minor':
                base_score -= 5
            elif issue.severity == 'info':
                base_score -= 2
        
        # Bonus points for good practices
        if metrics.documentation_coverage > 50:
            base_score += 5
        if metrics.security_score > 80:
            base_score += 5
        if metrics.performance_score > 80:
            base_score += 5
        
        return max(0.0, min(100.0, base_score))
    
    def _score_to_grade(self, score: float) -> str:
        """Convert numeric score to letter grade"""
        if score >= 95:
            return "A+"
        elif score >= 90:
            return "A"
        elif score >= 85:
            return "B+"
        elif score >= 80:
            return "B"
        elif score >= 75:
            return "C+"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    async def _generate_suggestions(self, code: str, language: str, issues: List[CodeIssue], metrics: CodeMetrics) -> List[str]:
        """Generate improvement suggestions"""
        suggestions = []
        
        # Priority suggestions based on issues
        critical_issues = [i for i in issues if i.severity == 'critical']
        if critical_issues:
            suggestions.append("🚨 Address critical security and reliability issues first")
        
        major_issues = [i for i in issues if i.severity == 'major']
        if major_issues:
            suggestions.append("⚠️ Fix major code quality issues to improve maintainability")
        
        # Metric-based suggestions
        if metrics.complexity > 20:
            suggestions.append("🔄 Consider refactoring complex functions into smaller, more focused units")
        
        if metrics.documentation_coverage < 30:
            suggestions.append("📚 Add more documentation and comments to improve code readability")
        
        if metrics.code_duplication > 20:
            suggestions.append("🔄 Reduce code duplication by extracting common functionality")
        
        if metrics.security_score < 70:
            suggestions.append("🔒 Review and improve security practices")
        
        if metrics.performance_score < 70:
            suggestions.append("⚡ Optimize performance bottlenecks identified in the analysis")
        
        # Language-specific suggestions
        if language.lower() == 'python':
            if re.search(r'print\s*\(', code):
                suggestions.append("🐍 Replace print statements with proper logging")
            if re.search(r'except:\s*$', code):
                suggestions.append("🐍 Avoid bare except clauses, catch specific exceptions")
        
        elif language.lower() == 'javascript':
            if re.search(r'var\s+', code):
                suggestions.append("📜 Consider using 'let' or 'const' instead of 'var'")
            if re.search(r'==', code):
                suggestions.append("📜 Use strict equality (===) instead of loose equality (==)")
        
        return suggestions[:10]  # Limit to top 10 suggestions
    
    def _identify_positive_aspects(self, code: str, language: str, metrics: CodeMetrics) -> List[str]:
        """Identify positive aspects of the code"""
        positives = []
        
        if metrics.documentation_coverage > 70:
            positives.append("📚 Excellent documentation coverage")
        
        if metrics.security_score > 85:
            positives.append("🔒 Good security practices implemented")
        
        if metrics.performance_score > 85:
            positives.append("⚡ Performance-conscious code design")
        
        if metrics.complexity < 10:
            positives.append("✨ Clean and simple code structure")
        
        if metrics.code_duplication < 10:
            positives.append("🎯 Good adherence to DRY principles")
        
        # Language-specific positives
        if language.lower() == 'python':
            if re.search(r'"""[^"]*"""', code):
                positives.append("🐍 Good use of docstrings")
            if re.search(r'with\s+open', code):
                positives.append("🐍 Proper use of context managers")
        
        elif language.lower() == 'javascript':
            if re.search(r'const\s+', code) and not re.search(r'var\s+', code):
                positives.append("📜 Modern JavaScript practices")
            if re.search(r'===', code):
                positives.append("📜 Proper use of strict equality")
        
        return positives
    
    async def _generate_review_summary(self, score: float, metrics: CodeMetrics, issues: List[CodeIssue], suggestions: List[str]) -> str:
        """Generate a summary of the code review"""
        grade = self._score_to_grade(score)
        
        critical_count = len([i for i in issues if i.severity == 'critical'])
        major_count = len([i for i in issues if i.severity == 'major'])
        minor_count = len([i for i in issues if i.severity == 'minor'])
        
        summary = f"## Code Review Summary\n\n"
        summary += f"**Overall Score:** {score:.1f}/100 ({grade})\n\n"
        
        if score >= 85:
            summary += "✅ **Excellent code quality!** This code demonstrates strong development practices.\n\n"
        elif score >= 70:
            summary += "👍 **Good code quality** with room for minor improvements.\n\n"
        elif score >= 50:
            summary += "⚠️ **Moderate code quality** - several areas need attention.\n\n"
        else:
            summary += "🚨 **Code needs significant improvement** before production use.\n\n"
        
        summary += f"**Issues Found:**\n"
        summary += f"- Critical: {critical_count}\n"
        summary += f"- Major: {major_count}\n"
        summary += f"- Minor: {minor_count}\n\n"
        
        summary += f"**Code Metrics:**\n"
        summary += f"- Complexity: {metrics.complexity}\n"
        summary += f"- Lines of Code: {metrics.lines_of_code}\n"
        summary += f"- Documentation: {metrics.documentation_coverage:.1f}%\n"
        summary += f"- Security Score: {metrics.security_score:.1f}/100\n\n"
        
        if suggestions:
            summary += f"**Top Priority Actions:**\n"
            for i, suggestion in enumerate(suggestions[:5], 1):
                summary += f"{i}. {suggestion}\n"
        
        return summary
    
    def _load_issue_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load issue detection patterns for different languages"""
        return {
            'python': [
                {
                    'pattern': r'eval\s*\(',
                    'severity': 'critical',
                    'category': 'security',
                    'title': 'Use of eval() function',
                    'description': 'eval() can execute arbitrary code and is a security risk',
                    'suggestion': 'Use safer alternatives like literal_eval() or avoid dynamic code execution',
                    'confidence': 0.95
                },
                {
                    'pattern': r'except:\s*$',
                    'severity': 'major',
                    'category': 'bug',
                    'title': 'Bare except clause',
                    'description': 'Catching all exceptions can hide important errors',
                    'suggestion': 'Catch specific exception types instead',
                    'example_fix': 'except ValueError as e:',
                    'confidence': 0.9
                },
                {
                    'pattern': r'print\s*\(',
                    'severity': 'minor',
                    'category': 'maintainability',
                    'title': 'Use of print statement',
                    'description': 'Print statements should be replaced with proper logging',
                    'suggestion': 'Use logging module instead of print',
                    'example_fix': 'logging.info("message")',
                    'confidence': 0.8
                },
                {
                    'pattern': r'TODO|FIXME|HACK',
                    'severity': 'minor',
                    'category': 'maintainability',
                    'title': 'TODO/FIXME comment found',
                    'description': 'Unresolved TODO or FIXME comments',
                    'suggestion': 'Address the TODO item or create a ticket to track it',
                    'confidence': 0.7
                }
            ],
            'javascript': [
                {
                    'pattern': r'eval\s*\(',
                    'severity': 'critical',
                    'category': 'security',
                    'title': 'Use of eval() function',
                    'description': 'eval() can execute arbitrary code and is a security risk',
                    'suggestion': 'Use safer alternatives or avoid dynamic code execution',
                    'confidence': 0.95
                },
                {
                    'pattern': r'innerHTML\s*=',
                    'severity': 'major',
                    'category': 'security',
                    'title': 'Use of innerHTML',
                    'description': 'innerHTML can lead to XSS vulnerabilities',
                    'suggestion': 'Use textContent or properly sanitize the content',
                    'confidence': 0.8
                },
                {
                    'pattern': r'var\s+',
                    'severity': 'minor',
                    'category': 'style',
                    'title': 'Use of var keyword',
                    'description': 'var has function scope and can cause confusion',
                    'suggestion': 'Use let or const instead of var',
                    'example_fix': 'let variableName = value;',
                    'confidence': 0.7
                },
                {
                    'pattern': r'==(?!=)',
                    'severity': 'minor',
                    'category': 'bug',
                    'title': 'Use of loose equality',
                    'description': 'Loose equality can cause unexpected type coercion',
                    'suggestion': 'Use strict equality (===) instead',
                    'example_fix': 'if (a === b)',
                    'confidence': 0.8
                }
            ]
        }
    
    def _load_language_rules(self) -> Dict[str, Dict[str, Any]]:
        """Load language-specific rules and best practices"""
        return {
            'python': {
                'naming_conventions': {
                    'function': r'^[a-z][a-z0-9_]*$',
                    'class': r'^[A-Z][a-zA-Z0-9]*$',
                    'constant': r'^[A-Z][A-Z0-9_]*$'
                },
                'max_line_length': 88,
                'max_function_length': 50,
                'max_class_length': 300
            },
            'javascript': {
                'naming_conventions': {
                    'function': r'^[a-z][a-zA-Z0-9]*$',
                    'class': r'^[A-Z][a-zA-Z0-9]*$',
                    'constant': r'^[A-Z][A-Z0-9_]*$'
                },
                'max_line_length': 100,
                'max_function_length': 40,
                'max_class_length': 250
            }
        }