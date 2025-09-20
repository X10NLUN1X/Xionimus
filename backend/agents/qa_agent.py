import re
from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentTask, AgentStatus, AgentCapability
import os
from openai import AsyncOpenAI

class QAAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="QA Agent",
            description="Specialized in testing, quality assurance, and validation using Perplexity AI for current best practices",
            capabilities=[
                AgentCapability.TESTING
            ]
        )
        self.ai_model = "perplexity"
        
    def can_handle_task(self, task_description: str, context: Dict[str, Any]) -> float:
        """Evaluate if this agent can handle the task"""
        qa_keywords = [
            'test', 'testing', 'quality', 'assurance', 'qa', 'validation',
            'verify', 'check', 'review', 'audit', 'inspect', 'evaluate',
            'bug', 'defect', 'issue', 'error', 'failure', 'regression',
            'unit test', 'integration test', 'e2e test', 'automation',
            'testen', 'prüfen', 'qualität', 'validierung', 'überprüfung',
            'selenium', 'cypress', 'jest', 'pytest', 'testng', 'junit',
            'performance test', 'load test', 'security test', 'usability'
        ]
        
        description_lower = task_description.lower()
        matches = sum(1 for keyword in qa_keywords if keyword in description_lower)
        confidence = min(matches / 3, 1.0)
        
        # Boost confidence for testing-specific terms
        if any(term in description_lower for term in ['test', 'testing', 'qa', 'quality assurance']):
            confidence += 0.4
        
        # Boost for testing frameworks
        if any(framework in description_lower for framework in ['selenium', 'cypress', 'jest', 'pytest']):
            confidence += 0.3
            
        # Boost if context suggests testing
        if context.get('file_extension') in ['.test.js', '.spec.js', '.test.py', '.spec.py']:
            confidence += 0.3
            
        return min(confidence, 1.0)
    
    async def execute_task(self, task: AgentTask) -> AgentTask:
        """Execute QA tasks using Perplexity AI for current best practices"""
        try:
            task.status = AgentStatus.THINKING
            await self.update_progress(task, 0.1, "Initializing Perplexity for QA research")
            
            # Get Perplexity client
            api_key = os.environ.get('PERPLEXITY_API_KEY')
            if not api_key:
                raise Exception("Perplexity API key not configured")
            
            client = AsyncOpenAI(
                api_key=api_key,
                base_url="https://api.perplexity.ai"
            )
            
            await self.update_progress(task, 0.3, "Analyzing testing requirements")
            
            task_type = self._identify_qa_task_type(task.description)
            enhanced_prompt = self._create_qa_prompt(task.description, task_type, task.input_data)
            
            await self.update_progress(task, 0.6, f"Researching {task_type} best practices")
            
            # Make API call to Perplexity for current testing best practices
            response = await client.chat.completions.create(
                model="sonar",
                messages=[
                    {"role": "system", "content": "You are a QA expert and testing specialist. Provide current testing best practices, tools, and methodologies with up-to-date information."},
                    {"role": "user", "content": enhanced_prompt}
                ],
                max_tokens=4000,
                temperature=0.3,
                stream=False
            )
            
            await self.update_progress(task, 0.8, "Processing QA recommendations")
            
            content = response.choices[0].message.content
            sources = getattr(response, 'search_results', [])
            
            # Structure the QA result
            result = self._process_qa_response(content, task_type, task.input_data, sources)
            task.result = result
            
            task.status = AgentStatus.COMPLETED
            await self.update_progress(task, 1.0, "QA analysis completed successfully")
            
        except Exception as e:
            task.status = AgentStatus.ERROR
            task.error_message = f"QA analysis failed: {str(e)}"
            self.logger.error(f"QA agent error: {e}")
            
        return task
    
    def _identify_qa_task_type(self, description: str) -> str:
        """Identify the type of QA task"""
        description_lower = description.lower()
        
        if any(word in description_lower for word in ['unit test', 'unit testing']):
            return "unit_testing"
        elif any(word in description_lower for word in ['integration test', 'integration testing']):
            return "integration_testing"
        elif any(word in description_lower for word in ['e2e', 'end to end', 'end-to-end']):
            return "e2e_testing"
        elif any(word in description_lower for word in ['performance', 'load', 'stress']):
            return "performance_testing"
        elif any(word in description_lower for word in ['security', 'penetration', 'vulnerability']):
            return "security_testing"
        elif any(word in description_lower for word in ['automation', 'automated', 'ci/cd']):
            return "test_automation"
        elif any(word in description_lower for word in ['usability', 'user experience', 'ux']):
            return "usability_testing"
        elif any(word in description_lower for word in ['api', 'rest', 'graphql']):
            return "api_testing"
        else:
            return "general_testing"
    
    def _create_qa_prompt(self, description: str, task_type: str, input_data: Dict[str, Any]) -> str:
        """Create an enhanced prompt for QA tasks"""
        language = input_data.get('language', 'english')
        technology_stack = input_data.get('technology_stack', '')
        project_type = input_data.get('project_type', '')
        
        language_instructions = {
            'german': "Bitte antworte auf Deutsch und verwende aktuelle deutsche Testing-Ressourcen.",
            'english': "Please respond in English and use current English testing resources.",
            'spanish': "Por favor responde en español y usa recursos de testing actuales en español.",
            'french': "Veuillez répondre en français et utiliser des ressources de test actuelles en français.",
            'italian': "Si prega di rispondere in italiano e utilizzare risorse di testing attuali in italiano."
        }
        
        lang_instruction = language_instructions.get(language, language_instructions['english'])
        
        base_prompt = f"{description}\n\n{lang_instruction}\n\n"
        
        if task_type == "unit_testing":
            base_prompt += """
Provide current best practices for unit testing including:
- Latest testing frameworks and tools (2024-2025)
- Test structure and organization patterns
- Mocking and stubbing strategies
- Code coverage best practices
- CI/CD integration
- Specific examples and code samples
"""
        elif task_type == "integration_testing":
            base_prompt += """
Provide current best practices for integration testing including:
- Modern integration testing approaches
- Database and API testing strategies
- Container-based testing environments
- Service virtualization
- Data management in tests
- Current tools and frameworks
"""
        elif task_type == "e2e_testing":
            base_prompt += """
Provide current best practices for end-to-end testing including:
- Modern E2E testing frameworks (Playwright, Cypress, etc.)
- Browser automation strategies
- Visual regression testing
- Cross-browser testing approaches
- Mobile testing considerations
- Performance and reliability optimization
"""
        elif task_type == "performance_testing":
            base_prompt += """
Provide current best practices for performance testing including:
- Latest performance testing tools
- Load testing strategies and patterns
- Monitoring and observability
- Performance budgets and SLAs
- Cloud-based testing solutions
- Metrics and reporting
"""
        elif task_type == "security_testing":
            base_prompt += """
Provide current best practices for security testing including:
- Latest security testing tools (2024-2025)
- OWASP top 10 testing approaches
- Automated vulnerability scanning
- Penetration testing methodologies
- API security testing
- Compliance and regulatory requirements
"""
        elif task_type == "test_automation":
            base_prompt += """
Provide current best practices for test automation including:
- Modern automation frameworks and tools
- CI/CD pipeline integration
- Test data management
- Parallel execution strategies
- Reporting and analytics
- Maintenance and scalability
"""
        
        if technology_stack:
            base_prompt += f"\nTechnology stack: {technology_stack}"
        
        if project_type:
            base_prompt += f"\nProject type: {project_type}"
        
        base_prompt += "\nFocus on the most current practices, tools, and methodologies available in 2024-2025."
        
        return base_prompt
    
    def _process_qa_response(self, content: str, task_type: str, input_data: Dict[str, Any], sources: List[Dict]) -> Dict[str, Any]:
        """Process the QA response into structured format"""
        result = {
            "type": task_type,
            "qa_content": content,
            "sources": sources,
            "ai_model_used": "perplexity",
            "best_practices": self._extract_best_practices(content),
            "tools_recommended": self._extract_tools(content),
            "frameworks_mentioned": self._extract_frameworks(content),
            "key_recommendations": self._extract_recommendations(content)
        }
        
        # Add task-specific fields
        if task_type == "unit_testing":
            result.update({
                "testing_patterns": self._extract_testing_patterns(content),
                "coverage_recommendations": self._extract_coverage_info(content)
            })
        elif task_type == "performance_testing":
            result.update({
                "performance_metrics": self._extract_performance_metrics(content),
                "load_testing_strategies": self._extract_load_strategies(content)
            })
        elif task_type == "security_testing":
            result.update({
                "security_vulnerabilities": self._extract_vulnerabilities(content),
                "compliance_standards": self._extract_compliance_standards(content)
            })
        elif task_type == "test_automation":
            result.update({
                "automation_frameworks": self._extract_automation_frameworks(content),
                "ci_cd_practices": self._extract_cicd_practices(content)
            })
        
        return result
    
    def _extract_best_practices(self, content: str) -> List[str]:
        """Extract best practices from the content"""
        practices = []
        lines = content.split('\n')
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['best practice', 'recommendation', 'should', 'must', 'important']):
                practices.append(line.strip())
        
        return practices[:15]
    
    def _extract_tools(self, content: str) -> List[str]:
        """Extract testing tools mentioned in content"""
        tools = []
        tool_keywords = [
            'selenium', 'cypress', 'playwright', 'jest', 'pytest', 'testng', 'junit',
            'postman', 'newman', 'insomnia', 'k6', 'jmeter', 'gatling',
            'burp suite', 'owasp zap', 'sonarqube', 'codecov', 'coveralls'
        ]
        
        content_lower = content.lower()
        for tool in tool_keywords:
            if tool in content_lower:
                tools.append(tool)
        
        return list(set(tools))  # Remove duplicates
    
    def _extract_frameworks(self, content: str) -> List[str]:
        """Extract testing frameworks mentioned in content"""
        frameworks = []
        framework_keywords = [
            'react testing library', 'vue test utils', 'angular testing',
            'mocha', 'jasmine', 'qunit', 'ava', 'tape',
            'rspec', 'minitest', 'phpunit', 'nunit', 'xunit'
        ]
        
        content_lower = content.lower()
        for framework in framework_keywords:
            if framework in content_lower:
                frameworks.append(framework)
        
        return list(set(frameworks))
    
    def _extract_recommendations(self, content: str) -> List[str]:
        """Extract key recommendations from content"""
        recommendations = []
        lines = content.split('\n')
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['recommend', 'suggest', 'consider', 'advice', 'tip']):
                recommendations.append(line.strip())
        
        return recommendations[:10]
    
    def _extract_testing_patterns(self, content: str) -> List[str]:
        """Extract testing patterns mentioned in content"""
        patterns = []
        pattern_keywords = [
            'aaa pattern', 'given-when-then', 'page object model', 'data driven',
            'keyword driven', 'behavior driven', 'test pyramid', 'testing trophy'
        ]
        
        content_lower = content.lower()
        for pattern in pattern_keywords:
            if pattern in content_lower:
                patterns.append(pattern)
        
        return patterns
    
    def _extract_coverage_info(self, content: str) -> List[str]:
        """Extract code coverage information from content"""
        coverage_info = []
        lines = content.split('\n')
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['coverage', 'code coverage', 'test coverage']):
                coverage_info.append(line.strip())
        
        return coverage_info[:5]
    
    def _extract_performance_metrics(self, content: str) -> List[str]:
        """Extract performance metrics mentioned in content"""
        metrics = []
        metric_keywords = [
            'response time', 'throughput', 'latency', 'cpu usage', 'memory usage',
            'requests per second', 'concurrent users', 'error rate'
        ]
        
        content_lower = content.lower()
        for metric in metric_keywords:
            if metric in content_lower:
                metrics.append(metric)
        
        return metrics
    
    def _extract_load_strategies(self, content: str) -> List[str]:
        """Extract load testing strategies from content"""
        strategies = []
        lines = content.split('\n')
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['load strategy', 'testing strategy', 'approach']):
                strategies.append(line.strip())
        
        return strategies[:5]
    
    def _extract_vulnerabilities(self, content: str) -> List[str]:
        """Extract security vulnerabilities mentioned in content"""
        vulnerabilities = []
        vuln_keywords = [
            'sql injection', 'xss', 'csrf', 'authentication bypass',
            'authorization', 'session management', 'input validation'
        ]
        
        content_lower = content.lower()
        for vuln in vuln_keywords:
            if vuln in content_lower:
                vulnerabilities.append(vuln)
        
        return vulnerabilities
    
    def _extract_compliance_standards(self, content: str) -> List[str]:
        """Extract compliance standards mentioned in content"""
        standards = []
        standard_keywords = [
            'owasp', 'pci dss', 'gdpr', 'hipaa', 'sox', 'iso 27001',
            'nist', 'cis controls'
        ]
        
        content_lower = content.lower()
        for standard in standard_keywords:
            if standard in content_lower:
                standards.append(standard.upper())
        
        return list(set(standards))
    
    def _extract_automation_frameworks(self, content: str) -> List[str]:
        """Extract automation frameworks from content"""
        frameworks = []
        framework_keywords = [
            'selenium grid', 'appium', 'robot framework', 'cucumber',
            'specflow', 'gauge', 'testcomplete', 'katalon'
        ]
        
        content_lower = content.lower()
        for framework in framework_keywords:
            if framework in content_lower:
                frameworks.append(framework)
        
        return frameworks
    
    def _extract_cicd_practices(self, content: str) -> List[str]:
        """Extract CI/CD practices from content"""
        practices = []
        lines = content.split('\n')
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['ci/cd', 'continuous', 'pipeline', 'deployment']):
                practices.append(line.strip())
        
        return practices[:8]