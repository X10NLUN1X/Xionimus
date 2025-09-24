"""
Offline AI Simulator - Provides intelligent mock responses when APIs are unavailable
Works around DNS blocks and connection issues by providing contextually appropriate responses
"""
import re
import random
from typing import Dict, Any, List
from datetime import datetime

class OfflineAISimulator:
    """Simulates AI responses when external APIs are blocked"""
    
    def __init__(self):
        self.code_templates = {
            'python': {
                'function': '''def {function_name}({params}):
    """
    {description}
    """
    # Implementation here
    {implementation}
    return result''',
                'class': '''class {class_name}:
    """
    {description}
    """
    def __init__(self{params}):
        {init_code}
    
    def {method_name}(self{method_params}):
        {method_implementation}
        return result''',
                'todo_app': '''# Simple TODO List Manager
class TodoManager:
    def __init__(self):
        self.tasks = []
    
    def add_task(self, description, priority="medium"):
        """Add a new task to the list"""
        task = {
            "id": len(self.tasks) + 1,
            "description": description,
            "priority": priority,
            "completed": False,
            "created_at": datetime.now().isoformat()
        }
        self.tasks.append(task)
        return task
    
    def complete_task(self, task_id):
        """Mark a task as completed"""
        for task in self.tasks:
            if task["id"] == task_id:
                task["completed"] = True
                return True
        return False
    
    def delete_task(self, task_id):
        """Delete a task from the list"""
        self.tasks = [t for t in self.tasks if t["id"] != task_id]
    
    def get_tasks(self, completed=None):
        """Get all tasks or filter by completion status"""
        if completed is None:
            return self.tasks
        return [t for t in self.tasks if t["completed"] == completed]

# Example usage:
todo = TodoManager()
todo.add_task("Learn Python programming", "high")
todo.add_task("Build a web application", "medium")
print("Current tasks:", todo.get_tasks(completed=False))'''
            },
            'javascript': {
                'function': '''function {function_name}({params}) {{
    /**
     * {description}
     */
    {implementation}
    return result;
}}''',
                'react_component': '''import React, {{ useState, useEffect }} from 'react';

function {component_name}({{ {props} }}) {{
    const [state, setState] = useState({initial_state});
    
    useEffect(() => {{
        // Component initialization
        {effect_code}
    }}, []);
    
    const handle{action} = ({params}) => {{
        {handler_code}
    }};
    
    return (
        <div className="{css_class}">
            <h2>{title}</h2>
            {jsx_content}
        </div>
    );
}}

export default {component_name};'''
            },
            'html': {
                'landing_page': '''<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page_title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Arial', sans-serif;
            line-height: 1.6;
            color: #333;
        }}
        
        .hero {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-align: center;
            padding: 100px 0;
        }}
        
        .hero h1 {{
            font-size: 3rem;
            margin-bottom: 1rem;
        }}
        
        .hero p {{
            font-size: 1.2rem;
            max-width: 600px;
            margin: 0 auto;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }}
        
        .btn {{
            display: inline-block;
            background: #ff6b6b;
            color: white;
            padding: 12px 30px;
            text-decoration: none;
            border-radius: 5px;
            margin-top: 20px;
            transition: background 0.3s;
        }}
        
        .btn:hover {{
            background: #ff5252;
        }}
    </style>
</head>
<body>
    <section class="hero">
        <div class="container">
            <h1>{main_heading}</h1>
            <p>{description}</p>
            <a href="#contact" class="btn">Jetzt starten</a>
        </div>
    </section>
    
    <section class="features">
        <div class="container">
            <h2>Unsere Features</h2>
            {features_content}
        </div>
    </section>
</body>
</html>'''
            }
        }
    
    def analyze_request(self, message: str) -> Dict[str, Any]:
        """Analyze user request to determine appropriate response type"""
        message_lower = message.lower()
        
        # Code-related keywords
        code_indicators = ['code', 'function', 'class', 'programmier', 'entwickle', 'erstelle', 'python', 'javascript', 'react', 'html', 'css']
        
        # Research-related keywords  
        research_indicators = ['erkläre', 'explain', 'was ist', 'what is', 'wie funktioniert', 'recherche', 'information']
        
        # Conversational indicators
        greeting_indicators = ['hallo', 'hi', 'hello', 'guten tag', 'wie geht']
        
        analysis = {
            'is_code_request': any(indicator in message_lower for indicator in code_indicators),
            'is_research_request': any(indicator in message_lower for indicator in research_indicators),
            'is_greeting': any(indicator in message_lower for indicator in greeting_indicators),
            'language_detected': self._detect_programming_language(message),
            'complexity': len(message.split()),
            'has_question': '?' in message
        }
        
        return analysis
    
    def _detect_programming_language(self, message: str) -> str:
        """Detect programming language from the message"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['python', 'def', 'import', 'django', 'flask']):
            return 'python'
        elif any(word in message_lower for word in ['javascript', 'js', 'react', 'node', 'function']):
            return 'javascript'
        elif any(word in message_lower for word in ['html', 'website', 'landing', 'webpage']):
            return 'html'
        elif any(word in message_lower for word in ['css', 'style', 'design']):
            return 'css'
        
        return 'python'  # Default fallback
    
    def generate_code_response(self, message: str, language: str = 'python') -> str:
        """Generate appropriate code based on the request"""
        message_lower = message.lower()
        
        if 'todo' in message_lower or 'task' in message_lower:
            if language == 'python':
                return self.code_templates['python']['todo_app']
        
        if 'function' in message_lower or 'funktion' in message_lower:
            if language == 'python':
                return self.code_templates['python']['function'].format(
                    function_name='my_function',
                    params='param1, param2',
                    description='Generated function based on your request',
                    implementation='    # Add your logic here\n    result = param1 + param2'
                )
        
        if 'landing' in message_lower or 'website' in message_lower:
            return self.code_templates['html']['landing_page'].format(
                page_title='Meine Website',
                main_heading='Willkommen auf meiner Website',
                description='Eine moderne, responsive Website erstellt mit HTML und CSS.',
                features_content='<p>Feature 1, Feature 2, Feature 3</p>'
            )
        
        # Default code response
        return f"""# {language.title()} Code Beispiel
