"""
AI Service - Real AI-powered documentation generation using Gemini API
"""

import os
import logging
import google.generativeai as genai
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class AIService:
    """Service for AI-powered documentation generation using Google Gemini"""
    
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.model = None
        
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not found in environment variables. AI features will be disabled.")
            return
        
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-pro')
            logger.info("Gemini AI service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini AI service: {e}")
            self.model = None
    
    def is_available(self) -> bool:
        """Check if AI service is available"""
        return self.model is not None
    
    async def generate_documentation(self, analysis_data: Dict[str, Any], target_audience: str = "developers") -> str:
        """Generate comprehensive documentation using AI"""
        if not self.is_available():
            logger.warning("AI service not available, using fallback documentation")
            return self._generate_fallback_documentation(analysis_data)
        
        try:
            prompt = self._create_documentation_prompt(analysis_data, target_audience)
            
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                logger.info("AI documentation generated successfully")
                return response.text
            else:
                logger.warning("AI service returned empty response, using fallback")
                return self._generate_fallback_documentation(analysis_data)
                
        except Exception as e:
            logger.error(f"AI documentation generation failed: {e}")
            return self._generate_fallback_documentation(analysis_data)
    
    async def translate_content(self, content: str, target_language: Dict[str, str], context: Dict[str, Any] = None) -> str:
        """Translate content to target language using AI"""
        if not self.is_available():
            logger.warning("AI service not available for translation")
            return f"Translation to {target_language.get('name', 'Unknown')} not available. Original content:\n\n{content}"
        
        try:
            prompt = self._create_translation_prompt(content, target_language, context)
            
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                logger.info(f"Translation to {target_language.get('name')} completed successfully")
                return response.text
            else:
                logger.warning(f"Translation to {target_language.get('name')} failed, returning original")
                return content
                
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return content
    
    def _generate_text(self, prompt: str) -> Optional[str]:
        """Generate text using Gemini API"""
        if not self.is_available():
            return None
        
        try:
            response = self.model.generate_content(prompt)
            return response.text if response else None
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            return None
    
    def _create_documentation_prompt(self, analysis_data: Dict[str, Any], target_audience: str) -> str:
        """Create a comprehensive prompt for documentation generation"""
        
        project_name = analysis_data.get('project_id', 'Unknown Project')
        functions = analysis_data.get('functions', [])
        classes = analysis_data.get('classes', [])
        dependencies = analysis_data.get('dependencies', [])
        file_count = analysis_data.get('file_count', 0)
        lines_of_code = analysis_data.get('lines_of_code', 0)
        
        # Build prompt with proper structure
        prompt = f"""
Generate comprehensive technical documentation for the project "{project_name}".

PROJECT ANALYSIS DATA:
- Total Files: {file_count}
- Lines of Code: {lines_of_code}
- Functions: {len(functions)}
- Classes: {len(classes)}
- Dependencies: {len(dependencies)}

TARGET AUDIENCE: {target_audience}

REQUIREMENTS:
1. Create professional, well-structured documentation in Markdown format
2. Include proper headers with TWO blank lines between major sections
3. Add comprehensive code examples with language specification
4. Structure with these sections:
   - Project Overview
   - Installation Instructions  
   - Architecture Overview
   - API Reference (if applicable)
   - Usage Examples
   - Configuration
   - Development Setup
   - Testing
   - Troubleshooting
   - Contributing Guidelines

FORMATTING REQUIREMENTS:
- Use ## for main headers with TWO blank lines before each
- Use ### for subsections
- Include ```language code blocks for all examples
- Add clear, concise explanations suitable for {target_audience}
- Include practical examples and use cases
- Ensure consistent formatting throughout

PROJECT DETAILS:
"""

        # Add function details if available
        if functions:
            prompt += f"\nKEY FUNCTIONS ({len(functions)} total):\n"
            for i, func in enumerate(functions[:10]):  # Limit to 10 for prompt size
                if isinstance(func, dict):
                    func_name = func.get('name', f'function_{i+1}')
                    prompt += f"- {func_name}\n"
        
        # Add class details if available  
        if classes:
            prompt += f"\nKEY CLASSES ({len(classes)} total):\n"
            for i, cls in enumerate(classes[:10]):  # Limit to 10 for prompt size
                if isinstance(cls, dict):
                    class_name = cls.get('name', f'class_{i+1}')
                    prompt += f"- {class_name}\n"
        
        # Add dependency details if available
        if dependencies:
            prompt += f"\nKEY DEPENDENCIES ({len(dependencies)} total):\n"
            for i, dep in enumerate(dependencies[:15]):  # Limit to 15 for prompt size
                if isinstance(dep, dict):
                    dep_name = dep.get('name', f'dependency_{i+1}')
                    prompt += f"- {dep_name}\n"
        
        prompt += """

Generate complete, production-ready documentation that developers can immediately use to understand, install, configure, and contribute to this project. Focus on clarity, completeness, and practical utility.
"""
        
        return prompt
    
    def _create_translation_prompt(self, content: str, target_language: Dict[str, str], context: Dict[str, Any] = None) -> str:
        """Create prompt for content translation"""
        
        language_name = target_language.get('name', 'Unknown')
        language_code = target_language.get('code', 'unknown')
        
        prompt = f"""
Translate the following technical documentation to {language_name} ({language_code}).

TRANSLATION REQUIREMENTS:
1. Maintain all Markdown formatting exactly
2. Preserve all code blocks unchanged
3. Keep all URLs and links intact
4. Translate technical terms appropriately for {language_name} developers
5. Maintain professional, technical tone
6. Keep section headers clear and consistent
7. Preserve all examples and code snippets
8. Ensure cultural appropriateness for {language_name} speakers

CONTENT TO TRANSLATE:

{content}

Provide the complete translated documentation maintaining the exact same structure and formatting.
"""
        
        return prompt
    
    def _generate_fallback_documentation(self, analysis_data: Dict[str, Any]) -> str:
        """Generate fallback documentation when AI is not available"""
        
        project_name = analysis_data.get('project_id', 'Unknown Project')
        functions = analysis_data.get('functions', [])
        classes = analysis_data.get('classes', [])
        dependencies = analysis_data.get('dependencies', [])
        file_count = analysis_data.get('file_count', 0)
        lines_of_code = analysis_data.get('lines_of_code', 0)
        
        doc = f"""# {project_name}

## Project Overview

This is an automatically generated documentation for **{project_name}**.


## Project Statistics

- **Total Files**: {file_count}
- **Lines of Code**: {lines_of_code}  
- **Functions**: {len(functions)}
- **Classes**: {len(classes)}
- **Dependencies**: {len(dependencies)}


## Installation

```bash
# Clone the repository
git clone <repository-url>
cd {project_name.lower().replace(' ', '-')}

# Install dependencies
# (Add specific installation commands based on your project type)
```


## Architecture Overview

This project contains:

"""

        if functions:
            doc += f"""
### Functions ({len(functions)})

"""
            for i, func in enumerate(functions[:10]):
                if isinstance(func, dict):
                    func_name = func.get('name', f'function_{i+1}')
                    doc += f"- `{func_name}`\n"

        if classes:
            doc += f"""
### Classes ({len(classes)})

"""
            for i, cls in enumerate(classes[:10]):
                if isinstance(cls, dict):
                    class_name = cls.get('name', f'class_{i+1}')
                    doc += f"- `{class_name}`\n"

        if dependencies:
            doc += f"""
### Dependencies ({len(dependencies)})

"""
            for i, dep in enumerate(dependencies[:15]):
                if isinstance(dep, dict):
                    dep_name = dep.get('name', f'dependency_{i+1}')
                    doc += f"- `{dep_name}`\n"

        doc += """

## Usage

```python
# Add usage examples here
```


## Configuration

Configuration details will be added based on project analysis.


## Development

```bash
# Development setup commands
```


## Testing

```bash
# Testing commands
```


## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request


## License

Please check the project repository for license information.

---

*Note: This documentation was generated using fallback mode. For AI-enhanced documentation, please configure the GEMINI_API_KEY environment variable.*
"""
        
        return doc

# Global AI service instance
ai_service = AIService() 