"""
Technical Documentation Suite - Main Application Entry Point
Built for the Google Cloud ADK Hackathon
"""

from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import os
import uuid
from datetime import datetime
import shutil
import logging
from pathlib import Path

# Import our agent modules
from src.agents.base_agent import BaseAgent, Message
from src.agents.code_analyzer import CodeAnalyzerAgent
from src.agents.doc_writer import DocumentationWriterAgent
from src.agents.translation_agent import TranslationAgent
from src.agents.orchestrator import (
    DiagramGeneratorAgent, 
    QualityReviewerAgent, 
    ContentOrchestratorAgent, 
    UserFeedbackAgent
)
from src.utils.git_utils import clone_repo
from src.services.github_service import github_service
from src.services.ai_service import AIService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

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

# Mount static files for React frontend
static_directory = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_directory):
    # Mount the React build's static directory to serve CSS, JS, and other assets
    react_static_dir = os.path.join(static_directory, "static")
    if os.path.exists(react_static_dir):
        app.mount("/static", StaticFiles(directory=react_static_dir), name="static")
    else:
        # Fallback to the main static directory if nested structure doesn't exist
        app.mount("/static", StaticFiles(directory=static_directory), name="static")

# Pydantic models
class DocumentationRequest(BaseModel):
    repository_url: str
    project_id: str
    output_formats: List[str] = ["markdown", "html"]
    include_diagrams: bool = True
    target_audience: str = "developers"
    # GitHub authentication for private repos
    github_token: Optional[str] = None
    github_username: Optional[str] = None

class GitHubAuthRequest(BaseModel):
    code: str  # Authorization code from GitHub OAuth
    state: Optional[str] = None

class GitHubRepoRequest(BaseModel):
    github_token: str
    per_page: int = 30
    page: int = 1
    type: str = "all"  # all, owner, public, private, member

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
    ai_powered: bool = False

class FeedbackRequest(BaseModel):
    workflow_id: str
    user_id: Optional[str] = None
    rating: int
    usefulness_score: int
    accuracy_score: int
    completeness_score: int
    comments: Optional[str] = None

class TranslationRequest(BaseModel):
    content: str
    selected_languages: List[str]
    project_context: Optional[Dict[str, Any]] = None

# In-memory storage for demo (in production, this would be in a database)
workflows: Dict[str, WorkflowStatus] = {}
agent_execution_queue: Dict[str, List[str]] = {}  # workflow_id -> list of agent names

# Initialize agents
agents = {
    "code_analyzer": CodeAnalyzerAgent("code_analyzer_01"),
    "doc_writer": DocumentationWriterAgent("doc_writer_01"),
    "translation_agent": TranslationAgent("translation_01"),
    "diagram_generator": DiagramGeneratorAgent("diagram_gen_01"),
    "quality_reviewer": QualityReviewerAgent("quality_reviewer_01"),
    "orchestrator": ContentOrchestratorAgent("orchestrator_01"),
    "feedback_collector": UserFeedbackAgent("feedback_01")
}

async def doc_writer_generate_async(agent, analysis_data, target_audience="developers"):
    """Generate documentation asynchronously"""
    try:
        return await agent._generate_documentation_async(analysis_data, target_audience)
    except Exception as e:
        logger.error(f"Documentation generation failed: {e}")
        raise

def quality_reviewer_score_sync(agent, content, analysis_data):
    """Calculate quality score synchronously"""
    try:
        return agent._calculate_quality_score(content, analysis_data)
    except Exception as e:
        logger.error(f"Quality review failed: {e}")
        return 0.0

