"""
All remaining agents for the Technical Documentation Suite
"""

from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent, Message
import json

class DiagramGeneratorAgent(BaseAgent):
    """Agent responsible for generating diagrams"""
    
    def __init__(self, agent_id: str):
        super().__init__(agent_id, "DiagramGenerator")
        self.diagram_types = ["architecture", "flow", "class", "sequence"]
    
    async def handle_message(self, message: Message) -> Optional[Message]:
        if message.type == "generate_diagram":
            return await self._generate_diagram(message)
        return None
    
    async def _generate_diagram(self, message: Message) -> Message:
        diagram_type = message.data.get("type", "architecture")
        analysis_data = message.data.get("analysis", {})
        
        # Mock Mermaid diagram generation
        if diagram_type == "architecture":
            diagram_content = self._generate_architecture_diagram(analysis_data)
        elif diagram_type == "class":
            diagram_content = self._generate_class_diagram(analysis_data)
        else:
            diagram_content = "graph TD\n    A[Start] --> B[End]"
        
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
        """Generate repository-specific diagrams based on code analysis"""
        diagrams = []
        
        # 1. Project Structure Diagram
        if analysis_data.get('file_count', 0) > 0:
            structure_diagram = self._generate_project_structure_diagram(analysis_data)
            diagrams.append({
                "type": "architecture",
                "title": f"{analysis_data.get('project_id', 'Project')} Structure",
                "content": structure_diagram
            })
        
        # 2. Class Hierarchy Diagram (if classes exist)
        if analysis_data.get('classes', []):
            class_diagram = self._generate_repository_class_diagram(analysis_data)
            diagrams.append({
                "type": "class",
                "title": "Class Hierarchy",
                "content": class_diagram
            })
        
        # 3. API Flow Diagram (if API endpoints exist)
        if analysis_data.get('api_endpoints', []):
            api_diagram = self._generate_api_flow_diagram(analysis_data)
            diagrams.append({
                "type": "flow",
                "title": "API Flow",
                "content": api_diagram
            })
        
        # 4. Dependencies Diagram
        if analysis_data.get('dependencies', []):
            deps_diagram = self._generate_dependencies_diagram(analysis_data)
            diagrams.append({
                "type": "graph",
                "title": "Dependencies",
                "content": deps_diagram
            })
        
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
        
        diagram = f"graph TD\n    A[{project_name}] --> B[Source_Code]\n"
        
        # Add classes
        if classes:
            diagram += "    B --> C[Classes]\n"
            for i, cls in enumerate(classes):
                if isinstance(cls, dict):
                    class_name = cls.get('name', f'Class{i+1}').replace(' ', '_').replace('-', '_')
                else:
                    class_name = str(cls).replace(' ', '_').replace('-', '_')
                diagram += f"    C --> C{i+1}[{class_name}]\n"
        
        # Add functions
        if functions:
            diagram += "    B --> F[Functions]\n"
            for i, func in enumerate(functions):
                if isinstance(func, dict):
                    func_name = func.get('name', f'function{i+1}').replace(' ', '_').replace('-', '_')
                else:
                    func_name = str(func).replace(' ', '_').replace('-', '_')
                diagram += f"    F --> F{i+1}[{func_name}]\n"
        
        # Add dependencies
        dependencies = analysis_data.get('dependencies', [])[:5]
        if dependencies:
            diagram += "    A --> D[Dependencies]\n"
            for i, dep in enumerate(dependencies):
                if isinstance(dep, dict):
                    dep_name = dep.get('name', f'dep{i+1}').replace(' ', '_').replace('-', '_')
                else:
                    dep_name = str(dep).replace(' ', '_').replace('-', '_')
                diagram += f"    D --> D{i+1}[{dep_name}]\n"
        
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
        """Generate dependencies diagram"""
        dependencies = analysis_data.get('dependencies', [])[:8]  # Limit to 8 dependencies
        project_name = analysis_data.get('project_id', 'Project').replace(' ', '_').replace('-', '_')
        
        diagram = f"graph LR\n    A[{project_name}] --> B[Runtime_Deps]\n    A --> C[Dev_Deps]\n\n"
        
        runtime_deps = [d for d in dependencies if isinstance(d, dict) and d.get('type') == 'runtime'][:4]
        dev_deps = [d for d in dependencies if isinstance(d, dict) and d.get('type') == 'development'][:4]
        
        # If no categorized dependencies, use first 4 as runtime deps
        if not runtime_deps and not dev_deps:
            runtime_deps = dependencies[:4]
        
        for i, dep in enumerate(runtime_deps):
            if isinstance(dep, dict):
                dep_name = dep.get('name', f'runtime_dep_{i+1}').replace(' ', '_').replace('-', '_')
            else:
                dep_name = str(dep).replace(' ', '_').replace('-', '_')
            diagram += f"    B --> R{i+1}[{dep_name}]\n"
        
        for i, dep in enumerate(dev_deps):
            if isinstance(dep, dict):
                dep_name = dep.get('name', f'dev_dep_{i+1}').replace(' ', '_').replace('-', '_')
            else:
                dep_name = str(dep).replace(' ', '_').replace('-', '_')
            diagram += f"    C --> D{i+1}[{dep_name}]\n"
        
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
        
        # Mock quality assessment
        quality_score = self._calculate_quality_score(content, analysis_data)
        
        return Message(
            type="quality_review_complete",
            data={
                "quality_score": quality_score,
                "metrics": self.quality_metrics,
                "suggestions": [
                    "Add more code examples",
                    "Improve section consistency",
                    "Add troubleshooting section"
                ]
            },
            sender=self.agent_id,
            recipient=message.sender
        )
    
    def _calculate_quality_score(self, content: str, analysis_data: Dict[str, Any]) -> float:
        # Simple quality scoring
        word_count = len(content.split())
        has_examples = "```" in content
        has_sections = "##" in content
        
        score = 0.5  # Base score
        if word_count > 100:
            score += 0.2
        if has_examples:
            score += 0.2
        if has_sections:
            score += 0.1
        
        return min(score, 1.0)

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