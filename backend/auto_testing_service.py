#!/usr/bin/env python3
"""
Auto-Testing Service for XIONIMUS AI v2.1
Automatic test generation and execution capabilities
"""

import logging
import asyncio
import ast
import re
import tempfile
import subprocess
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timezone
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import os

@dataclass
class TestResult:
    """Represents a test execution result"""
    test_name: str
    status: str  # 'passed', 'failed', 'skipped', 'error'
    execution_time: float
    output: str
    error_message: Optional[str] = None
    coverage: Optional[float] = None

@dataclass
class TestSuite:
    """Represents a generated test suite"""
    name: str
    language: str
    framework: str
    test_cases: List[Dict[str, Any]]
    setup_code: str
    teardown_code: str
    dependencies: List[str]

class TestFramework(Enum):
    """Supported testing frameworks"""
    PYTEST = "pytest"
    UNITTEST = "unittest"
    JEST = "jest"
    JUNIT = "junit"
    MOCHA = "mocha"
    RSPEC = "rspec"

class AutoTestingService:
    """
    Automatic test generation and execution service
    """
    
    def __init__(self, ai_client=None):
        self.ai_client = ai_client
        self.logger = logging.getLogger("auto_testing_service")
        self.supported_languages = {
            'python': ['pytest', 'unittest'],
            'javascript': ['jest', 'mocha'],
            'typescript': ['jest', 'mocha'],
            'java': ['junit'],
            'ruby': ['rspec'],
            'go': ['testing'],
            'rust': ['cargo-test'],
            'csharp': ['nunit', 'xunit']
        }
        self.logger.info("🤖 Auto-Testing Service initialized")
    
    async def generate_tests(self, 
                           code: str, 
                           language: str,
                           framework: Optional[str] = None,
                           test_types: List[str] = None,
                           coverage_target: float = 80.0) -> TestSuite:
        """
        Generate comprehensive test suite for given code
        
        Args:
            code: Source code to generate tests for
            language: Programming language (python, javascript, etc.)
            framework: Testing framework preference
            test_types: Types of tests to generate (unit, integration, e2e)
            coverage_target: Desired code coverage percentage
            
        Returns:
            TestSuite object with generated tests
        """
        try:
            self.logger.info(f"🧪 Generating tests for {language} code")
            
            # Auto-detect framework if not specified
            if not framework:
                framework = self._detect_best_framework(language)
            
            # Default test types
            if not test_types:
                test_types = ['unit', 'integration']
            
            # Analyze code structure
            code_analysis = await self._analyze_code_structure(code, language)
            
            # Generate test cases using AI
            test_cases = await self._generate_test_cases_ai(
                code, language, framework, test_types, code_analysis
            )
            
            # Generate setup and teardown code
            setup_code = await self._generate_setup_code(code, language, framework)
            teardown_code = await self._generate_teardown_code(code, language, framework)
            
            # Determine dependencies
            dependencies = self._determine_test_dependencies(language, framework)
            
            test_suite = TestSuite(
                name=f"auto_generated_tests_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                language=language,
                framework=framework,
                test_cases=test_cases,
                setup_code=setup_code,
                teardown_code=teardown_code,
                dependencies=dependencies
            )
            
            self.logger.info(f"✅ Generated {len(test_cases)} test cases")
            return test_suite
            
        except Exception as e:
            self.logger.error(f"❌ Test generation error: {str(e)}")
            # Return empty test suite on error
            return TestSuite(
                name="empty_suite",
                language=language,
                framework=framework or "unknown",
                test_cases=[],
                setup_code="",
                teardown_code="",
                dependencies=[]
            )
    
    async def execute_tests(self, test_suite: TestSuite, project_path: Optional[str] = None) -> List[TestResult]:
        """
        Execute generated test suite
        
        Args:
            test_suite: TestSuite to execute
            project_path: Path to project directory (optional)
            
        Returns:
            List of TestResult objects
        """
        results = []
        
        try:
            self.logger.info(f"🚀 Executing test suite: {test_suite.name}")
            
            # Create temporary test environment
            with tempfile.TemporaryDirectory() as temp_dir:
                test_dir = Path(temp_dir)
                
                # Write test files
                test_files = await self._write_test_files(test_suite, test_dir)
                
                # Install dependencies if needed
                await self._install_test_dependencies(test_suite, test_dir)
                
                # Execute each test case
                for i, test_case in enumerate(test_suite.test_cases):
                    result = await self._execute_single_test(
                        test_case, test_suite, test_dir, i
                    )
                    results.append(result)
            
            # Calculate overall statistics
            passed = len([r for r in results if r.status == 'passed'])
            total = len(results)
            
            self.logger.info(f"✅ Test execution complete: {passed}/{total} tests passed")
            
        except Exception as e:
            self.logger.error(f"❌ Test execution error: {str(e)}")
            # Return error result
            results.append(TestResult(
                test_name="execution_error",
                status="error",
                execution_time=0.0,
                output="",
                error_message=str(e)
            ))
        
        return results
    
    def _detect_best_framework(self, language: str) -> str:
        """Detect the best testing framework for the language"""
        frameworks = self.supported_languages.get(language.lower(), [])
        return frameworks[0] if frameworks else 'unknown'
    
    async def _analyze_code_structure(self, code: str, language: str) -> Dict[str, Any]:
        """Analyze code structure to inform test generation"""
        analysis = {
            'functions': [],
            'classes': [],
            'imports': [],
            'complexity': 'low',
            'patterns': []
        }
        
        try:
            if language.lower() == 'python':
                analysis = await self._analyze_python_code(code)
            elif language.lower() in ['javascript', 'typescript']:
                analysis = await self._analyze_javascript_code(code)
            else:
                # Generic analysis for other languages
                analysis = await self._analyze_generic_code(code)
                
        except Exception as e:
            self.logger.error(f"❌ Code analysis error: {str(e)}")
        
        return analysis
    
    async def _analyze_python_code(self, code: str) -> Dict[str, Any]:
        """Analyze Python code structure"""
        analysis = {
            'functions': [],
            'classes': [],
            'imports': [],
            'complexity': 'low',
            'patterns': []
        }
        
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    analysis['functions'].append({
                        'name': node.name,
                        'args': [arg.arg for arg in node.args.args],
                        'decorators': [d.id for d in node.decorator_list if isinstance(d, ast.Name)],
                        'line_no': node.lineno
                    })
                elif isinstance(node, ast.ClassDef):
                    analysis['classes'].append({
                        'name': node.name,
                        'methods': [n.name for n in node.body if isinstance(n, ast.FunctionDef)],
                        'line_no': node.lineno
                    })
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        analysis['imports'].append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ''
                    for alias in node.names:
                        analysis['imports'].append(f"{module}.{alias.name}")
            
            # Determine complexity based on function count and nesting
            func_count = len(analysis['functions'])
            class_count = len(analysis['classes'])
            
            if func_count > 10 or class_count > 5:
                analysis['complexity'] = 'high'
            elif func_count > 5 or class_count > 2:
                analysis['complexity'] = 'medium'
            
        except Exception as e:
            self.logger.error(f"❌ Python code analysis error: {str(e)}")
        
        return analysis
    
    async def _analyze_javascript_code(self, code: str) -> Dict[str, Any]:
        """Analyze JavaScript/TypeScript code structure"""
        analysis = {
            'functions': [],
            'classes': [],
            'imports': [],
            'complexity': 'low',
            'patterns': []
        }
        
        # Simple regex-based analysis for JavaScript
        function_pattern = r'(?:function\s+(\w+)|const\s+(\w+)\s*=.*?(?:function|\(.*?\)\s*=>))'
        class_pattern = r'class\s+(\w+)'
        import_pattern = r'(?:import.*?from\s+[\'"]([^\'"]+)[\'"]|require\([\'"]([^\'"]+)[\'"]\))'
        
        functions = re.findall(function_pattern, code)
        classes = re.findall(class_pattern, code)
        imports = re.findall(import_pattern, code)
        
        analysis['functions'] = [{'name': f[0] or f[1], 'args': [], 'line_no': 0} for f in functions]
        analysis['classes'] = [{'name': cls, 'methods': [], 'line_no': 0} for cls in classes]
        analysis['imports'] = [imp[0] or imp[1] for imp in imports]
        
        # Determine complexity
        if len(functions) > 8 or len(classes) > 4:
            analysis['complexity'] = 'high'
        elif len(functions) > 4 or len(classes) > 2:
            analysis['complexity'] = 'medium'
        
        return analysis
    
    async def _analyze_generic_code(self, code: str) -> Dict[str, Any]:
        """Generic code analysis for unsupported languages"""
        analysis = {
            'functions': [],
            'classes': [],
            'imports': [],
            'complexity': 'medium',  # Default to medium for unknown languages
            'patterns': []
        }
        
        # Count lines as a basic complexity measure
        lines = len(code.split('\n'))
        if lines > 200:
            analysis['complexity'] = 'high'
        elif lines < 50:
            analysis['complexity'] = 'low'
        
        return analysis
    
    async def _generate_test_cases_ai(self, 
                                    code: str, 
                                    language: str, 
                                    framework: str,
                                    test_types: List[str],
                                    code_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate test cases using AI"""
        test_cases = []
        
        # If no AI client available, generate basic template tests
        if not self.ai_client:
            test_cases = self._generate_template_tests(code_analysis, language, framework)
        else:
            # Use AI to generate comprehensive tests
            try:
                prompt = self._build_test_generation_prompt(code, language, framework, test_types, code_analysis)
                
                # This would call the AI service (Claude/GPT) to generate tests
                # For now, we'll use template generation
                test_cases = self._generate_template_tests(code_analysis, language, framework)
                
            except Exception as e:
                self.logger.error(f"❌ AI test generation error: {str(e)}")
                test_cases = self._generate_template_tests(code_analysis, language, framework)
        
        return test_cases
    
    def _generate_template_tests(self, code_analysis: Dict[str, Any], language: str, framework: str) -> List[Dict[str, Any]]:
        """Generate template test cases based on code analysis"""
        test_cases = []
        
        if language.lower() == 'python' and framework == 'pytest':
            # Generate Python/pytest tests
            for func in code_analysis['functions']:
                test_cases.append({
                    'name': f"test_{func['name']}",
                    'type': 'unit',
                    'target_function': func['name'],
                    'test_code': self._generate_python_pytest_template(func),
                    'description': f"Test function {func['name']}",
                    'expected_result': 'pass'
                })
            
            for cls in code_analysis['classes']:
                test_cases.append({
                    'name': f"test_{cls['name'].lower()}_class",
                    'type': 'unit',
                    'target_class': cls['name'],
                    'test_code': self._generate_python_class_test_template(cls),
                    'description': f"Test class {cls['name']}",
                    'expected_result': 'pass'
                })
        
        elif language.lower() == 'javascript' and framework == 'jest':
            # Generate JavaScript/Jest tests
            for func in code_analysis['functions']:
                test_cases.append({
                    'name': f"{func['name']}.test",
                    'type': 'unit',
                    'target_function': func['name'],
                    'test_code': self._generate_jest_template(func),
                    'description': f"Test function {func['name']}",
                    'expected_result': 'pass'
                })
        
        # Add integration tests if complexity is medium or high
        if code_analysis['complexity'] in ['medium', 'high']:
            test_cases.append({
                'name': 'test_integration',
                'type': 'integration',
                'target_function': 'multiple',
                'test_code': self._generate_integration_test_template(language, framework),
                'description': 'Integration test for multiple components',
                'expected_result': 'pass'
            })
        
        return test_cases
    
    def _generate_python_pytest_template(self, func: Dict[str, Any]) -> str:
        """Generate Python pytest template"""
        return f'''def test_{func['name']}():
    """Test function {func['name']}"""
    # TODO: Implement test logic for {func['name']}
    # Test with valid inputs
    # result = {func['name']}({', '.join(['test_' + arg for arg in func['args']])})
    # assert result is not None
    
    # Test edge cases
    # Test error conditions
    pass
'''
    
    def _generate_python_class_test_template(self, cls: Dict[str, Any]) -> str:
        """Generate Python class test template"""
        return f'''class Test{cls['name']}:
    """Test class for {cls['name']}"""
    
    def setup_method(self):
        """Setup test fixtures"""
        # TODO: Initialize test instance
        # self.instance = {cls['name']}()
        pass
    
    def test_initialization(self):
        """Test class initialization"""
        # TODO: Test constructor
        # assert self.instance is not None
        pass
    
    def teardown_method(self):
        """Cleanup after tests"""
        # TODO: Cleanup resources
        pass
'''
    
    def _generate_jest_template(self, func: Dict[str, Any]) -> str:
        """Generate Jest test template"""
        return f'''describe('{func['name']}', () => {{
    test('should work correctly', () => {{
        // TODO: Implement test for {func['name']}
        // const result = {func['name']}(testInput);
        // expect(result).toBeDefined();
    }});
    
    test('should handle edge cases', () => {{
        // TODO: Test edge cases
    }});
    
    test('should handle errors gracefully', () => {{
        // TODO: Test error conditions
    }});
}});
'''
    
    def _generate_integration_test_template(self, language: str, framework: str) -> str:
        """Generate integration test template"""
        if language.lower() == 'python':
            return '''def test_integration():
    """Integration test for multiple components"""
    # TODO: Test component interactions
    # Test data flow between components
    # Test end-to-end scenarios
    pass
'''
        else:
            return '''// Integration test template
// TODO: Implement integration tests
// Test component interactions
// Test data flow
// Test end-to-end scenarios
'''
    
    def _build_test_generation_prompt(self, code: str, language: str, framework: str, test_types: List[str], analysis: Dict[str, Any]) -> str:
        """Build prompt for AI test generation"""
        return f"""
Generate comprehensive {framework} tests for the following {language} code:

Code to test:
```{language}
{code}
```

Code analysis:
- Functions: {len(analysis['functions'])}
- Classes: {len(analysis['classes'])}
- Complexity: {analysis['complexity']}

Requirements:
- Test types: {', '.join(test_types)}
- Framework: {framework}
- Include edge cases and error conditions
- Aim for high code coverage
- Follow {framework} best practices

Generate complete, executable test code.
"""
    
    async def _generate_setup_code(self, code: str, language: str, framework: str) -> str:
        """Generate setup code for tests"""
        setup_templates = {
            ('python', 'pytest'): '''import pytest
import sys
import os

# Add source directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

@pytest.fixture
def sample_data():
    """Provide sample test data"""
    return {"test": "data"}
''',
            ('javascript', 'jest'): '''// Test setup
beforeAll(() => {
    // Global setup
});

beforeEach(() => {
    // Setup before each test
});
''',
            ('python', 'unittest'): '''import unittest
import sys
import os

# Add source directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
'''
        }
        
        return setup_templates.get((language.lower(), framework), '# Test setup\n')
    
    async def _generate_teardown_code(self, code: str, language: str, framework: str) -> str:
        """Generate teardown code for tests"""
        teardown_templates = {
            ('javascript', 'jest'): '''afterEach(() => {
    // Cleanup after each test
});

afterAll(() => {
    // Global cleanup
});
''',
            ('python', 'pytest'): '''# Pytest teardown
def teardown_module():
    """Module-level teardown"""
    pass
'''
        }
        
        return teardown_templates.get((language.lower(), framework), '# Test teardown\n')
    
    def _determine_test_dependencies(self, language: str, framework: str) -> List[str]:
        """Determine test dependencies"""
        dependencies = {
            ('python', 'pytest'): ['pytest', 'pytest-cov'],
            ('python', 'unittest'): [],  # Built into Python
            ('javascript', 'jest'): ['jest'],
            ('javascript', 'mocha'): ['mocha', 'chai'],
            ('typescript', 'jest'): ['jest', '@types/jest', 'ts-jest'],
        }
        
        return dependencies.get((language.lower(), framework), [])
    
    async def _write_test_files(self, test_suite: TestSuite, test_dir: Path) -> List[Path]:
        """Write test files to temporary directory"""
        test_files = []
        
        # Write setup file
        if test_suite.setup_code:
            setup_file = test_dir / 'setup.py'
            setup_file.write_text(test_suite.setup_code)
            test_files.append(setup_file)
        
        # Write individual test files
        for i, test_case in enumerate(test_suite.test_cases):
            filename = f"test_{test_case['name']}_{i}"
            
            if test_suite.language.lower() == 'python':
                filename += '.py'
            elif test_suite.language.lower() in ['javascript', 'typescript']:
                filename += '.js'
            
            test_file = test_dir / filename
            test_content = f"{test_suite.setup_code}\n\n{test_case['test_code']}\n\n{test_suite.teardown_code}"
            test_file.write_text(test_content)
            test_files.append(test_file)
        
        return test_files
    
    async def _install_test_dependencies(self, test_suite: TestSuite, test_dir: Path):
        """Install test dependencies"""
        if not test_suite.dependencies:
            return
        
        try:
            if test_suite.language.lower() == 'python':
                cmd = ['pip', 'install'] + test_suite.dependencies
                subprocess.run(cmd, cwd=test_dir, capture_output=True, timeout=60)
            elif test_suite.language.lower() in ['javascript', 'typescript']:
                # Create package.json if it doesn't exist
                package_json = test_dir / 'package.json'
                if not package_json.exists():
                    package_data = {
                        "name": "auto-generated-tests",
                        "version": "1.0.0",
                        "scripts": {"test": "jest"}
                    }
                    package_json.write_text(json.dumps(package_data, indent=2))
                
                cmd = ['npm', 'install'] + test_suite.dependencies
                subprocess.run(cmd, cwd=test_dir, capture_output=True, timeout=120)
        
        except Exception as e:
            self.logger.error(f"❌ Dependency installation error: {str(e)}")
    
    async def _execute_single_test(self, test_case: Dict[str, Any], test_suite: TestSuite, test_dir: Path, index: int) -> TestResult:
        """Execute a single test case"""
        start_time = datetime.now()
        
        try:
            # Determine test command based on framework
            if test_suite.framework == 'pytest':
                cmd = ['python', '-m', 'pytest', '-v', f'test_{test_case["name"]}_{index}.py']
            elif test_suite.framework == 'jest':
                cmd = ['npm', 'test', f'test_{test_case["name"]}_{index}.js']
            else:
                # Generic execution
                cmd = ['python', f'test_{test_case["name"]}_{index}.py']
            
            # Execute test
            process = subprocess.run(
                cmd,
                cwd=test_dir,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Determine test status
            if process.returncode == 0:
                status = 'passed'
                error_message = None
            else:
                status = 'failed'
                error_message = process.stderr
            
            return TestResult(
                test_name=test_case['name'],
                status=status,
                execution_time=execution_time,
                output=process.stdout,
                error_message=error_message
            )
        
        except subprocess.TimeoutExpired:
            return TestResult(
                test_name=test_case['name'],
                status='error',
                execution_time=30.0,
                output='',
                error_message='Test execution timed out'
            )
        except Exception as e:
            return TestResult(
                test_name=test_case['name'],
                status='error',
                execution_time=0.0,
                output='',
                error_message=str(e)
            )
    
    async def get_test_coverage(self, test_suite: TestSuite, source_code: str) -> Dict[str, Any]:
        """Calculate test coverage metrics"""
        coverage_data = {
            'overall_coverage': 0.0,
            'line_coverage': 0.0,
            'function_coverage': 0.0,
            'branch_coverage': 0.0,
            'uncovered_lines': [],
            'coverage_report': ''
        }
        
        try:
            # This is a simplified coverage calculation
            # In a real implementation, you'd use coverage tools like coverage.py, nyc, etc.
            
            # For now, estimate coverage based on test cases vs functions
            code_analysis = await self._analyze_code_structure(source_code, test_suite.language)
            total_functions = len(code_analysis['functions']) + len(code_analysis['classes'])
            
            if total_functions > 0:
                tested_functions = len([tc for tc in test_suite.test_cases if tc['type'] == 'unit'])
                coverage_data['function_coverage'] = min((tested_functions / total_functions) * 100, 100.0)
                coverage_data['overall_coverage'] = coverage_data['function_coverage'] * 0.8  # Estimate
            
        except Exception as e:
            self.logger.error(f"❌ Coverage calculation error: {str(e)}")
        
        return coverage_data