# Erstellt basierend auf Ihrer Anfrage: "{message[:50]}..."

def example_function():
    '''
    Diese Funktion wurde automatisch generiert.
    Passen Sie sie an Ihre Bedürfnisse an.
    '''
    print("Hello from {language}!")
    return "Erfolgreich ausgeführt"

# Verwendung:
result = example_function()
print(result)
"""
    
    def generate_conversational_response(self, message: str, analysis: Dict[str, Any]) -> str:
        """Generate conversational responses"""
        
        if analysis['is_greeting']:
            responses = [
                "Hallo! Ich bin Xionimus AI, Ihr intelligenter Assistent. Wie kann ich Ihnen heute helfen?",
                "Guten Tag! Ich stehe Ihnen für alle Ihre Fragen zur Verfügung. Was möchten Sie wissen?",
                "Hallo! Schön, Sie zu treffen. Ich kann Ihnen bei Programmierung, Recherche und vielem mehr helfen."
            ]
            return random.choice(responses)
        
        if analysis['is_research_request']:
            return self._generate_research_response(message)
        
        # General conversational response
        return f"""Ich verstehe Ihre Anfrage: "{message[:100]}{'...' if len(message) > 100 else ''}"

Als AI-Assistent kann ich Ihnen bei verschiedenen Aufgaben helfen:

🔧 **Programmierung**: Code in Python, JavaScript, React, HTML/CSS
📚 **Recherche**: Informationen und Erklärungen zu verschiedenen Themen  
💡 **Problemlösung**: Technische Analysen und Lösungsvorschläge
📝 **Dokumentation**: Erstellung von Dokumentation und Anleitungen

Können Sie mir mehr Details zu Ihrem spezifischen Anliegen geben?"""
    
    def _generate_research_response(self, message: str) -> str:
        """Generate research-style responses"""
        topic_keywords = {
            'ai': 'Künstliche Intelligenz (AI) ist ein Bereich der Informatik, der sich mit der Entwicklung intelligenter Systeme beschäftigt.',
            'programming': 'Programmierung ist der Prozess der Erstellung von Computerprogrammen durch das Schreiben von Code.',
            'web': 'Webentwicklung umfasst die Erstellung von Websites und Webanwendungen für das Internet.',
            'python': 'Python ist eine vielseitige, interpretierte Programmiersprache, die für ihre Lesbarkeit bekannt ist.',
            'javascript': 'JavaScript ist eine dynamische Programmiersprache, die hauptsächlich für Webentwicklung verwendet wird.',
            'react': 'React ist eine JavaScript-Bibliothek zur Erstellung von Benutzeroberflächen, entwickelt von Facebook.'
        }
        
        message_lower = message.lower()
        
        for keyword, description in topic_keywords.items():
            if keyword in message_lower:
                return f"""📚 **Recherche-Ergebnis zu "{keyword.title()}"**

{description}

**Wichtige Punkte:**
• Weit verbreitet in der modernen Softwareentwicklung
• Unterstützt von einer großen Community
• Viele Lernressourcen verfügbar
• Kontinuierliche Weiterentwicklung

**Empfehlungen:**
- Beginnen Sie mit grundlegenden Konzepten
- Nutzen Sie praktische Projekte zum Lernen
- Verwenden Sie offizielle Dokumentation
- Treten Sie relevanten Communities bei

Möchten Sie spezifischere Informationen zu einem bestimmten Aspekt?"""
        
        return """📚 **Recherche-Information**

Basierend auf Ihrer Anfrage kann ich Ihnen folgende Informationen bereitstellen:

• **Fachbereich**: Ihr Thema gehört zu einem wichtigen Wissensgebiet
• **Relevanz**: Aktuell und praxisrelevant
• **Anwendung**: Vielseitige Einsatzmöglichkeiten
• **Lernkurve**: Mit der richtigen Herangehensweise gut erlernbar

**Empfohlene nächste Schritte:**
1. Vertiefen Sie spezifische Aspekte
2. Suchen Sie nach praktischen Beispielen
3. Experimentieren Sie mit eigenen Projekten

Haben Sie spezifische Fragen zu diesem Thema?"""
    
    def simulate_ai_response(self, message: str, intent: Dict[str, Any]) -> str:
        """Main method to simulate AI response based on message and intent"""
        analysis = self.analyze_request(message)
        
        if analysis['is_code_request']:
            language = analysis['language_detected']
            return self.generate_code_response(message, language)
        
        if analysis['is_research_request']:
            return self._generate_research_response(message)
        
        return self.generate_conversational_response(message, analysis)

# Global instance for reuse
offline_simulator = OfflineAISimulator()