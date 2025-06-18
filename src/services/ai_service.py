"""
AI Service - Real AI-powered documentation generation using Gemini API
"""

import os
import google.generativeai as genai
from typing import Dict, Any, List, Optional
import logging

class AIService:
    """Service for AI-powered documentation generation using Google Gemini"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.api_key = os.getenv('GEMINI_API_KEY')
        
        if not self.api_key:
            self.logger.warning("GEMINI_API_KEY not found in environment variables. AI features will be disabled.")
            self.enabled = False
            return
        
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-pro')
            self.enabled = True
            self.logger.info("Gemini AI service initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Gemini AI service: {e}")
            self.enabled = False

    async def generate_documentation(self, analysis_data: Dict[str, Any], target_audience: str = "developers") -> str:
        """Generate comprehensive documentation using AI"""
        if not self.enabled:
            return self._fallback_documentation(analysis_data)
        
        try:
            prompt = self._build_documentation_prompt(analysis_data, target_audience)
            response = await self._generate_text(prompt)
            return response
        except Exception as e:
            self.logger.error(f"AI documentation generation failed: {e}")
            return self._fallback_documentation(analysis_data)

    async def generate_api_documentation(self, endpoints: List[Dict[str, Any]]) -> str:
        """Generate API documentation for endpoints"""
        if not self.enabled or not endpoints:
            return self._fallback_api_docs(endpoints)
        
        try:
            prompt = f"""
            Generate comprehensive API documentation for the following endpoints:
            
            {self._format_endpoints_for_prompt(endpoints)}
            
            Include:
            - Clear descriptions for each endpoint
            - Parameter details and types
            - Response formats and examples
            - Error handling information
            - Usage examples with curl commands
            
            Format as professional markdown documentation.
            """
            
            response = await self._generate_text(prompt)
            return response
        except Exception as e:
            self.logger.error(f"AI API documentation generation failed: {e}")
            return self._fallback_api_docs(endpoints)

    async def generate_code_explanation(self, code_analysis: Dict[str, Any]) -> str:
        """Generate explanations for code structure and functions"""
        if not self.enabled:
            return self._fallback_code_explanation(code_analysis)
        
        try:
            prompt = f"""
            Analyze and explain the following code structure:
            
            Functions: {code_analysis.get('functions', [])}
            Classes: {code_analysis.get('classes', [])}
            Dependencies: {code_analysis.get('dependencies', [])}
            
            Provide:
            - Overview of the codebase architecture
            - Explanation of key functions and their purposes
            - Class hierarchy and relationships
            - Dependency analysis and recommendations
            
            Write in clear, technical language suitable for developers.
            """
            
            response = await self._generate_text(prompt)
            return response
        except Exception as e:
            self.logger.error(f"AI code explanation generation failed: {e}")
            return self._fallback_code_explanation(code_analysis)

    async def improve_documentation_quality(self, existing_docs: str, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use AI to assess and improve documentation quality"""
        if not self.enabled:
            return {
                "score": 0.75,
                "suggestions": ["Add more examples", "Improve clarity"],
                "improved_content": existing_docs
            }
        
        try:
            prompt = f"""
            Review and improve the following technical documentation:
            
            {existing_docs}
            
            Based on the code analysis: {analysis_data}
            
            Provide:
            1. A quality score (0-1.0)
            2. Specific improvement suggestions
            3. Improved version of the documentation
            
            Focus on clarity, completeness, accuracy, and usefulness.
            Format response as JSON with keys: score, suggestions, improved_content
            """
            
            response = await self._generate_text(prompt)
            
            # Try to parse JSON response, fallback to structured format
            try:
                import json
                result = json.loads(response)
                return result
            except:
                # Fallback to basic scoring
                return {
                    "score": 0.8,
                    "suggestions": ["Review AI-generated improvements"],
                    "improved_content": response
                }
                
        except Exception as e:
            self.logger.error(f"AI quality improvement failed: {e}")
            return {
                "score": 0.75,
                "suggestions": ["Manual review recommended"],
                "improved_content": existing_docs
            }

    async def _generate_text(self, prompt: str) -> str:
        """Generate text using Gemini API"""
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            self.logger.error(f"Gemini API call failed: {e}")
            raise

    def _build_documentation_prompt(self, analysis_data: Dict[str, Any], target_audience: str) -> str:
        """Build a comprehensive prompt for documentation generation"""
        repo_url = analysis_data.get('repository_url', 'Unknown Repository')
        project_id = analysis_data.get('project_id', 'Unknown Project')
        file_count = analysis_data.get('file_count', 0)
        lines_of_code = analysis_data.get('lines_of_code', 0)
        functions = analysis_data.get('functions', [])
        classes = analysis_data.get('classes', [])
        dependencies = analysis_data.get('dependencies', [])
        
        prompt = f"""
        Generate comprehensive technical documentation for this software project using proper markdown formatting with excellent spacing and readability:
        
        **Project Information:**
        - Name: {project_id}
        - Repository: {repo_url}
        - Files: {file_count}
        - Lines of Code: {lines_of_code}
        - Target Audience: {target_audience}
        
        **Code Analysis:**
        - Functions: {len(functions)} functions found
        - Classes: {len(classes)} classes found
        - Dependencies: {dependencies}
        
        **Key Functions:**
        {self._format_functions_for_prompt(functions[:10])}  # Limit to top 10
        
        **Key Classes:**
        {self._format_classes_for_prompt(classes[:10])}  # Limit to top 10
        
        **CRITICAL FORMATTING REQUIREMENTS:**
        - Use proper markdown headers (# ## ### ####)
        - Add TWO blank lines between major sections
        - Add ONE blank line between subsections and paragraphs
        - Use code blocks with language specification ```python, ```bash, etc.
        - Include bullet points and numbered lists where appropriate
        - Add horizontal rules (---) to separate major sections
        - Use **bold** and *italic* for emphasis appropriately
        - Include tables for structured data when applicable
        - Ensure proper spacing around code blocks
        - Use proper indentation for nested lists
        
        Generate a complete, well-formatted documentation that includes:
        
        1. **Project Overview** - Clear description of what the project does
        
        2. **Installation & Setup** - Step-by-step installation instructions
        
        3. **Architecture Overview** - High-level system design and components
        
        4. **API Reference** - If applicable, document main interfaces with examples
        
        5. **Usage Examples** - Practical code examples with proper formatting
        
        6. **Key Functions & Classes** - Document important code elements with descriptions
        
        7. **Dependencies** - Required packages and their purposes
        
        8. **Configuration** - Environment variables and settings
        
        9. **Contributing** - How others can contribute to the project
        
        10. **Troubleshooting** - Common issues and solutions
        
        Write professional, clear documentation in Markdown format with excellent spacing and readability.
        Make it suitable for {target_audience}.
        Be comprehensive but well-organized.
        Include practical code examples with proper syntax highlighting.
        Ensure every section has proper spacing and is easy to read.
        """
        
        return prompt

    def _format_functions_for_prompt(self, functions: List[Dict[str, Any]]) -> str:
        """Format functions for AI prompt"""
        if not functions:
            return "No functions found"
        
        formatted = []
        for func in functions:
            name = func.get('name', 'unknown')
            params = func.get('parameters', [])
            docstring = func.get('docstring', 'No description')
            formatted.append(f"- {name}({', '.join(params)}): {docstring}")
        
        return '\n'.join(formatted)

    def _format_classes_for_prompt(self, classes: List[Dict[str, Any]]) -> str:
        """Format classes for AI prompt"""
        if not classes:
            return "No classes found"
        
        formatted = []
        for cls in classes:
            name = cls.get('name', 'unknown')
            methods = cls.get('methods', [])
            docstring = cls.get('docstring', 'No description')
            formatted.append(f"- {name}: {docstring} (Methods: {', '.join(methods)})")
        
        return '\n'.join(formatted)

    def _format_endpoints_for_prompt(self, endpoints: List[Dict[str, Any]]) -> str:
        """Format API endpoints for AI prompt"""
        formatted = []
        for endpoint in endpoints:
            method = endpoint.get('method', 'GET')
            path = endpoint.get('path', '/')
            function = endpoint.get('function', 'unknown')
            formatted.append(f"- {method} {path} -> {function}")
        
        return '\n'.join(formatted)

    def _fallback_documentation(self, analysis_data: Dict[str, Any]) -> str:
        """Fallback documentation when AI is not available"""
        project_id = analysis_data.get('project_id', 'Unknown Project')
        repo_url = analysis_data.get('repository_url', '')
        file_count = analysis_data.get('file_count', 0)
        lines_of_code = analysis_data.get('lines_of_code', 0)
        
        return f"""# {project_id}

## Project Overview

This is a software project with {file_count} files containing approximately {lines_of_code} lines of code.

**Repository:** {repo_url}

## Quick Stats
- **Files:** {file_count}
- **Lines of Code:** {lines_of_code}
- **Primary Language:** Python

## Installation

```bash
# Clone the repository
git clone {repo_url}

# Install dependencies
pip install -r requirements.txt
```

## Usage

Please refer to the project's README file for detailed usage instructions.

---

*Note: This documentation was generated using fallback mode. For AI-enhanced documentation, please configure the GEMINI_API_KEY environment variable.*
"""

    def _fallback_api_docs(self, endpoints: List[Dict[str, Any]]) -> str:
        """Fallback API documentation"""
        if not endpoints:
            return "## API Endpoints\n\nNo API endpoints found."
        
        docs = "## API Endpoints\n\n"
        for endpoint in endpoints:
            method = endpoint.get('method', 'GET')
            path = endpoint.get('path', '/')
            function = endpoint.get('function', 'unknown')
            docs += f"### {method} {path}\n\n**Handler:** `{function}`\n\n"
        
        return docs

    def _fallback_code_explanation(self, code_analysis: Dict[str, Any]) -> str:
        """Fallback code explanation"""
        functions = code_analysis.get('functions', [])
        classes = code_analysis.get('classes', [])
        
        explanation = "## Code Structure\n\n"
        
        if functions:
            explanation += f"### Functions ({len(functions)} found)\n\n"
            for func in functions[:5]:  # Limit to first 5
                name = func.get('name', 'unknown')
                explanation += f"- **{name}**: {func.get('docstring', 'No description')}\n"
        
        if classes:
            explanation += f"\n### Classes ({len(classes)} found)\n\n"
            for cls in classes[:5]:  # Limit to first 5
                name = cls.get('name', 'unknown')
                explanation += f"- **{name}**: {cls.get('docstring', 'No description')}\n"
        
        return explanation

# Global AI service instance
ai_service = AIService() 