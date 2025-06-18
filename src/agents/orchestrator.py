"""
All remaining agents for the Technical Documentation Suite
"""

from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent, Message
import json
import asyncio
import uuid
import logging
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

class DiagramGeneratorAgent(BaseAgent):
    """Agent responsible for generating diagrams"""
    
    def __init__(self, agent_id: str):
        super().__init__(agent_id, "DiagramGenerator")
        self.diagram_types = ["architecture", "sequence", "class", "component"]
    
    async def handle_message(self, message: Message) -> Optional[Message]:
        if message.type == "generate_diagram":
            return await self._generate_diagram(message)
        return None
    
    async def _generate_diagram(self, message: Message) -> Message:
        # Extract analysis data from message
        analysis_data = message.data.get("analysis", {})
        diagram_type = message.data.get("type", "architecture")
        
        # Generate appropriate diagram based on type
        if diagram_type == "architecture":
            diagram_content = self._generate_architecture_diagram(analysis_data)
        elif diagram_type == "class":
            diagram_content = self._generate_class_diagram(analysis_data)
        else:
            diagram_content = self._generate_architecture_diagram(analysis_data)
        
        return Message(
            type="diagram_generated",
            data={
                "diagram_type": diagram_type,
                "content": diagram_content,
                "format": "mermaid"
            },
            sender=self.agent_id,
            recipient=message.sender
        )
    
    def _generate_architecture_diagram(self, analysis_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate multiple architecture diagrams based on actual repository data"""
        diagrams = []
        
        # Generate project structure diagram
        try:
            structure_diagram = self._generate_project_structure_diagram(analysis_data)
            diagrams.append({
                "type": "structure",
                "title": "Project Structure",
                "content": structure_diagram
            })
        except Exception as e:
            logger.warning(f"Failed to generate structure diagram: {e}")
        
        # Generate class hierarchy diagram if classes exist
        classes = analysis_data.get('classes', [])
        if classes:
            try:
                class_diagram = self._generate_repository_class_diagram(analysis_data)
                diagrams.append({
                    "type": "class",
                    "title": "Class Hierarchy",
                    "content": class_diagram
                })
            except Exception as e:
                logger.warning(f"Failed to generate class diagram: {e}")
        
        # Generate API flow diagram if endpoints exist
        endpoints = analysis_data.get('api_endpoints', [])
        if endpoints:
            try:
                api_diagram = self._generate_api_flow_diagram(analysis_data)
                diagrams.append({
                    "type": "sequence",
                    "title": "API Flow",
                    "content": api_diagram
                })
            except Exception as e:
                logger.warning(f"Failed to generate API diagram: {e}")
        
        # Generate dependencies diagram
        dependencies = analysis_data.get('dependencies', [])
        if dependencies:
            try:
                deps_diagram = self._generate_dependencies_diagram(analysis_data)
                diagrams.append({
                    "type": "dependencies",
                    "title": "Dependencies",
                    "content": deps_diagram
                })
            except Exception as e:
                logger.warning(f"Failed to generate dependencies diagram: {e}")
        
        # If no specific diagrams, create a general project overview
        if not diagrams:
            overview_diagram = self._generate_project_overview_diagram(analysis_data)
            diagrams.append({
                "type": "architecture",
                "title": "Project Overview",
                "content": overview_diagram
            })
        
        return diagrams
    
    def _generate_project_structure_diagram(self, analysis_data: Dict[str, Any]) -> str:
        """Generate project structure diagram"""
        project_name = analysis_data.get('project_id', 'Project').replace(' ', '_').replace('-', '_')
        functions = analysis_data.get('functions', [])[:8]  # Limit to 8 functions
        classes = analysis_data.get('classes', [])[:6]  # Limit to 6 classes
        
        logger.debug(f"Generating diagram for project: {project_name} with {len(functions)} functions, {len(classes)} classes")
        
        diagram = f"graph TD\n    A[\"{project_name}\"]\n"
        
        # Add basic structure
        diagram += "    A --> B[\"📁 Source Code\"]\n"
        diagram += "    A --> C[\"📋 Statistics\"]\n"
        
        # Add statistics
        stats = analysis_data.get('statistics', {})
        file_count = stats.get('total_files', analysis_data.get('file_count', 0))
        line_count = stats.get('total_lines', analysis_data.get('lines_of_code', 0))
        
        diagram += f"    C --> C1[\"{file_count} Files\"]\n"
        diagram += f"    C --> C2[\"{line_count} Lines of Code\"]\n"
        diagram += f"    C --> C3[\"{len(functions)} Functions\"]\n"
        diagram += f"    C --> C4[\"{len(classes)} Classes\"]\n"
        
        # Add classes with more details
        if classes:
            diagram += "    B --> CLS[\"🏗️ Classes\"]\n"
            for i, cls in enumerate(classes[:6]):  # Limit to prevent diagram overflow
                if isinstance(cls, dict):
                    class_name = cls.get('name', f'Class{i+1}')
                    # Sanitize name for Mermaid
                    safe_name = class_name.replace(' ', '_').replace('-', '_').replace('.', '_')[:20]
                    diagram += f"    CLS --> CLS{i+1}[\"{safe_name}\"]\n"
                else:
                    safe_name = str(cls).replace(' ', '_').replace('-', '_').replace('.', '_')[:20]
                    diagram += f"    CLS --> CLS{i+1}[\"{safe_name}\"]\n"
        
        # Add functions with more details
        if functions:
            diagram += "    B --> FN[\"⚙️ Functions\"]\n"
            for i, func in enumerate(functions[:6]):  # Limit to prevent diagram overflow
                if isinstance(func, dict):
                    func_name = func.get('name', f'function{i+1}')
                    safe_name = func_name.replace(' ', '_').replace('-', '_').replace('.', '_')[:20]  
                    diagram += f"    FN --> FN{i+1}[\"{safe_name}\"]\n"
                else:
                    safe_name = str(func).replace(' ', '_').replace('-', '_').replace('.', '_')[:20]
                    diagram += f"    FN --> FN{i+1}[\"{safe_name}\"]\n"
        
        # Add dependencies with more details
        dependencies = analysis_data.get('dependencies', [])[:5]
        if dependencies:
            diagram += "    A --> DEP[\"📦 Dependencies\"]\n"
            for i, dep in enumerate(dependencies):
                if isinstance(dep, dict):
                    dep_name = dep.get('name', f'dep{i+1}')
                    safe_name = dep_name.replace(' ', '_').replace('-', '_').replace('.', '_')[:15]
                    diagram += f"    DEP --> DEP{i+1}[\"{safe_name}\"]\n"
                else:
                    safe_name = str(dep).replace(' ', '_').replace('-', '_').replace('.', '_')[:15]
                    diagram += f"    DEP --> DEP{i+1}[\"{safe_name}\"]\n"
        
        logger.debug(f"Generated diagram with {len(diagram)} characters")
        return diagram
    
    def _generate_repository_class_diagram(self, analysis_data: Dict[str, Any]) -> str:
        """Generate class hierarchy diagram for the actual repository"""
        classes = analysis_data.get('classes', [])[:8]  # Limit to 8 classes
        diagram = "classDiagram\n"
        
        for cls in classes:
            if isinstance(cls, dict):
                class_name = cls.get('name', 'UnknownClass').replace(' ', '_').replace('-', '_')
                methods = cls.get('methods', [])[:5]  # Limit to 5 methods per class
                
                diagram += f"    class {class_name} {{\n"
                for method in methods:
                    if isinstance(method, dict):
                        method_name = method.get('name', 'method').replace(' ', '_').replace('-', '_')
                    else:
                        method_name = str(method).replace(' ', '_').replace('-', '_')
                    diagram += f"        +{method_name}()\n"
                diagram += "    }\n"
                
                # Add inheritance if available
                inheritance = cls.get('inheritance', [])
                for parent in inheritance:
                    parent_name = str(parent).replace(' ', '_').replace('-', '_')
                    diagram += f"    {parent_name} <|-- {class_name}\n"
            else:
                class_name = str(cls).replace(' ', '_').replace('-', '_')
                diagram += f"    class {class_name} {{\n    }}\n"
        
        return diagram
    
    def _generate_api_flow_diagram(self, analysis_data: Dict[str, Any]) -> str:
        """Generate API flow diagram"""
        endpoints = analysis_data.get('api_endpoints', [])[:6]  # Limit to 6 endpoints
        diagram = "sequenceDiagram\n    participant Client\n    participant API\n    participant Handler\n\n"
        
        for endpoint in endpoints:
            if isinstance(endpoint, dict):
                method = endpoint.get('method', 'GET')
                path = endpoint.get('path', '/endpoint')
                function = endpoint.get('function', 'handler')
            else:
                method = 'GET'
                path = str(endpoint)
                function = 'handler'
            
            diagram += f"    Client->>API: {method} {path}\n"
            diagram += f"    API->>Handler: {function}()\n"
            diagram += f"    Handler->>API: Response\n"
            diagram += f"    API->>Client: JSON Response\n"
        
        return diagram
    
    def _generate_dependencies_diagram(self, analysis_data: Dict[str, Any]) -> str:
        """Generate dependencies diagram with proper categorization"""
        dependencies = analysis_data.get('dependencies', [])[:12]  # Limit to prevent overflow
        project_name = analysis_data.get('project_id', 'Project').replace(' ', '_').replace('-', '_')
        
        logger.debug(f"Generating dependencies diagram with {len(dependencies)} dependencies")
        
        diagram = f"graph TD\n    PROJECT[\"{project_name}\"]\n"
        
        # Categorize dependencies more intelligently
        runtime_deps = []
        dev_deps = []
        framework_deps = []
        
        framework_keywords = ['fastapi', 'flask', 'django', 'express', 'react', 'vue', 'angular', 'spring']
        dev_keywords = ['test', 'dev', 'debug', 'lint', 'format', 'build', 'webpack', 'babel']
        
        for dep in dependencies:
            if isinstance(dep, dict):
                dep_name = dep.get('name', '').lower()
                dep_type = dep.get('type', 'runtime')
            else:
                dep_name = str(dep).lower()
                dep_type = 'runtime'
            
            # Categorize based on keywords and explicit type
            if dep_type == 'development' or any(keyword in dep_name for keyword in dev_keywords):
                dev_deps.append(dep)
            elif any(keyword in dep_name for keyword in framework_keywords):
                framework_deps.append(dep)
            else:
                runtime_deps.append(dep)
        
        # Add framework dependencies
        if framework_deps:
            diagram += "    PROJECT --> FRAMEWORK[\"🏗️ Frameworks\"]\n"
            for i, dep in enumerate(framework_deps[:4]):
                if isinstance(dep, dict):
                    dep_name = dep.get('name', f'framework_{i+1}')[:15]
                else:
                    dep_name = str(dep)[:15]
                safe_name = dep_name.replace('-', '_').replace('.', '_')
                diagram += f"    FRAMEWORK --> FW{i+1}[\"{safe_name}\"]\n"
        
        # Add runtime dependencies  
        if runtime_deps:
            diagram += "    PROJECT --> RUNTIME[\"⚙️ Runtime\"]\n"
            for i, dep in enumerate(runtime_deps[:5]):
                if isinstance(dep, dict):
                    dep_name = dep.get('name', f'runtime_{i+1}')[:15]
                else:
                    dep_name = str(dep)[:15]
                safe_name = dep_name.replace('-', '_').replace('.', '_')
                diagram += f"    RUNTIME --> RT{i+1}[\"{safe_name}\"]\n"
        
        # Add development dependencies
        if dev_deps:
            diagram += "    PROJECT --> DEV[\"🛠️ Development\"]\n"
            for i, dep in enumerate(dev_deps[:4]):
                if isinstance(dep, dict):
                    dep_name = dep.get('name', f'dev_{i+1}')[:15]
                else:
                    dep_name = str(dep)[:15]
                safe_name = dep_name.replace('-', '_').replace('.', '_')
                diagram += f"    DEV --> DV{i+1}[\"{safe_name}\"]\n"
        
        # If no dependencies found, show a basic structure
        if not dependencies:
            diagram += "    PROJECT --> DEPS[\"📦 No Dependencies Found\"]\n"
            diagram += "    DEPS --> INFO[\"Self-contained Project\"]\n"
        
        return diagram
    
    def _generate_project_overview_diagram(self, analysis_data: Dict[str, Any]) -> str:
        """Generate general project overview diagram"""
        project_name = analysis_data.get('project_id', 'Project').replace(' ', '_').replace('-', '_')
        file_count = analysis_data.get('file_count', 0)
        func_count = len(analysis_data.get('functions', []))
        class_count = len(analysis_data.get('classes', []))
        
        return f"""graph TD
    A[{project_name}] --> B[Code_Base]
    B --> C[{file_count}_Files]
    B --> D[{func_count}_Functions]
    B --> E[{class_count}_Classes]
    
    A --> F[Repository]
    F --> G[Source_Code]
    
    A --> H[Statistics]
    H --> I[{analysis_data.get('lines_of_code', 0)}_Lines_of_Code]"""
    
    def _generate_class_diagram(self, analysis_data: Dict[str, Any]) -> str:
        return """classDiagram
    class BaseAgent {
        +agent_id: str
        +name: str
        +start()
        +stop()
        +handle_message()
    }
    
    class CodeAnalyzerAgent {
        +analyze_repository()
        +analyze_file()
    }
    
    class DocumentationWriterAgent {
        +generate_documentation()
        +format_documentation()
    }
    
    BaseAgent <|-- CodeAnalyzerAgent
    BaseAgent <|-- DocumentationWriterAgent"""

class QualityReviewerAgent(BaseAgent):
    """Agent responsible for quality review"""
    
    def __init__(self, agent_id: str):
        super().__init__(agent_id, "QualityReviewer")
        self.quality_metrics = {
            "completeness": 0.0,
            "accuracy": 0.0,
            "readability": 0.0,
            "consistency": 0.0
        }
    
    async def handle_message(self, message: Message) -> Optional[Message]:
        if message.type == "review_documentation":
            return await self._review_documentation(message)
        return None
    
    async def _review_documentation(self, message: Message) -> Message:
        content = message.data.get("content", "")
        analysis_data = message.data.get("analysis", {})
        
        # Calculate comprehensive quality assessment
        quality_score = self._calculate_quality_score(content, analysis_data)
        detailed_metrics = self._analyze_detailed_metrics(content, analysis_data)
        improvement_suggestions = self._generate_improvement_suggestions(content, detailed_metrics)
        
        return Message(
            type="quality_review_complete",
            data={
                "quality_score": quality_score,
                "metrics": detailed_metrics,
                "suggestions": improvement_suggestions
            },
            sender=self.agent_id,
            recipient=message.sender
        )
    
    def _calculate_quality_score(self, content: str, analysis_data: Dict[str, Any]) -> float:
        """Calculate comprehensive quality score"""
        total_score = 0.0
        max_score = 100.0
        
        # Content structure (25 points)
        headers = content.count("## ") + content.count("### ")
        total_score += min(headers * 5, 25)
        
        # Code examples (20 points)
        code_blocks = content.count("```")
        total_score += min(code_blocks * 5, 20)
        
        # Content depth (20 points)
        word_count = len(content.split())
        if word_count >= 1000:
            total_score += 20
        elif word_count >= 500:
            total_score += 15
        elif word_count >= 200:
            total_score += 10
        
        # Technical accuracy (15 points)
        tech_terms = ['class', 'function', 'method', 'api', 'endpoint', 'parameter', 'return', 'import']
        tech_count = sum(1 for term in tech_terms if term in content.lower())
        total_score += min(tech_count * 2, 15)
        
        # Examples and usage (10 points)
        examples = content.lower().count('example') + content.lower().count('usage')
        total_score += min(examples * 3, 10)
        
        # Documentation completeness (10 points)
        sections = ['installation', 'usage', 'api', 'example', 'overview', 'getting started']
        section_count = sum(1 for section in sections if section in content.lower())
        total_score += min(section_count * 2, 10)
        
        return min(total_score / max_score, 1.0)
    
    def _analyze_detailed_metrics(self, content: str, analysis_data: Dict[str, Any]) -> Dict[str, float]:
        """Analyze detailed quality metrics"""
        word_count = len(content.split())
        headers = content.count("## ") + content.count("### ")
        code_blocks = content.count("```")
        
        return {
            "completeness": min(word_count / 1000, 1.0) * 0.8 + (headers >= 5) * 0.2,
            "accuracy": min(code_blocks / 5, 1.0) * 0.6 + (content.count('def ') > 0) * 0.4,
            "readability": (headers >= 3) * 0.4 + (word_count >= 200) * 0.3 + ('example' in content.lower()) * 0.3,
            "consistency": (headers >= 2) * 0.5 + (code_blocks >= 2) * 0.5
        }
    
    def _generate_improvement_suggestions(self, content: str, metrics: Dict[str, float]) -> List[str]:
        """Generate specific improvement suggestions"""
        suggestions = []
        
        if metrics['completeness'] < 0.8:
            suggestions.append("📝 Add more comprehensive content - aim for at least 1000 words")
            suggestions.append("🏗️ Include more detailed sections such as installation, usage, and API reference")
        
        if metrics['accuracy'] < 0.7:
            suggestions.append("💻 Add more code examples and function definitions")
            suggestions.append("🔍 Include actual code snippets from your repository")
        
        if metrics['readability'] < 0.6:
            suggestions.append("📚 Improve structure with more clear headings and subheadings")
            suggestions.append("💡 Add practical examples to illustrate concepts")
        
        if metrics['consistency'] < 0.7:
            suggestions.append("🎯 Maintain consistent formatting throughout the documentation")
            suggestions.append("🔗 Ensure all code blocks have proper language specification")
        
        # Content-specific suggestions
        if "```python" not in content and "def " in content:
            suggestions.append("🐍 Specify Python language in code blocks for better syntax highlighting")
        
        if content.count("## ") < 3:
            suggestions.append("📋 Add more section headers to organize content better")
        
        if "troubleshooting" not in content.lower():
            suggestions.append("🔧 Add a troubleshooting section to help users solve common issues")
        
        return suggestions[:5]  # Limit to top 5 suggestions

class ContentOrchestratorAgent(BaseAgent):
    """Agent responsible for orchestrating the workflow"""
    
    def __init__(self, agent_id: str):
        super().__init__(agent_id, "ContentOrchestrator")
        self.workflows = {}
        self.workflow_steps = [
            "analyze_code",
            "generate_documentation", 
            "create_diagrams",
            "review_quality",
            "finalize_content"
        ]
    
    async def handle_message(self, message: Message) -> Optional[Message]:
        if message.type == "start_workflow":
            return await self._start_workflow(message)
        elif message.type == "workflow_step_complete":
            return await self._handle_step_complete(message)
        return None
    
    async def _start_workflow(self, message: Message) -> Message:
        workflow_id = message.data.get("workflow_id")
        
        self.workflows[workflow_id] = {
            "status": "running",
            "current_step": 0,
            "steps_completed": [],
            "data": message.data
        }
        
        return Message(
            type="workflow_started",
            data={
                "workflow_id": workflow_id,
                "total_steps": len(self.workflow_steps),
                "current_step": self.workflow_steps[0]
            },
            sender=self.agent_id,
            recipient=message.sender
        )
    
    async def _handle_step_complete(self, message: Message) -> Message:
        workflow_id = message.data.get("workflow_id")
        step_name = message.data.get("step_name")
        
        if workflow_id in self.workflows:
            workflow = self.workflows[workflow_id]
            workflow["steps_completed"].append(step_name)
            workflow["current_step"] += 1
            
            if workflow["current_step"] >= len(self.workflow_steps):
                workflow["status"] = "completed"
        
        return Message(
            type="workflow_updated",
            data={
                "workflow_id": workflow_id,
                "status": self.workflows[workflow_id]["status"]
            },
            sender=self.agent_id,
            recipient=message.sender
        )

class UserFeedbackAgent(BaseAgent):
    """Agent responsible for handling user feedback"""
    
    def __init__(self, agent_id: str):
        super().__init__(agent_id, "UserFeedback")
        self.feedback_store = []
    
    async def handle_message(self, message: Message) -> Optional[Message]:
        if message.type == "collect_feedback":
            return await self._collect_feedback(message)
        elif message.type == "analyze_feedback":
            return await self._analyze_feedback(message)
        return None
    
    async def _collect_feedback(self, message: Message) -> Message:
        feedback_data = message.data
        
        # Store feedback (in real implementation would go to BigQuery)
        self.feedback_store.append(feedback_data)
        
        return Message(
            type="feedback_collected",
            data={
                "feedback_id": len(self.feedback_store),
                "status": "stored"
            },
            sender=self.agent_id,
            recipient=message.sender
        )
    
    async def _analyze_feedback(self, message: Message) -> Message:
        # Analyze collected feedback
        if not self.feedback_store:
            avg_rating = 0
            total_feedback = 0
        else:
            ratings = [f.get("rating", 0) for f in self.feedback_store]
            avg_rating = sum(ratings) / len(ratings)
            total_feedback = len(self.feedback_store)
        
        return Message(
            type="feedback_analysis_complete",
            data={
                "average_rating": avg_rating,
                "total_feedback": total_feedback,
                "trends": ["Generally positive", "Users want more examples"]
            },
            sender=self.agent_id,
            recipient=message.sender
        ) 