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
import shutil

# Import our agent modules
from src.agents.base_agent import BaseAgent, Message
from src.agents.code_analyzer import CodeAnalyzerAgent
from src.agents.doc_writer import DocumentationWriterAgent
from src.agents.orchestrator import (
    DiagramGeneratorAgent, 
    QualityReviewerAgent, 
    ContentOrchestratorAgent, 
    UserFeedbackAgent
)
from src.utils.git_utils import clone_repo

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

class AgentStatus(BaseModel):
    agent_id: str
    agent_name: str
    status: str  # idle, active, completed, error
    progress: int
    current_task: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class WorkflowStatus(BaseModel):
    workflow_id: str
    status: str
    progress: int
    message: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    current_agent: Optional[str] = None
    agents: Dict[str, AgentStatus] = {}
    result: Optional[Dict[str, Any]] = None

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
agent_execution_queue: Dict[str, List[str]] = {}  # workflow_id -> list of agent names

# Initialize agents
agents = {
    "code_analyzer": CodeAnalyzerAgent("code_analyzer_01"),
    "doc_writer": DocumentationWriterAgent("doc_writer_01"),
    "diagram_generator": DiagramGeneratorAgent("diagram_gen_01"),
    "quality_reviewer": QualityReviewerAgent("quality_reviewer_01"),
    "orchestrator": ContentOrchestratorAgent("orchestrator_01"),
    "feedback_collector": UserFeedbackAgent("feedback_01")
}

# Add async wrapper to DocumentationWriterAgent
async def doc_writer_generate_async(agent, analysis_data, target_audience="developers"):
    msg = Message(
        type="generate_documentation",
        data={
            "analysis": analysis_data, 
            "format": "markdown",
            "audience": target_audience
        },
        sender=agent.agent_id,
        recipient=agent.agent_id
    )
    result = await agent._generate_documentation(msg)
    return result.data["content"]

# Add synchronous wrapper to QualityReviewerAgent
def quality_reviewer_score_sync(agent, content, analysis_data):
    return agent._calculate_quality_score(content, analysis_data)

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

@app.get("/agents/status")
async def get_agents_status():
    """Get the current status of all agents"""
    agent_statuses = {}
    for agent_id, agent in agents.items():
        agent_statuses[agent_id] = {
            "agent_id": agent_id,
            "agent_name": agent.__class__.__name__,
            "status": getattr(agent, 'current_status', 'idle'),
            "health": "healthy"
        }
    
    return {
        "success": True,
        "data": {
            "total_agents": len(agents),
            "agents": agent_statuses
        }
    }

async def initialize_workflow_agents(workflow_id: str):
    """Initialize agents for a workflow with proper status tracking"""
    agent_names = ["code_analyzer", "doc_writer", "diagram_generator", "quality_reviewer", "orchestrator", "feedback_collector"]
    
    workflow_agents = {}
    for agent_name in agent_names:
        workflow_agents[agent_name] = AgentStatus(
            agent_id=agent_name,
            agent_name=agent_name.replace("_", " ").title(),
            status="idle",
            progress=0
        )
    
    workflows[workflow_id].agents = workflow_agents
    agent_execution_queue[workflow_id] = agent_names.copy()

