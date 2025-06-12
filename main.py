"""
Technical Documentation Suite - Main Application Entry Point
Built for the Google Cloud ADK Hackathon
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import os
import uuid
from datetime import datetime

# Import our agent modules (will be created)
# from src.agents.orchestrator import ContentOrchestratorAgent
# from src.agents.code_analyzer import CodeAnalyzerAgent
# from src.agents.doc_writer import DocumentationWriterAgent
# from src.agents.diagram_generator import DiagramGeneratorAgent
# from src.agents.quality_reviewer import QualityReviewerAgent
# from src.agents.feedback_collector import UserFeedbackAgent

app = FastAPI(
    title="Technical Documentation Suite",
    description="Multi-agent system for automated technical documentation generation",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class DocumentationRequest(BaseModel):
    repository_url: str
    project_id: str
    output_formats: List[str] = ["markdown", "html"]
    include_diagrams: bool = True
    target_audience: str = "developers"

class WorkflowStatus(BaseModel):
    workflow_id: str
    status: str
    progress: int
    message: str
    created_at: datetime
    completed_at: Optional[datetime] = None

class FeedbackRequest(BaseModel):
    workflow_id: str
    user_id: Optional[str] = None
    rating: int
    usefulness_score: int
    accuracy_score: int
    completeness_score: int
    comments: Optional[str] = None

# In-memory storage for demo (in production, this would be in a database)
workflows: Dict[str, WorkflowStatus] = {}

@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "message": "Technical Documentation Suite API",
        "version": "1.0.0",
        "description": "Multi-agent system for automated technical documentation generation",
        "hackathon": "Google Cloud ADK Hackathon",
        "endpoints": {
            "health": "/health",
            "generate": "/generate",
            "status": "/status/{workflow_id}",
            "feedback": "/feedback"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Technical Documentation Suite",
        "version": "1.0.0"
    }

@app.post("/generate")
async def generate_documentation(request: DocumentationRequest):
    """
    Generate documentation for a repository using the multi-agent system
    """
    try:
        # Generate unique workflow ID
        workflow_id = str(uuid.uuid4())
        
        # Create initial workflow status
        workflow_status = WorkflowStatus(
            workflow_id=workflow_id,
            status="initiated",
            progress=0,
            message="Documentation generation initiated",
            created_at=datetime.now()
        )
        
        workflows[workflow_id] = workflow_status
        
        # TODO: Initialize and orchestrate agents
        # orchestrator = ContentOrchestratorAgent()
        # result = await orchestrator.process_documentation_request(request)
        
        # For now, simulate the process initiation
        workflows[workflow_id].status = "processing"
        workflows[workflow_id].progress = 10
        workflows[workflow_id].message = "Agents initialized, processing started"
        
        return {
            "success": True,
            "message": "Documentation generation initiated successfully",
            "data": {
                "workflow_id": workflow_id,
                "estimated_completion": "5-10 minutes",
                "status_endpoint": f"/status/{workflow_id}"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initiate documentation generation: {str(e)}")

@app.get("/status/{workflow_id}")
async def get_workflow_status(workflow_id: str):
    """
    Get the status of a documentation generation workflow
    """
    if workflow_id not in workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    workflow = workflows[workflow_id]
    
    return {
        "success": True,
        "data": {
            "workflow_id": workflow.workflow_id,
            "status": workflow.status,
            "progress": workflow.progress,
            "message": workflow.message,
            "created_at": workflow.created_at.isoformat(),
            "completed_at": workflow.completed_at.isoformat() if workflow.completed_at else None
        }
    }

@app.post("/feedback")
async def submit_feedback(feedback: FeedbackRequest):
    """
    Submit feedback for a completed documentation workflow
    """
    try:
        if feedback.workflow_id not in workflows:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        # TODO: Store feedback in BigQuery
        # feedback_agent = UserFeedbackAgent()
        # await feedback_agent.store_feedback(feedback)
        
        # For now, just acknowledge the feedback
        feedback_data = {
            "workflow_id": feedback.workflow_id,
            "timestamp": datetime.now().isoformat(),
            "rating": feedback.rating,
            "scores": {
                "usefulness": feedback.usefulness_score,
                "accuracy": feedback.accuracy_score,
                "completeness": feedback.completeness_score
            },
            "comments": feedback.comments,
            "user_id": feedback.user_id
        }
        
        return {
            "success": True,
            "message": "Feedback submitted successfully",
            "data": feedback_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit feedback: {str(e)}")

@app.get("/workflows")
async def list_workflows():
    """
    List all workflows (for debugging/admin purposes)
    """
    return {
        "success": True,
        "data": {
            "total_workflows": len(workflows),
            "workflows": [
                {
                    "workflow_id": wf.workflow_id,
                    "status": wf.status,
                    "progress": wf.progress,
                    "created_at": wf.created_at.isoformat()
                }
                for wf in workflows.values()
            ]
        }
    }

if __name__ == "__main__":
    # Get port from environment variable (for Cloud Run)
    port = int(os.environ.get("PORT", 8080))
    
    print("🚀 Starting Technical Documentation Suite API")
    print(f"📋 Version: 1.0.0")
    print(f"🌐 Port: {port}")
    print(f"🏆 Built for: Google Cloud ADK Hackathon")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Set to True for development
        log_level="info"
    ) 