import re
from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentTask, AgentStatus, AgentCapability
import os
import anthropic

class DataAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Data Agent",
            description="Specialized in data analysis, visualization, and statistical processing using Claude AI",
            capabilities=[
                AgentCapability.DATA_ANALYSIS
            ]
        )
        self.ai_model = "claude"
        
    def can_handle_task(self, task_description: str, context: Dict[str, Any]) -> float:
        """Evaluate if this agent can handle the task"""
        data_keywords = [
            'data', 'analysis', 'analyze', 'statistics', 'statistical', 'chart',
            'graph', 'visualization', 'visualize', 'plot', 'dataset', 'csv',
            'excel', 'pandas', 'numpy', 'matplotlib', 'seaborn', 'plotly',
            'daten', 'analyse', 'statistik', 'diagramm', 'grafik', 'visualisierung',
            'correlation', 'regression', 'clustering', 'classification', 'prediction',
            'machine learning', 'ml', 'data science', 'insights', 'trends',
            'metrics', 'kpi', 'dashboard', 'report', 'summary'
        ]
        
        description_lower = task_description.lower()
        matches = sum(1 for keyword in data_keywords if keyword in description_lower)
        confidence = min(matches / 3, 1.0)
        
        # Boost confidence for data-specific terms
        if any(term in description_lower for term in ['analyze data', 'data analysis', 'visualization', 'statistics']):
            confidence += 0.4
        
        # Boost if file extension suggests data files
        if context.get('file_extension') in ['.csv', '.xlsx', '.json', '.parquet']:
            confidence += 0.3
            
        # Boost for data science libraries mentioned
        if any(lib in description_lower for lib in ['pandas', 'numpy', 'matplotlib', 'seaborn', 'plotly']):
            confidence += 0.3
            
        return min(confidence, 1.0)
    
    async def execute_task(self, task: AgentTask) -> AgentTask:
        """Execute data analysis tasks using Claude AI"""
        try:
            task.status = AgentStatus.THINKING
            await self.update_progress(task, 0.1, "Initializing Claude for data analysis")
            
            # Get Claude client
            api_key = os.environ.get('ANTHROPIC_API_KEY')
            if not api_key:
                raise Exception("Anthropic API key not configured")
            
            client = anthropic.AsyncAnthropic(api_key=api_key)
            
            # Detect language for system message
            language = task.input_data.get('language', 'english')
            system_message = self._get_system_message(language)
            
            await self.update_progress(task, 0.3, "Analyzing data requirements")
            
            task_type = self._identify_data_task_type(task.description)
            enhanced_prompt = self._create_data_prompt(task.description, task_type, task.input_data)
            
            await self.update_progress(task, 0.6, f"Executing {task_type} with Claude")
            
            # Make API call to Claude 4 Sonnet (latest)
            response = await client.messages.create(
                model="claude-3-5-sonnet-20250110",
                max_tokens=4000,
                temperature=0.7,
                system=system_message,
                messages=[
                    {"role": "user", "content": enhanced_prompt}
                ]
            )
            
            await self.update_progress(task, 0.8, "Processing data analysis results")
            
            # Structure the data result
            content = response.content[0].text
            result = self._process_data_response(content, task_type, task.input_data)
            task.result = result
            
            task.status = AgentStatus.COMPLETED
            await self.update_progress(task, 1.0, "Data analysis completed successfully")
            
        except Exception as e:
            task.status = AgentStatus.ERROR
            task.error_message = f"Data analysis failed: {str(e)}"
            self.logger.error(f"Data agent error: {e}")
            
        return task
    
    def _get_system_message(self, language: str) -> str:
        """Get system message in appropriate language"""
        messages = {
            'german': "Du bist ein erfahrener Datenanalyst und Data Scientist. Du hilfst bei Datenanalyse, Visualisierung und statistischen Auswertungen. Liefere präzise Analysen mit klaren Erklärungen und praktischen Code-Beispielen.",
            'english': "You are an experienced data analyst and data scientist. You help with data analysis, visualization, and statistical evaluations. Provide precise analyses with clear explanations and practical code examples.",
            'spanish': "Eres un analista de datos experimentado y científico de datos. Ayudas con análisis de datos, visualización y evaluaciones estadísticas. Proporciona análisis precisos con explicaciones claras y ejemplos de código prácticos.",
            'french': "Vous êtes un analyste de données expérimenté et data scientist. Vous aidez avec l'analyse de données, la visualisation et les évaluations statistiques. Fournissez des analyses précises avec des explications claires et des exemples de code pratiques.",
            'italian': "Sei un analista di dati esperto e data scientist. Aiuti con analisi dei dati, visualizzazione e valutazioni statistiche. Fornisci analisi precise con spiegazioni chiare ed esempi di codice pratici."
        }
        return messages.get(language, messages['english'])
    
    def _identify_data_task_type(self, description: str) -> str:
        """Identify the type of data analysis task"""
        description_lower = description.lower()
        
        if any(word in description_lower for word in ['visualize', 'plot', 'chart', 'graph', 'visualization']):
            return "data_visualization"
        elif any(word in description_lower for word in ['statistics', 'statistical', 'correlation', 'regression']):
            return "statistical_analysis"
        elif any(word in description_lower for word in ['clean', 'preprocessing', 'prepare', 'transform']):
            return "data_preprocessing"
        elif any(word in description_lower for word in ['predict', 'prediction', 'model', 'machine learning', 'ml']):
            return "predictive_analysis"
        elif any(word in description_lower for word in ['explore', 'exploratory', 'eda', 'summary']):
            return "exploratory_analysis"
        elif any(word in description_lower for word in ['dashboard', 'report', 'insights']):
            return "reporting"
        else:
            return "general_analysis"
    
    def _create_data_prompt(self, description: str, task_type: str, input_data: Dict[str, Any]) -> str:
        """Create an enhanced prompt for data analysis tasks"""
        language = input_data.get('language', 'english')
        data_format = input_data.get('data_format', 'csv')
        tools_preference = input_data.get('tools', 'python')
        
        base_prompt = f"{description}\n\n"
        
        if task_type == "data_visualization":
            base_prompt += f"""
Create {tools_preference} code for data visualization that includes:
- Appropriate chart types for the data
- Clear labels and titles
- Professional styling
- Interactive features (if using plotly)
- Multiple visualization options
- Code to save/export charts
"""
        elif task_type == "statistical_analysis":
            base_prompt += f"""
Perform statistical analysis using {tools_preference} that includes:
- Descriptive statistics
- Correlation analysis
- Hypothesis testing (if applicable)
- Confidence intervals
- Statistical significance testing
- Clear interpretation of results
"""
        elif task_type == "data_preprocessing":
            base_prompt += f"""
Create {tools_preference} code for data preprocessing that includes:
- Data loading and inspection
- Missing value handling
- Outlier detection and treatment
- Data type conversions
- Feature engineering
- Data validation
"""
        elif task_type == "predictive_analysis":
            base_prompt += f"""
Create {tools_preference} code for predictive analysis that includes:
- Feature selection and engineering
- Model selection and training
- Cross-validation
- Performance evaluation
- Model interpretation
- Prediction examples
"""
        elif task_type == "exploratory_analysis":
            base_prompt += f"""
Perform exploratory data analysis using {tools_preference} that includes:
- Data overview and structure
- Summary statistics
- Distribution analysis
- Missing value analysis
- Correlation analysis
- Key insights and patterns
"""
        elif task_type == "reporting":
            base_prompt += f"""
Create a comprehensive data report that includes:
- Executive summary
- Key findings and insights
- Supporting visualizations
- Statistical evidence
- Recommendations
- Appendices with detailed results
"""
        
        base_prompt += f"\nData format: {data_format}"
        base_prompt += f"\nPreferred tools: {tools_preference}"
        base_prompt += "\nProvide complete, runnable code with clear explanations."
        
        return base_prompt
    
    def _process_data_response(self, content: str, task_type: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process the AI response into structured format"""
        # Extract code blocks from response
        code_blocks = self._extract_code_blocks(content)
        
        result = {
            "type": task_type,
            "analysis_content": content,
            "code_blocks": code_blocks,
            "main_code": code_blocks[0] if code_blocks else "",
            "ai_model_used": "claude",
            "insights": self._extract_insights(content),
            "recommendations": self._extract_recommendations(content),
            "tools_used": input_data.get('tools', 'python')
        }
        
        # Add task-specific fields
        if task_type == "data_visualization":
            result.update({
                "chart_types": self._extract_chart_types(content),
                "libraries_used": self._extract_libraries(content)
            })
        elif task_type == "statistical_analysis":
            result.update({
                "statistical_tests": self._extract_statistical_tests(content),
                "p_values": self._extract_p_values(content),
                "confidence_intervals": self._extract_confidence_intervals(content)
            })
        elif task_type == "predictive_analysis":
            result.update({
                "models_used": self._extract_models(content),
                "performance_metrics": self._extract_metrics(content),
                "feature_importance": self._extract_feature_importance(content)
            })
        
        return result
    
    def _extract_code_blocks(self, response: str) -> List[str]:
        """Extract code blocks from the response"""
        import re
        code_pattern = r'```(?:\w+)?\n(.*?)\n```'
        matches = re.findall(code_pattern, response, re.DOTALL)
        return matches
    
    def _extract_insights(self, response: str) -> List[str]:
        """Extract key insights from the analysis"""
        insights = []
        lines = response.split('\n')
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['insight', 'finding', 'observation', 'key point', 'important']):
                insights.append(line.strip())
        
        return insights[:10]
    
    def _extract_recommendations(self, response: str) -> List[str]:
        """Extract recommendations from the analysis"""
        recommendations = []
        lines = response.split('\n')
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['recommend', 'suggest', 'should', 'consider', 'advice']):
                recommendations.append(line.strip())
        
        return recommendations[:10]
    
    def _extract_chart_types(self, response: str) -> List[str]:
        """Extract chart types mentioned in visualization response"""
        chart_types = []
        chart_keywords = ['bar chart', 'line chart', 'scatter plot', 'histogram', 'box plot', 'heatmap', 'pie chart']
        
        response_lower = response.lower()
        for chart_type in chart_keywords:
            if chart_type in response_lower:
                chart_types.append(chart_type)
        
        return chart_types
    
    def _extract_libraries(self, response: str) -> List[str]:
        """Extract Python libraries mentioned in response"""
        libraries = []
        lib_keywords = ['matplotlib', 'seaborn', 'plotly', 'pandas', 'numpy', 'scipy', 'sklearn']
        
        response_lower = response.lower()
        for lib in lib_keywords:
            if lib in response_lower:
                libraries.append(lib)
        
        return libraries
    
    def _extract_statistical_tests(self, response: str) -> List[str]:
        """Extract statistical tests mentioned in response"""
        tests = []
        test_keywords = ['t-test', 'chi-square', 'anova', 'correlation', 'regression', 'mann-whitney']
        
        response_lower = response.lower()
        for test in test_keywords:
            if test in response_lower:
                tests.append(test)
        
        return tests
    
    def _extract_p_values(self, response: str) -> List[float]:
        """Extract p-values from statistical analysis"""
        import re
        p_values = []
        
        # Look for p-value patterns
        p_value_pattern = r'p[-\s]*value[s]?[:=\s]+(\d*\.?\d+)'
        matches = re.findall(p_value_pattern, response, re.IGNORECASE)
        
        for match in matches:
            try:
                p_values.append(float(match))
            except ValueError:
                continue
        
        return p_values[:5]  # Return max 5 p-values
    
    def _extract_confidence_intervals(self, response: str) -> List[str]:
        """Extract confidence intervals from response"""
        import re
        intervals = []
        
        # Look for confidence interval patterns
        ci_pattern = r'(\d+%?\s*confidence\s*interval[s]?[:\s]+[\[\(]?[\d\.\-\s,]+[\]\)]?)'
        matches = re.findall(ci_pattern, response, re.IGNORECASE)
        
        return matches[:5]  # Return max 5 confidence intervals
    
    def _extract_models(self, response: str) -> List[str]:
        """Extract machine learning models mentioned in response"""
        models = []
        model_keywords = ['linear regression', 'logistic regression', 'random forest', 'svm', 'neural network', 'xgboost', 'decision tree']
        
        response_lower = response.lower()
        for model in model_keywords:
            if model in response_lower:
                models.append(model)
        
        return models
    
    def _extract_metrics(self, response: str) -> Dict[str, float]:
        """Extract performance metrics from response"""
        import re
        metrics = {}
        
        # Common metrics patterns
        metric_patterns = {
            'accuracy': r'accuracy[:=\s]+(\d*\.?\d+)',
            'precision': r'precision[:=\s]+(\d*\.?\d+)',
            'recall': r'recall[:=\s]+(\d*\.?\d+)',
            'f1_score': r'f1[-\s]*score[:=\s]+(\d*\.?\d+)',
            'r2_score': r'r2[-\s]*score[:=\s]+(\d*\.?\d+)',
            'rmse': r'rmse[:=\s]+(\d*\.?\d+)'
        }
        
        for metric_name, pattern in metric_patterns.items():
            matches = re.findall(pattern, response, re.IGNORECASE)
            if matches:
                try:
                    metrics[metric_name] = float(matches[0])
                except ValueError:
                    continue
        
        return metrics
    
    def _extract_feature_importance(self, response: str) -> List[str]:
        """Extract feature importance information from response"""
        importance = []
        lines = response.split('\n')
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['feature importance', 'important feature', 'top feature']):
                importance.append(line.strip())
        
        return importance[:10]