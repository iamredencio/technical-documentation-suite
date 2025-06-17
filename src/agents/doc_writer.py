"""
Documentation Writer Agent - Generates documentation from code analysis
"""

from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent, Message
from ..services.ai_service import ai_service

class DocumentationWriterAgent(BaseAgent):
    """Agent responsible for writing documentation"""
    
    def __init__(self, agent_id: str):
        super().__init__(agent_id, "DocumentationWriter")
        self.templates = self._load_templates()
        self.supported_formats = ["markdown", "html", "rst"]
    
    async def handle_message(self, message: Message) -> Optional[Message]:
        """Handle incoming messages"""
        if message.type == "generate_documentation":
            return await self._generate_documentation(message)
        elif message.type == "format_documentation":
            return await self._format_documentation(message)
        else:
            self.logger.warning(f"Unknown message type: {message.type}")
            return None
    
    def _load_templates(self) -> Dict[str, str]:
        """Load documentation templates"""
        return {
            "api_reference": """
# {title} API Reference

## Overview
{overview}

## Endpoints
{endpoints}

## Models
{models}

## Examples
{examples}
            """,
            "class_documentation": """
## {class_name}

{description}

### Methods
{methods}

### Usage
```python
{usage_example}
```
            """,
            "function_documentation": """
### {function_name}

{description}

**Parameters:**
{parameters}

**Returns:**
{returns}

**Example:**
```python
{example}
```
            """
        }
    
    async def _generate_documentation(self, message: Message) -> Message:
        """Generate documentation from analysis data using AI"""
        analysis_data = message.data.get("analysis", {})
        output_format = message.data.get("format", "markdown")
        target_audience = message.data.get("audience", "developers")
        
        self.logger.info(f"Generating AI-powered documentation for {analysis_data.get('project_id', 'unknown')}")
        
        try:
            # Use AI service for real documentation generation
            full_documentation = await ai_service.generate_documentation(analysis_data, target_audience)
            
            # If AI-generated content is very short, supplement with traditional sections
            if len(full_documentation) < 500:
                self.logger.info("AI response too short, supplementing with traditional documentation")
                traditional_sections = []
                
                # Add traditional sections as backup
                if "repository_url" in analysis_data:
                    traditional_sections.append(self._generate_overview_section(analysis_data))
                
                if "api_endpoints" in analysis_data:
                    traditional_sections.append(self._generate_api_section(analysis_data["api_endpoints"]))
                
                if "classes" in analysis_data:
                    traditional_sections.append(self._generate_classes_section(analysis_data["classes"]))
                
                if "functions" in analysis_data:
                    traditional_sections.append(self._generate_functions_section(analysis_data["functions"]))
                
                if "dependencies" in analysis_data:
                    traditional_sections.append(self._generate_dependencies_section(analysis_data["dependencies"]))
                
                # Combine AI and traditional content
                traditional_content = "\n\n".join(traditional_sections)
                full_documentation = f"{full_documentation}\n\n{traditional_content}"
            
            # Apply formatting
            if output_format == "html":
                full_documentation = self._convert_to_html(full_documentation)
            elif output_format == "rst":
                full_documentation = self._convert_to_rst(full_documentation)
            
            return Message(
                type="documentation_generated",
                data={
                    "content": full_documentation,
                    "format": output_format,
                    "ai_generated": ai_service.enabled,
                    "word_count": len(full_documentation.split()),
                    "target_audience": target_audience
                },
                sender=self.agent_id,
                recipient=message.sender
            )
            
        except Exception as e:
            self.logger.error(f"Documentation generation failed: {e}")
            # Fallback to traditional generation
            return await self._generate_traditional_documentation(message)
    
    def _generate_overview_section(self, analysis_data: Dict[str, Any]) -> str:
        """Generate project overview section"""
        project_id = analysis_data.get("project_id", "Unknown Project")
        repo_url = analysis_data.get("repository_url", "")
        file_count = analysis_data.get("file_count", 0)
        lines_of_code = analysis_data.get("lines_of_code", 0)
        
        return f"""# {project_id}

## Project Overview

This project is a software repository with {file_count} files containing approximately {lines_of_code} lines of code.

**Repository:** {repo_url}

## Quick Stats
- **Files:** {file_count}
- **Lines of Code:** {lines_of_code}
- **Primary Language:** Python
"""
    
    def _generate_api_section(self, endpoints: List[Dict[str, Any]]) -> str:
        """Generate API documentation section"""
        if not endpoints:
            return ""
        
        section = "## API Endpoints\n\n"
        
        for endpoint in endpoints:
            method = endpoint.get("method", "GET")
            path = endpoint.get("path", "/")
            function = endpoint.get("function", "unknown")
            description = endpoint.get("description", f"Handles {method} requests to {path}")
            
            section += f"""### {method} {path}

**Function:** `{function}`

{description}

"""
        
        return section
    
    def _generate_classes_section(self, classes: List[Dict[str, Any]]) -> str:
        """Generate class documentation section"""
        if not classes:
            return ""
        
        section = "## Classes\n\n"
        
        for cls in classes:
            name = cls.get("name", "Unknown")
            docstring = cls.get("docstring", "No description available")
            methods = cls.get("methods", [])
            inheritance = cls.get("inheritance", [])
            
            section += f"""### {name}

{docstring}

"""
            if inheritance:
                section += f"**Inherits from:** {', '.join(inheritance)}\n\n"
            
            if methods:
                section += "**Methods:**\n"
                for method in methods:
                    section += f"- `{method}`\n"
                section += "\n"
        
        return section
    
    def _generate_functions_section(self, functions: List[Dict[str, Any]]) -> str:
        """Generate function documentation section"""
        if not functions:
            return ""
        
        section = "## Functions\n\n"
        
        for func in functions:
            name = func.get("name", "unknown")
            docstring = func.get("docstring", "No description available")
            parameters = func.get("parameters", [])
            return_type = func.get("return_type", "Any")
            
            section += f"""### {name}

{docstring}

**Parameters:** {', '.join(parameters)}
**Returns:** {return_type}

"""
        
        return section
    
    async def _generate_traditional_documentation(self, message: Message) -> Message:
        """Fallback to traditional documentation generation"""
        analysis_data = message.data.get("analysis", {})
        output_format = message.data.get("format", "markdown")
        target_audience = message.data.get("audience", "developers")
        
        self.logger.info("Using traditional documentation generation (fallback)")
        
        # Generate different sections based on analysis
        sections = []
        
        # Project overview
        if "repository_url" in analysis_data:
            sections.append(self._generate_overview_section(analysis_data))
        
        # API documentation
        if "api_endpoints" in analysis_data:
            sections.append(self._generate_api_section(analysis_data["api_endpoints"]))
        
        # Class documentation
        if "classes" in analysis_data:
            sections.append(self._generate_classes_section(analysis_data["classes"]))
        
        # Function documentation  
        if "functions" in analysis_data:
            sections.append(self._generate_functions_section(analysis_data["functions"]))
        
        # Dependencies
        if "dependencies" in analysis_data:
            sections.append(self._generate_dependencies_section(analysis_data["dependencies"]))
        
        # Combine all sections
        full_documentation = "\n\n".join(sections)
        
        # Apply formatting
        if output_format == "html":
            full_documentation = self._convert_to_html(full_documentation)
        elif output_format == "rst":
            full_documentation = self._convert_to_rst(full_documentation)
        
        return Message(
            type="documentation_generated",
            data={
                "content": full_documentation,
                "format": output_format,
                "ai_generated": False,
                "sections": len(sections),
                "word_count": len(full_documentation.split()),
                "target_audience": target_audience
            },
            sender=self.agent_id,
            recipient=message.sender
        )
    
    def _generate_dependencies_section(self, dependencies: List[Dict[str, Any]]) -> str:
        """Generate dependencies section"""
        if not dependencies:
            return ""
        
        section = "## Dependencies\n\n"
        
        runtime_deps = [d for d in dependencies if d.get("type") == "runtime"]
        dev_deps = [d for d in dependencies if d.get("type") == "development"]
        
        if runtime_deps:
            section += "### Runtime Dependencies\n\n"
            for dep in runtime_deps:
                name = dep.get("name")
                version = dep.get("version", "latest")
                section += f"- **{name}** ({version})\n"
            section += "\n"
        
        if dev_deps:
            section += "### Development Dependencies\n\n"
            for dep in dev_deps:
                name = dep.get("name")
                version = dep.get("version", "latest")
                section += f"- **{name}** ({version})\n"
            section += "\n"
        
        return section
    
    async def _format_documentation(self, message: Message) -> Message:
        """Format documentation for different outputs"""
        content = message.data.get("content", "")
        target_format = message.data.get("target_format", "markdown")
        
        if target_format == "html":
            formatted_content = self._convert_to_html(content)
        elif target_format == "rst":
            formatted_content = self._convert_to_rst(content)
        else:
            formatted_content = content  # Keep as markdown
        
        return Message(
            type="documentation_formatted",
            data={
                "content": formatted_content,
                "format": target_format
            },
            sender=self.agent_id,
            recipient=message.sender
        )
    
    def _convert_to_html(self, markdown_content: str) -> str:
        """Convert markdown to HTML (basic implementation)"""
        # Simple markdown to HTML conversion
        html_content = markdown_content
        html_content = html_content.replace("# ", "<h1>").replace("\n", "</h1>\n", 1)
        html_content = html_content.replace("## ", "<h2>").replace("\n", "</h2>\n", 1)
        html_content = html_content.replace("### ", "<h3>").replace("\n", "</h3>\n", 1)
        html_content = f"<html><body>{html_content}</body></html>"
        return html_content
    
    def _convert_to_rst(self, markdown_content: str) -> str:
        """Convert markdown to reStructuredText (basic implementation)"""
        # Simple markdown to RST conversion
        rst_content = markdown_content
        rst_content = rst_content.replace("# ", "").replace("\n", "\n" + "="*50 + "\n", 1)
        rst_content = rst_content.replace("## ", "").replace("\n", "\n" + "-"*30 + "\n", 1)
        return rst_content 