@app.get("/api")
async def api_info():
    """API information endpoint"""
    return {
        "message": "Technical Documentation Suite API",
        "version": "1.0.0",
        "description": "Multi-agent system for automated technical documentation generation",
        "hackathon": "Google Cloud ADK Hackathon",
        "endpoints": {
            "health": "/health",
            "generate": "/generate",
            "status": "/status/{workflow_id}",
            "feedback": "/feedback",
            "translation_languages": "/translation/languages",
            "translate": "/translation/translate",
            "github_auth": "/auth/github/config",
            "github_token": "/auth/github/token",
            "github_repos": "/github/repositories",
            "github_validate": "/github/validate-repo"
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
    try:
        agent_names = ["code_analyzer", "doc_writer", "translation_agent", "diagram_generator", "quality_reviewer", "orchestrator", "feedback_collector"]
        
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
        logger.info(f"Successfully initialized {len(agent_names)} agents for workflow {workflow_id}")
        
    except Exception as e:
        logger.error(f"Failed to initialize agents for workflow {workflow_id}: {e}")
        raise Exception(f"Agent initialization failed: {str(e)}")

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
    workflows[workflow_id].progress = min(10 + ((7 - len(agent_execution_queue[workflow_id])) * 12), 90)
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
    Generate comprehensive technical documentation for a GitHub repository
    """
    workflow_id = str(uuid.uuid4())
    
    # Initialize workflow_id in workflows dict early to prevent KeyError
    workflows[workflow_id] = WorkflowStatus(
        workflow_id=workflow_id,
        status="initiated",
        progress=0,
        message="Initializing documentation generation workflow",
        created_at=datetime.now(),
        agents={}
    )
    
    # Check if we should use real AI analysis
    use_real_analysis = os.getenv('GEMINI_API_KEY') is not None
    
    try:
        # Initialize workflow agents
        await initialize_workflow_agents(workflow_id)
        
        # Update status to processing and mark if AI-powered
        workflows[workflow_id].status = "processing"
        workflows[workflow_id].progress = 5
        workflows[workflow_id].message = "Workflow initialized, starting documentation generation"
        
        # Add ai_powered flag to workflow for status endpoint logic
        workflows[workflow_id].ai_powered = use_real_analysis

        # Check if we should use real AI analysis
        if use_real_analysis:
            logger.info("Starting AI-powered documentation generation")
            
            # Repository cloning with proper error handling
            try:
                repo_path = f"/tmp/repo_{workflow_id}"
                clone_cmd = f"git clone {request.repository_url} {repo_path}"
                
                if request.github_token and request.github_username:
                    logger.info("Using GitHub authentication for private repository access")
                    # Handle private repos
                    auth_url = request.repository_url.replace(
                        "https://github.com/", 
                        f"https://{request.github_username}:{request.github_token}@github.com/"
                    )
                    clone_cmd = f"git clone {auth_url} {repo_path}"
                
                exit_code = os.system(clone_cmd)
                if exit_code != 0:
                    raise Exception(f"Failed to clone repository: {request.repository_url}")
                    
                logger.info(f"Repository cloned successfully")
                
            except Exception as e:
                logger.error(f"Repository cloning failed: {e}")
                raise HTTPException(status_code=400, detail=f"Failed to clone repository: {str(e)}")

            try:
                # Update workflow status for AI processing
                workflows[workflow_id].status = "processing"
                workflows[workflow_id].progress = 20
                workflows[workflow_id].message = "Analyzing repository structure"
                
                # Start with code analyzer
                workflows[workflow_id].current_agent = "code_analyzer"
                if "code_analyzer" in workflows[workflow_id].agents:
                    workflows[workflow_id].agents["code_analyzer"].status = "active"
                    workflows[workflow_id].agents["code_analyzer"].started_at = datetime.now()
                    workflows[workflow_id].agents["code_analyzer"].current_task = "Analyzing repository"
                
                logger.info("🔄 Current Agent: code_analyzer (1/7) - Repository Analysis")
                
                code_analysis = agents["code_analyzer"].analyze_repository(repo_path)
                
                # Add request metadata to analysis data for documentation generation
                code_analysis["repository_url"] = request.repository_url
                code_analysis["project_id"] = request.project_id
                
                logger.info(f"Code analysis complete: {len(code_analysis.get('functions', []))} functions, {len(code_analysis.get('classes', []))} classes")

                # Update workflow status
                if "code_analyzer" in workflows[workflow_id].agents:
                    workflows[workflow_id].agents["code_analyzer"].status = "completed"
                    workflows[workflow_id].agents["code_analyzer"].progress = 100
                    workflows[workflow_id].agents["code_analyzer"].completed_at = datetime.now()

                workflows[workflow_id].current_agent = "doc_writer"
                if "doc_writer" in workflows[workflow_id].agents:
                    workflows[workflow_id].agents["doc_writer"].status = "active"
                    workflows[workflow_id].agents["doc_writer"].started_at = datetime.now()
                    workflows[workflow_id].agents["doc_writer"].current_task = "Generating documentation"
                
                logger.info("🔄 Current Agent: doc_writer (2/7) - Documentation Generation")

                # Documentation generation
                workflows[workflow_id].progress = 60
                workflows[workflow_id].message = "Generating comprehensive documentation using AI"
                logger.info("Starting AI documentation generation")
                
                documentation = await doc_writer_generate_async(
                    agents["doc_writer"], 
                    code_analysis, 
                    request.target_audience
                )
                
                logger.info(f"Documentation generated: {len(documentation)} characters")

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
                
                logger.info("🔄 Current Agent: diagram_generator (3/7) - Diagram Creation")
            
                # Generate diagrams
                workflows[workflow_id].progress = 80
                workflows[workflow_id].message = "Creating architectural diagrams"
                logger.info("Generating diagrams")
                
                diagrams = agents["diagram_generator"]._generate_architecture_diagram(code_analysis)
                logger.info("Diagrams generated successfully")
                
                # Complete diagram generator, start translation agent
                if "diagram_generator" in workflows[workflow_id].agents:
                    workflows[workflow_id].agents["diagram_generator"].status = "completed"
                    workflows[workflow_id].agents["diagram_generator"].progress = 100
                    workflows[workflow_id].agents["diagram_generator"].completed_at = datetime.now()

                workflows[workflow_id].current_agent = "translation_agent"
                if "translation_agent" in workflows[workflow_id].agents:
                    workflows[workflow_id].agents["translation_agent"].status = "active"
                    workflows[workflow_id].agents["translation_agent"].started_at = datetime.now()
                    workflows[workflow_id].agents["translation_agent"].current_task = "Generating translations"

                logger.info("🔄 Current Agent: translation_agent (4/7) - Translation")

                # Generate translations
                workflows[workflow_id].progress = 85
                workflows[workflow_id].message = "Generating translations"
                logger.info("Generating translations")
                
                translations = {}
                translation_agent = agents["translation_agent"]
                supported_languages = list(translation_agent.supported_languages.keys())
                
                for lang_key in supported_languages:
                    try:
                        translated_content = await translation_agent._perform_translation(
                            documentation, 
                            translation_agent.supported_languages[lang_key], 
                            code_analysis
                        )
                        translations[lang_key] = {
                            "content": translated_content,
                            "language": translation_agent.supported_languages[lang_key]
                        }
                    except Exception as e:
                        logger.warning(f"Translation to {lang_key} failed: {e}")
                        translations[lang_key] = {
                            "content": f"Translation to {translation_agent.supported_languages[lang_key]['name']} failed. Original content:\n\n{documentation}",
                            "language": translation_agent.supported_languages[lang_key]
                        }

                logger.info(f"Translations generated for {len(translations)} languages")

                # Complete translation agent, start quality reviewer  
                if "translation_agent" in workflows[workflow_id].agents:
                    workflows[workflow_id].agents["translation_agent"].status = "completed"
                    workflows[workflow_id].agents["translation_agent"].progress = 100
                    workflows[workflow_id].agents["translation_agent"].completed_at = datetime.now()

                workflows[workflow_id].current_agent = "quality_reviewer"
                if "quality_reviewer" in workflows[workflow_id].agents:
                    workflows[workflow_id].agents["quality_reviewer"].status = "active"
                    workflows[workflow_id].agents["quality_reviewer"].started_at = datetime.now()
                    workflows[workflow_id].agents["quality_reviewer"].current_task = "Reviewing quality"

                logger.info("🔄 Current Agent: quality_reviewer (5/7) - Quality Review")

                # Quality review
                workflows[workflow_id].progress = 95
                workflows[workflow_id].message = "Reviewing documentation quality"
                logger.info("Starting quality review")
                
                quality = quality_reviewer_score_sync(agents["quality_reviewer"], documentation, code_analysis)
                logger.info(f"Quality review complete: {quality}")

                # Complete quality reviewer
                if "quality_reviewer" in workflows[workflow_id].agents:
                    workflows[workflow_id].agents["quality_reviewer"].status = "completed"
                    workflows[workflow_id].agents["quality_reviewer"].progress = 100
                    workflows[workflow_id].agents["quality_reviewer"].completed_at = datetime.now()

                # Cleanup
                if os.path.exists(repo_path):
                    shutil.rmtree(repo_path)
                logger.info("Repository cleanup completed")

                # Store real results
                workflows[workflow_id].status = "completed"
                workflows[workflow_id].progress = 100
                workflows[workflow_id].message = "AI-powered documentation generation completed successfully"
                workflows[workflow_id].completed_at = datetime.now()
                workflows[workflow_id].current_agent = None
                workflows[workflow_id].result = {
                    "documentation": documentation,
                    "translations": translations,
                    "diagrams": diagrams,
                    "quality": quality,
                    "analysis": code_analysis,
                    "ai_generated": True
                }

                logger.info("Real AI workflow completed successfully")
                
            except Exception as e:
                # If real analysis fails, show the error and fall back to demo mode
                error_msg = str(e)
                logger.error(f"Real analysis failed: {error_msg}")
                workflows[workflow_id].message = f"AI analysis failed ({error_msg}), switching to demo mode"
                workflows[workflow_id].progress = 15
                
                # Reset agents and use demo mode
                await initialize_workflow_agents(workflow_id)
                await execute_next_agent(workflow_id)
        else:
            # Demo mode - simulate workflow
            logger.info("Running in demo mode - GEMINI_API_KEY not set")
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
        error_message = str(e)
        if workflow_id in workflows:
            workflows[workflow_id].status = "failed"
            workflows[workflow_id].message = f"Generation failed: {error_message}"
        logger.error(f"Generation failed for workflow {workflow_id}: {error_message}")
        raise HTTPException(status_code=500, detail=f"Failed: {error_message}")

@app.get("/status/{workflow_id}")
async def get_workflow_status(workflow_id: str):
    """
    Get the status of a documentation generation workflow
    """
    if workflow_id not in workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    workflow = workflows[workflow_id]
    
    # Only auto-advance agents for demo mode workflows (not real AI workflows)
    # Real AI workflows manage their own progression
    if (workflow.status == "processing" and 
        workflow_id in agent_execution_queue and 
        not getattr(workflow, 'ai_powered', False)):
        
        # Simulate agent processing time - advance every 3 seconds (demo mode only)
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

@app.get("/translation/languages")
async def get_supported_languages():
    """Get list of supported languages for translation"""
    try:
        translation_agent = agents["translation_agent"]
        language_options = translation_agent.get_language_selection_options()
        
        return {
            "success": True,
            "data": {
                "languages": language_options,
                "total_count": len(language_options)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get supported languages: {str(e)}")

@app.post("/translation/translate")
async def translate_documentation(request: TranslationRequest):
    """Translate documentation to selected languages"""
    try:
        if not request.content:
            raise HTTPException(status_code=400, detail="Content is required for translation")
        
        if not request.selected_languages:
            raise HTTPException(status_code=400, detail="At least one language must be selected")
        
        translation_agent = agents["translation_agent"]
        
        # Create message for translation agent
        translation_message = Message(
            type="translate_documentation",
            data={
                "content": request.content,
                "languages": request.selected_languages,
                "project_context": request.project_context or {}
            },
            sender="api",
            recipient=translation_agent.agent_id
        )
        
        # Process translation
        response = await translation_agent.handle_message(translation_message)
        
        if response.type == "translation_error":
            raise HTTPException(status_code=400, detail=response.data.get("error", "Translation failed"))
        
        return {
            "success": True,
            "data": response.data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")

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

@app.get("/auth/github/config")
async def get_github_config():
    """Get GitHub OAuth configuration for frontend"""
    return {
        "success": True,
        "data": {
            "client_id": github_service.client_id,
            "oauth_configured": github_service.is_oauth_configured(),
            "redirect_uri": f"{os.getenv('APP_URL', 'http://localhost:3000')}/auth/callback",
            "scope": "repo,user:email"
        }
    }

@app.post("/auth/github/token")
async def exchange_github_token(request: GitHubAuthRequest):
    """Exchange GitHub OAuth code for access token"""
    try:
        if not github_service.is_oauth_configured():
            raise HTTPException(
                status_code=503, 
                detail="GitHub OAuth not configured. Set GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET environment variables."
            )
        
        # Exchange code for token
        token_response = github_service.exchange_code_for_token(request.code)
        
        if "access_token" not in token_response:
            raise HTTPException(status_code=400, detail="Failed to get access token from GitHub")
        
        access_token = token_response["access_token"]
        
        # Get user info
        user_info = github_service.get_user_info(access_token)
        
        return {
            "success": True,
            "data": {
                "access_token": access_token,
                "token_type": token_response.get("token_type", "bearer"),
                "scope": token_response.get("scope", ""),
                "user": {
                    "id": user_info["id"],
                    "login": user_info["login"],
                    "name": user_info.get("name"),
                    "email": user_info.get("email"),
                    "avatar_url": user_info.get("avatar_url"),
                    "public_repos": user_info.get("public_repos", 0),
                    "private_repos": user_info.get("total_private_repos", 0)
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"GitHub authentication failed: {str(e)}")

@app.post("/github/repositories")
async def list_github_repositories(request: GitHubRepoRequest):
    """List repositories for authenticated user"""
    try:
        repos = github_service.list_repositories(
            token=request.github_token,
            repo_type=request.type,
            per_page=request.per_page,
            page=request.page
        )
        
        return {
            "success": True,
            "data": repos
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch repositories: {str(e)}")

@app.post("/github/validate-repo")
async def validate_github_repository(request: Dict[str, str]):
    """Validate repository access for the user"""
    try:
        github_token = request.get("github_token")
        repository_url = request.get("repository_url")
        
        if not github_token or not repository_url:
            raise HTTPException(status_code=400, detail="github_token and repository_url are required")
        
        validation_result = github_service.validate_repository_access(github_token, repository_url)
        
        return {
            "success": True,
            "data": validation_result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Repository validation failed: {str(e)}")

@app.get("/github/user")
async def get_github_user(token: str):
    """Get GitHub user information"""
    try:
        user_info = github_service.get_user_info(token)
        
        return {
            "success": True,
            "data": {
                "user": {
                    "id": user_info["id"],
                    "login": user_info["login"],
                    "name": user_info.get("name"),
                    "email": user_info.get("email"),
                    "avatar_url": user_info.get("avatar_url"),
                    "public_repos": user_info.get("public_repos", 0),
                    "private_repos": user_info.get("total_private_repos", 0),
                    "created_at": user_info.get("created_at"),
                    "bio": user_info.get("bio")
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user info: {str(e)}")

# Catch-all route to serve React app for frontend routes  
@app.get("/{path:path}")
async def serve_frontend(path: str):
    """Serve React frontend for all non-API routes"""
    static_directory = os.path.join(os.path.dirname(__file__), "static")
    index_file = os.path.join(static_directory, "index.html")
    
    # Don't intercept API routes or static file routes
    if path.startswith(("api/", "docs", "openapi.json", "health", "generate", "status", "feedback", "workflows", "agents", "debug", "static/")):
        # Let FastAPI handle these normally - this shouldn't normally be reached due to route precedence
        raise HTTPException(status_code=404, detail="Not found")
    
    # For all other routes (including root), serve the React app's index.html
    if os.path.exists(index_file):
        return FileResponse(index_file)
    else:
        # Fallback if frontend files are not available
        return {
            "app": "Technical Documentation Suite",
            "version": "1.0.0",
            "status": "frontend_missing",
            "note": "React frontend build files not found. Please build the frontend first.",
            "api_docs": "/docs"
        }

if __name__ == "__main__":
    # Get port from environment variable (for Cloud Run)
    port = int(os.getenv("PORT", 8080))
    
    # Startup logging
    logger.info("🚀 Starting Technical Documentation Suite API")
    logger.info(f"📋 Version: 1.0.0")
    logger.info(f"🌐 Port: {port}")
    logger.info(f"🏆 Built for: Google Cloud ADK Hackathon")
    
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info") 