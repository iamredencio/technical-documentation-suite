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
    
    def _generate_architecture_diagram(self, analysis_data: Dict[str, Any]) -> str:
        return """graph TB
    subgraph "Application Layer"
        API[FastAPI Application]
        AGENTS[Multi-Agent System]
    end
    
    subgraph "Agent Layer"
        CA[Code Analyzer]
        DW[Doc Writer]
        DG[Diagram Generator]
        QR[Quality Reviewer]
        CO[Content Orchestrator]
        UF[User Feedback]
    end
    
    subgraph "Storage Layer"
        GCS[Google Cloud Storage]
        BQ[BigQuery]
    end
    
    API --> AGENTS
    AGENTS --> CA
    AGENTS --> DW
    AGENTS --> DG
    AGENTS --> QR
    AGENTS --> CO
    AGENTS --> UF
    CA --> GCS
    UF --> BQ"""
    
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