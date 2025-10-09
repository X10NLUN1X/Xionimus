"""Documentation Agent using Claude Sonnet 4"""
import logging
import re
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

from ...models.agent_models import AgentType
from ..base_agent import BaseAgent

logger = logging.getLogger(__name__)


class DocumentationAgent(BaseAgent):
    """
    Documentation Agent powered by Claude Sonnet 4
    Generates comprehensive documentation
    """
    
    def __init__(self, api_keys=None):
        super().__init__(AgentType.DOCUMENTATION, api_keys=api_keys)
    
    def _validate_input(self, input_data: Dict[str, Any]):
        """Validate documentation input"""
        super()._validate_input(input_data)
        
        if "code" not in input_data and "topic" not in input_data:
            raise ValueError("Either code or topic must be provided")
    
    def _generate_readme_template(self, project_name: str, description: str) -> str:
        """Generate README.md template"""
        return f"""# {project_name}

{description}

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Examples](#examples)
- [Contributing](#contributing)
- [License](#license)

## Installation

```bash
# Installation instructions will be added
```

## Usage

```python
# Basic usage example
```

## API Documentation

See API documentation below.

## Examples

### Example 1: Basic Usage

### Example 2: Advanced Usage

## Contributing

Contributions are welcome! Please read the contributing guidelines first.

## License

[Specify License]
"""
    
    def _generate_inline_comments(self, code: str, language: str) -> str:
        """Generate inline code comments"""
        comment_style = {
            "python": "#",
            "javascript": "//",
            "typescript": "//",
            "java": "//",
            "c": "//",
            "cpp": "//",
            "go": "//",
            "ruby": "#",
            "php": "//",
        }
        
        comment_char = comment_style.get(language.lower(), "//")
        return f"{comment_char} TODO: Add inline comments"
    
    def _extract_functions_classes(self, code: str, language: str) -> List[Dict[str, str]]:
        """Extract functions and classes from code for API documentation"""
        items = []
        
        # Python patterns
        if language.lower() == "python":
            # Find functions
            func_pattern = r'def\s+(\w+)\s*\((.*?)\):'
            for match in re.finditer(func_pattern, code):
                items.append({
                    "type": "function",
                    "name": match.group(1),
                    "params": match.group(2),
                    "language": "python"
                })
            
            # Find classes
            class_pattern = r'class\s+(\w+)(?:\(.*?\))?:'
            for match in re.finditer(class_pattern, code):
                items.append({
                    "type": "class",
                    "name": match.group(1),
                    "language": "python"
                })
        
        # JavaScript/TypeScript patterns
        elif language.lower() in ["javascript", "typescript"]:
            # Find functions
            func_pattern = r'(?:function|const|let|var)\s+(\w+)\s*=?\s*(?:\(.*?\)|async)'
            for match in re.finditer(func_pattern, code):
                items.append({
                    "type": "function",
                    "name": match.group(1),
                    "language": language
                })
        
        return items
    
    def get_system_prompt(self) -> str:
        """Get documentation agent system prompt"""
        return """You are an expert technical writer. Create clear, comprehensive 
        documentation that is:
        - Well-structured with proper headings and sections
        - Easy to understand for target audience
        - Complete with practical examples and use cases
        - Following documentation best practices (README, API docs, inline comments)
        - Includes code snippets and usage examples
        - Professional and consistent formatting
        
        Use markdown formatting for readability. For API documentation, use clear
        parameter descriptions, return values, and example usage."""
    
    async def _execute_internal(
        self,
        input_data: Dict[str, Any],
        execution_id: str,
        session_id: Optional[str],
        user_id: Optional[str],
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate documentation"""
        code = input_data.get("code", "")
        topic = input_data.get("topic", "")
        doc_type = input_data.get("doc_type", "api")  # api, tutorial, guide, reference
        language = input_data.get("language", "python")
        
        # Build documentation prompt
        prompt = f"""Generate {doc_type} documentation for:

"""
        if code:
            prompt += f"**Code:**\n```{language}\n{code}\n```\n\n"
        
        if topic:
            prompt += f"**Topic:**\n{topic}\n\n"
        
        # Enhanced prompt based on doc type
        if doc_type == "readme":
            prompt += """
Create a comprehensive README.md including:
1. **Project Title and Description**
2. **Table of Contents**
3. **Installation Instructions**
4. **Quick Start Guide**
5. **Usage Examples** (multiple scenarios)
6. **API Documentation** (if applicable)
7. **Configuration Options**
8. **Troubleshooting**
9. **Contributing Guidelines**
10. **License Information**

Use markdown formatting with badges, code blocks, and clear sections."""
        
        elif doc_type == "api":
            prompt += """
Create comprehensive API documentation including:
1. **API Overview**: Purpose and capabilities
2. **Authentication**: How to authenticate
3. **Endpoints**: All available endpoints with:
   - HTTP Method
   - URL Path
   - Parameters (query, path, body)
   - Request Examples
   - Response Format
   - Status Codes
   - Error Handling
4. **Data Models**: Schema definitions
5. **Rate Limiting**: If applicable
6. **Examples**: Practical usage examples

Use OpenAPI/Swagger style formatting."""
        
        elif doc_type == "inline":
            prompt += """
Generate inline code comments for the provided code including:
1. **File/Module docstring**: Purpose and overview
2. **Function/Method docstrings**: Parameters, returns, raises
3. **Complex logic explanations**: Inline comments for tricky parts
4. **Type hints**: Where applicable
5. **Usage examples**: In docstrings

Follow language-specific documentation standards (PEP 257 for Python, JSDoc for JavaScript, etc.)"""
        
        else:
            prompt += f"""
Create comprehensive {doc_type} documentation including:
1. **Overview**: Purpose and functionality
2. **Usage**: How to use with examples
3. **Parameters/Arguments**: Detailed descriptions
4. **Return Values**: What is returned
5. **Examples**: Practical use cases (at least 3)
6. **Notes**: Important considerations
7. **See Also**: Related documentation

Use markdown formatting and be thorough."""
        
        # Call Claude API
        response = self.client.messages.create(
            model=self.model,
            max_tokens=options.get("max_tokens", 4000),
            temperature=options.get("temperature", 0.4),
            system=self.get_system_prompt(),
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        content = response.content[0].text
        
        # Extract code examples from documentation
        code_examples = re.findall(r'```[\w]*\n(.*?)```', content, re.DOTALL)
        
        # Extract functions/classes if code provided
        api_items = []
        if code:
            api_items = self._extract_functions_classes(code, language)
        
        # Generate README template if requested
        readme_template = None
        if doc_type == "readme" and topic:
            readme_template = self._generate_readme_template(
                topic.split()[0] if topic else "Project",
                topic if topic else "Project description"
            )
        
        return {
            "documentation": content,
            "doc_type": doc_type,
            "language": language,
            "code_examples_count": len(code_examples),
            "code_examples": code_examples[:5],  # First 5 examples
            "api_items": api_items,
            "api_items_count": len(api_items),
            "readme_template": readme_template,
            "export_formats": ["markdown", "html", "pdf"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "model_used": self.model,
            "token_usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens
            }
        }