async def execute_next_agent(workflow_id: str):
    """Execute the next agent in the queue and update status"""
    if workflow_id not in agent_execution_queue or not agent_execution_queue[workflow_id]:
        # All agents completed - set demo result
        workflows[workflow_id].status = "completed"
        workflows[workflow_id].progress = 100
        workflows[workflow_id].message = "Documentation generation completed successfully"
        workflows[workflow_id].completed_at = datetime.now()
        workflows[workflow_id].current_agent = None
        
        # Set demo result data
        workflows[workflow_id].result = {
            "documentation": """# Sample Project Documentation

## Overview
This is a sample technical documentation generated in demo mode. To see real AI-generated documentation, please set your GEMINI_API_KEY environment variable.

## Features
- Multi-agent documentation generation
- Real-time progress tracking
- Quality assessment and scoring
- Support for multiple output formats

## Architecture
The system uses a multi-agent approach with specialized agents for different tasks:
- **Code Analyzer**: Analyzes repository structure and extracts key information
- **Documentation Writer**: Generates comprehensive documentation using AI
- **Diagram Generator**: Creates architectural and flow diagrams
- **Quality Reviewer**: Assesses documentation quality and completeness

## Getting Started
1. Set your GEMINI_API_KEY environment variable
2. Start the application
3. Enter a GitHub repository URL
4. Watch the agents work their magic!

## API Endpoints
- `POST /generate` - Generate documentation for a repository
- `GET /status/{workflow_id}` - Check generation progress
- `POST /feedback` - Submit feedback on generated documentation

*This is demo content. Enable AI features by setting GEMINI_API_KEY for real documentation generation.*
""",
            "diagrams": [
                {
                    "type": "architecture",
                    "title": "System Architecture",
                    "content": "graph TD\n    A[User] --> B[Frontend]\n    B --> C[API Gateway]\n    C --> D[Multi-Agent System]\n    D --> E[Code Analyzer]\n    D --> F[Doc Writer]\n    D --> G[Quality Reviewer]"
                },
                {
                    "type": "workflow",
                    "title": "Documentation Generation Flow", 
                    "content": "sequenceDiagram\n    participant U as User\n    participant F as Frontend\n    participant A as API\n    participant AG as Agents\n    U->>F: Submit Repository\n    F->>A: POST /generate\n    A->>AG: Initialize Workflow\n    AG->>A: Status Updates\n    A->>F: Progress Updates\n    F->>U: Real-time Progress"
                }
            ],
            "quality": {
                "overall_score": 85,
                "completeness": 90,
                "clarity": 80,
                "technical_accuracy": 85,
                "feedback": "Good documentation structure with clear sections and examples."
            },
            "analysis": {
                "repository_url": "demo-repository",
                "project_id": "demo-project",
                "file_count": 25,
                "lines_of_code": 1500,
                "functions": [
                    {"name": "generate_documentation", "description": "Main documentation generation function"},
                    {"name": "analyze_code", "description": "Code analysis function"},
                    {"name": "create_diagrams", "description": "Diagram generation function"}
                ],
                "classes": [
                    {"name": "DocumentationAgent", "description": "Main agent class for documentation generation"},
                    {"name": "CodeAnalyzer", "description": "Code analysis agent"},
                    {"name": "DiagramGenerator", "description": "Diagram generation agent"}
                ]
            },
            "ai_generated": False
        }
        return
    
    # Get next agent
    next_agent = agent_execution_queue[workflow_id].pop(0)
    
    # Update workflow status
    workflows[workflow_id].current_agent = next_agent
    workflows[workflow_id].progress = min(10 + ((6 - len(agent_execution_queue[workflow_id])) * 15), 90)
    workflows[workflow_id].message = f"Agent {next_agent.replace('_', ' ').title()} is processing"
    
    # Update agent status
    workflows[workflow_id].agents[next_agent].status = "active"
    workflows[workflow_id].agents[next_agent].started_at = datetime.now()
    workflows[workflow_id].agents[next_agent].current_task = "Processing repository data"
    workflows[workflow_id].agents[next_agent].progress = 50
    
    # Mark previous agents as completed
    for agent_name in workflows[workflow_id].agents:
        if agent_name != next_agent and workflows[workflow_id].agents[agent_name].status == "active":
            workflows[workflow_id].agents[agent_name].status = "completed"
            workflows[workflow_id].agents[agent_name].progress = 100
            workflows[workflow_id].agents[agent_name].completed_at = datetime.now()

@app.post("/generate")
async def generate_documentation(request: DocumentationRequest):
    """
    Generate technical documentation for a repository using multi-agent system
    """
    try:
        # Create workflow
        workflow_id = str(uuid.uuid4())
        workflow = WorkflowStatus(
            workflow_id=workflow_id,
            status="initiated",
            progress=0,
            message="Initializing documentation generation",
            created_at=datetime.now()
        )
        workflows[workflow_id] = workflow
        
        # Initialize agents for this workflow
        await initialize_workflow_agents(workflow_id)
        
        # Update status to processing
        workflows[workflow_id].status = "processing"
        workflows[workflow_id].progress = 10
        workflows[workflow_id].message = "Starting multi-agent workflow"

        # Check if we should use real repo analysis or demo mode
        use_real_analysis = os.getenv('GEMINI_API_KEY') is not None
        
        print(f"🔍 API Key present: {use_real_analysis}")
        print(f"🔍 GEMINI_API_KEY value: {'SET' if os.getenv('GEMINI_API_KEY') else 'NOT SET'}")
        
        if use_real_analysis:
            try:
                # Initialize AI workflow with proper agent tracking
                workflows[workflow_id].message = "Initializing AI-powered analysis"
                workflows[workflow_id].current_agent = "code_analyzer"
                
                # Update agent status
                if "code_analyzer" in workflows[workflow_id].agents:
                    workflows[workflow_id].agents["code_analyzer"].status = "active"
                    workflows[workflow_id].agents["code_analyzer"].started_at = datetime.now()
                    workflows[workflow_id].agents["code_analyzer"].current_task = "Cloning repository"
                
                # 1. Clone the repository
                workflows[workflow_id].progress = 20
                workflows[workflow_id].message = "Cloning repository"
                print(f"🔍 Attempting to clone: {request.repository_url}")
                repo_path = clone_repo(request.repository_url)
                print(f"✅ Repository cloned to: {repo_path}")
                
                # Update agent status
                if "code_analyzer" in workflows[workflow_id].agents:
                    workflows[workflow_id].agents["code_analyzer"].current_task = "Analyzing code structure"
                
                # 2. Analyze the repository with real code analysis
                workflows[workflow_id].progress = 40
                workflows[workflow_id].message = "Analyzing code structure"
                print("🔍 Starting code analysis...")
                code_analysis = agents["code_analyzer"].analyze_repository(repo_path)
                print(f"✅ Code analysis complete: {len(code_analysis.get('functions', []))} functions, {len(code_analysis.get('classes', []))} classes")
                
                # Add request data to analysis
                code_analysis["repository_url"] = request.repository_url
                code_analysis["project_id"] = request.project_id
                
                # Complete code analyzer, start doc writer
                if "code_analyzer" in workflows[workflow_id].agents:
                    workflows[workflow_id].agents["code_analyzer"].status = "completed"
                    workflows[workflow_id].agents["code_analyzer"].progress = 100
                    workflows[workflow_id].agents["code_analyzer"].completed_at = datetime.now()
                
                workflows[workflow_id].current_agent = "doc_writer"
                if "doc_writer" in workflows[workflow_id].agents:
                    workflows[workflow_id].agents["doc_writer"].status = "active"
                    workflows[workflow_id].agents["doc_writer"].started_at = datetime.now()
                    workflows[workflow_id].agents["doc_writer"].current_task = "Generating AI documentation"
                
                # 3. Generate documentation using AI
                workflows[workflow_id].progress = 60
                workflows[workflow_id].message = "Generating AI-powered documentation"
                print(f"🔍 Starting AI documentation generation...")
                documentation = await doc_writer_generate_async(
                    agents["doc_writer"], 
                    code_analysis, 
                    request.target_audience
                )
                print(f"✅ Documentation generated: {len(documentation)} characters")
                
                # Complete doc writer, start diagram generator
                if "doc_writer" in workflows[workflow_id].agents:
                    workflows[workflow_id].agents["doc_writer"].status = "completed"
                    workflows[workflow_id].agents["doc_writer"].progress = 100
                    workflows[workflow_id].agents["doc_writer"].completed_at = datetime.now()
                
                workflows[workflow_id].current_agent = "diagram_generator"
                if "diagram_generator" in workflows[workflow_id].agents:
                    workflows[workflow_id].agents["diagram_generator"].status = "active"
                    workflows[workflow_id].agents["diagram_generator"].started_at = datetime.now()
                    workflows[workflow_id].agents["diagram_generator"].current_task = "Creating diagrams"
                
                # 4. Generate diagrams
                workflows[workflow_id].progress = 80
                workflows[workflow_id].message = "Creating architectural diagrams"
                print("🔍 Generating diagrams...")
                diagrams = agents["diagram_generator"]._generate_architecture_diagram(code_analysis)
                print("✅ Diagrams generated")
                
                # Complete diagram generator, start quality reviewer
                if "diagram_generator" in workflows[workflow_id].agents:
                    workflows[workflow_id].agents["diagram_generator"].status = "completed"
                    workflows[workflow_id].agents["diagram_generator"].progress = 100
                    workflows[workflow_id].agents["diagram_generator"].completed_at = datetime.now()
                
                workflows[workflow_id].current_agent = "quality_reviewer"
                if "quality_reviewer" in workflows[workflow_id].agents:
                    workflows[workflow_id].agents["quality_reviewer"].status = "active"
                    workflows[workflow_id].agents["quality_reviewer"].started_at = datetime.now()
                    workflows[workflow_id].agents["quality_reviewer"].current_task = "Reviewing quality"
                
                # 5. Quality review
                workflows[workflow_id].progress = 90
                workflows[workflow_id].message = "Reviewing documentation quality"
                print("🔍 Starting quality review...")
                quality = quality_reviewer_score_sync(agents["quality_reviewer"], documentation, code_analysis)
                print(f"✅ Quality review complete: {quality}")
                
                # Complete quality reviewer
                if "quality_reviewer" in workflows[workflow_id].agents:
                    workflows[workflow_id].agents["quality_reviewer"].status = "completed"
                    workflows[workflow_id].agents["quality_reviewer"].progress = 100
                    workflows[workflow_id].agents["quality_reviewer"].completed_at = datetime.now()
                
                # Clean up
                shutil.rmtree(repo_path)
                print("✅ Cleanup complete")
                
                # Store real results
                workflows[workflow_id].status = "completed"
                workflows[workflow_id].progress = 100
                workflows[workflow_id].message = "AI-powered documentation generation completed successfully"
                workflows[workflow_id].completed_at = datetime.now()
                workflows[workflow_id].current_agent = None
                workflows[workflow_id].result = {
                    "documentation": documentation,
                    "diagrams": diagrams,
                    "quality": quality,
                    "analysis": code_analysis,
                    "ai_generated": True
                }
                
                print("🎉 Real AI workflow completed successfully!")
                
            except Exception as e:
                # If real analysis fails, show the error and fall back to demo mode
                error_msg = str(e)
                print(f"❌ Real analysis failed: {error_msg}")
                workflows[workflow_id].message = f"AI analysis failed ({error_msg}), switching to demo mode"
                workflows[workflow_id].progress = 15
                
                # Reset agents and use demo mode
                await initialize_workflow_agents(workflow_id)
                await execute_next_agent(workflow_id)
        else:
            # Demo mode - simulate workflow
            print("🎭 Running in demo mode - GEMINI_API_KEY not set")
            workflows[workflow_id].message = "Running in demo mode (set GEMINI_API_KEY for real AI generation)"
            await execute_next_agent(workflow_id)

        return {
            "success": True,
            "message": "Documentation generation initiated successfully",
            "data": {
                "workflow_id": workflow_id,
                "estimated_completion": "2-5 minutes",
                "ai_powered": use_real_analysis,
                "mode": "AI-Powered" if use_real_analysis else "Demo Mode"
            }
        }
    except Exception as e:
        # Update workflow status on error
        if workflow_id in workflows:
            workflows[workflow_id].status = "failed"
            workflows[workflow_id].message = f"Generation failed: {str(e)}"
        print(f"❌ Generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed: {str(e)}")

@app.get("/status/{workflow_id}")
async def get_workflow_status(workflow_id: str):
    """
    Get the status of a documentation generation workflow
    """
    if workflow_id not in workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    workflow = workflows[workflow_id]
    
    # Auto-advance agents if still processing
    if workflow.status == "processing" and workflow_id in agent_execution_queue:
        # Simulate agent processing time - advance every 3 seconds
        current_time = datetime.now()
        if workflow.current_agent:
            agent_start_time = workflow.agents[workflow.current_agent].started_at
            if agent_start_time and (current_time - agent_start_time).total_seconds() > 3:
                # Complete current agent and start next
                workflow.agents[workflow.current_agent].status = "completed"
                workflow.agents[workflow.current_agent].progress = 100
                workflow.agents[workflow.current_agent].completed_at = current_time
                await execute_next_agent(workflow_id)
    
    # Convert agents to serializable format
    agents_data = {}
    for agent_id, agent_status in workflow.agents.items():
        agents_data[agent_id] = {
            "agent_id": agent_status.agent_id,
            "agent_name": agent_status.agent_name,
            "status": agent_status.status,
            "progress": agent_status.progress,
            "current_task": agent_status.current_task,
            "started_at": agent_status.started_at.isoformat() if agent_status.started_at else None,
            "completed_at": agent_status.completed_at.isoformat() if agent_status.completed_at else None
        }
    
    return {
        "success": True,
        "data": {
            "workflow_id": workflow.workflow_id,
            "status": workflow.status,
            "progress": workflow.progress,
            "message": workflow.message,
            "current_agent": workflow.current_agent,
            "created_at": workflow.created_at.isoformat(),
            "completed_at": workflow.completed_at.isoformat() if workflow.completed_at else None,
            "agents": agents_data,
            "result": workflow.result
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

@app.get("/debug/ai-status")
async def get_ai_status():
    """Debug endpoint to check AI service status"""
    api_key_set = os.getenv('GEMINI_API_KEY') is not None
    api_key_length = len(os.getenv('GEMINI_API_KEY', ''))
    
    try:
        from src.services.ai_service import ai_service
        ai_enabled = ai_service.enabled if hasattr(ai_service, 'enabled') else False
        ai_error = None
    except Exception as e:
        ai_enabled = False
        ai_error = str(e)
    
    return {
        "success": True,
        "data": {
            "environment": {
                "GEMINI_API_KEY": "SET" if api_key_set else "NOT SET",
                "api_key_length": api_key_length if api_key_set else 0
            },
            "ai_service": {
                "enabled": ai_enabled,
                "error": ai_error
            },
            "real_analysis_enabled": api_key_set
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