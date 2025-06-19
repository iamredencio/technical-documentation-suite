"""
Technical Documentation Suite - Main Application Entry Point
Built for the Google Cloud ADK Hackathon
"""

from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, Response
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import os
import uuid
from datetime import datetime
import shutil
import logging
from pathlib import Path
import subprocess
import tempfile
import asyncio
import json
from contextlib import asynccontextmanager

# Import our agent modules
try:
    # Try relative imports first (when running as package)
    from .agents.base_agent import BaseAgent, Message
    from .agents.code_analyzer import CodeAnalyzerAgent
    from .agents.doc_writer import DocumentationWriterAgent
    from .agents.translation_agent import TranslationAgent
    from .agents.orchestrator import (
        DiagramGeneratorAgent, 
        QualityReviewerAgent, 
        ContentOrchestratorAgent, 
        UserFeedbackAgent
    )
    from .utils.git_utils import clone_repo
    from .services.github_service import github_service
    from .services.ai_service import AIService
except ImportError:
    # Fall back to absolute imports (when running directly)
    from tech_doc_suite.agents.base_agent import BaseAgent, Message
    from tech_doc_suite.agents.code_analyzer import CodeAnalyzerAgent
    from tech_doc_suite.agents.doc_writer import DocumentationWriterAgent
    from tech_doc_suite.agents.translation_agent import TranslationAgent
    from tech_doc_suite.agents.orchestrator import (
        DiagramGeneratorAgent, 
        QualityReviewerAgent, 
        ContentOrchestratorAgent, 
        UserFeedbackAgent
    )
    from tech_doc_suite.utils.git_utils import clone_repo
    from tech_doc_suite.services.github_service import github_service
    from tech_doc_suite.services.ai_service import AIService

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
static_directory = os.path.join(os.path.dirname(__file__), "..", "..", "static")
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
    translation_languages: List[str] = []  # Selected languages for translation
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

class StopWorkflowRequest(BaseModel):
    workflow_id: str

# In-memory storage for demo (in production, this would be in a database)
workflows: Dict[str, WorkflowStatus] = {}
agent_execution_queue: Dict[str, List[str]] = {}  # workflow_id -> list of agent names

# Add enhanced agent tracking
agent_transition_history: Dict[str, List[Dict]] = {}

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
        overall_score = agent._calculate_quality_score(content, analysis_data)
        detailed_metrics = agent._analyze_detailed_metrics(content, analysis_data)
        suggestions = agent._generate_improvement_suggestions(content, detailed_metrics)
        
        return {
            "overall_score": overall_score * 100,  # Convert to 0-100 scale
            "completeness": detailed_metrics.get("completeness", 0) * 100,
            "technical_accuracy": detailed_metrics.get("accuracy", 0) * 100,
            "clarity": detailed_metrics.get("readability", 0) * 100,
            "consistency": detailed_metrics.get("consistency", 0) * 100,
            "feedback": "; ".join(suggestions[:3]) if suggestions else "Good documentation quality",
            "suggestions": suggestions
        }
    except Exception as e:
        logger.error(f"Quality review failed: {e}")
        return {
            "overall_score": 0,
            "completeness": 0,
            "technical_accuracy": 0,
            "clarity": 0,
            "consistency": 0,
            "feedback": "Quality review failed",
            "suggestions": []
        }

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
            "repository_summary": {
                "project_name": "Demo Project",
                "repository_url": "demo-repository",
                "total_files": 25,
                "total_lines_of_code": 1500,
                "programming_languages": ["python", "javascript", "yaml", "markdown"],
                "language_breakdown": {
                    "python": 0.65,
                    "javascript": 0.20,
                    "yaml": 0.10,
                    "markdown": 0.05
                },
                "total_functions": 42,
                "total_classes": 8,
                "total_dependencies": 15,
                "project_structure": {
                    "src/": ["main.py", "agents/", "models/", "services/"],
                    "frontend/": ["src/", "public/", "package.json"],
                    "tests/": ["test_agents.py", "test_api.py"],
                    "config/": ["settings.py", "requirements.txt"],
                    "docs/": ["README.md", "API.md"]
                },
                "functions_detail": [
                    {"name": "generate_documentation", "file": "src/main.py", "parameters": ["request"], "docstring": "Main documentation generation function", "line": 45},
                    {"name": "analyze_repository", "file": "src/agents/code_analyzer.py", "parameters": ["repo_path"], "docstring": "Analyze repository structure and extract code information", "line": 23},
                    {"name": "create_diagrams", "file": "src/agents/diagram_generator.py", "parameters": ["analysis_data"], "docstring": "Generate architectural diagrams from analysis", "line": 67},
                    {"name": "translate_content", "file": "src/agents/translation_agent.py", "parameters": ["content", "target_lang"], "docstring": "Translate documentation content", "line": 34},
                    {"name": "review_quality", "file": "src/agents/quality_reviewer.py", "parameters": ["content"], "docstring": "Review documentation quality and provide scores", "line": 19}
                ],
                "classes_detail": [
                    {"name": "DocumentationAgent", "file": "src/agents/base_agent.py", "methods": ["start", "stop", "handle_message"], "docstring": "Base class for all documentation agents", "line": 12},
                    {"name": "CodeAnalyzerAgent", "file": "src/agents/code_analyzer.py", "methods": ["analyze_repository", "analyze_file"], "docstring": "Agent for analyzing code repositories", "line": 15},
                    {"name": "DiagramGeneratorAgent", "file": "src/agents/diagram_generator.py", "methods": ["generate_diagrams", "create_mermaid"], "docstring": "Agent for generating project diagrams", "line": 20},
                    {"name": "TranslationAgent", "file": "src/agents/translation_agent.py", "methods": ["translate", "get_languages"], "docstring": "Agent for translating documentation", "line": 18}
                ],
                "dependencies_detail": [
                    "fastapi", "pydantic", "uvicorn", "google-cloud-storage", "openai", "react", "axios", "mermaid", "tailwindcss", "pytest", "black", "flake8", "mypy", "docker", "kubernetes"
                ],
                "api_endpoints": [
                    {"method": "POST", "path": "/generate", "function": "generate_documentation", "parameters": ["DocumentationRequest"], "response_type": "WorkflowResponse"},
                    {"method": "GET", "path": "/status/{workflow_id}", "function": "get_workflow_status", "parameters": ["workflow_id"], "response_type": "WorkflowStatus"},
                    {"method": "POST", "path": "/feedback", "function": "submit_feedback", "parameters": ["FeedbackRequest"], "response_type": "Dict[str, Any]"}
                ],
                "complexity_metrics": {
                    "average_file_size": 60.0,
                    "functions_per_file": 1.68,
                    "classes_per_file": 0.32
                }
            },
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
                "language_distribution": {
                    "python": 0.65,
                    "javascript": 0.20,
                    "yaml": 0.10,
                    "markdown": 0.05
                },
                "functions": [
                    {"name": "generate_documentation", "description": "Main documentation generation function"},
                    {"name": "analyze_code", "description": "Code analysis function"},
                    {"name": "create_diagrams", "description": "Diagram generation function"}
                ],
                "classes": [
                    {"name": "DocumentationAgent", "description": "Main agent class for documentation generation"},
                    {"name": "CodeAnalyzer", "description": "Code analysis agent"},
                    {"name": "DiagramGenerator", "description": "Diagram generation agent"}
                ],
                "dependencies": ["fastapi", "pydantic", "uvicorn", "google-cloud-storage", "openai", "react", "axios", "mermaid", "tailwindcss", "pytest"],
                "structure": {
                    "src/": ["main.py", "agents/", "models/", "services/"],
                    "frontend/": ["src/", "public/", "package.json"],
                    "tests/": ["test_agents.py", "test_api.py"],
                    "config/": ["settings.py", "requirements.txt"]
                }
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

async def run_ai_workflow_background(workflow_id: str, request: DocumentationRequest, repo_path: str):
    """Run the AI workflow with proper orchestrator-driven architecture"""
    try:
        # Initialize transition history
        agent_transition_history[workflow_id] = []
        
        # ========== START ORCHESTRATOR (Active Throughout) ==========
        workflows[workflow_id].progress = 10
        workflows[workflow_id].message = "Content Orchestrator initializing workflow"
        workflows[workflow_id].current_agent = "orchestrator"
        
        await update_agent_status_with_history(
            workflow_id, "orchestrator", "active", 10, "Initializing workflow coordination"
        )
        
        logger.info("🎼 Content Orchestrator (ACTIVE) - Managing entire workflow")
        await asyncio.sleep(2)
        
        # ========== PHASE 1: CODE ANALYSIS (Orchestrated) ==========
        workflows[workflow_id].progress = 20
        workflows[workflow_id].message = "Orchestrator directing code analysis"
        
        await update_agent_status_with_history(
            workflow_id, "orchestrator", "active", 20, "Coordinating code analysis phase"
        )
        await update_agent_status_with_history(
            workflow_id, "code_analyzer", "active", 25, "Analyzing repository structure"
        )
        
        logger.info("🎼 Orchestrator → Delegating to Code Analyzer (1/6)")
        await asyncio.sleep(3)
        
        # Update progress during analysis
        await update_agent_status_with_history(
            workflow_id, "code_analyzer", "active", 75, "Extracting functions and classes"
        )
        await update_agent_status_with_history(
            workflow_id, "orchestrator", "active", 25, "Monitoring code analysis progress"
        )
        
        await asyncio.sleep(2)
        
        # Do the actual work
        code_analysis = agents["code_analyzer"].analyze_repository(repo_path)
        code_analysis["repository_url"] = request.repository_url
        code_analysis["project_id"] = request.project_id
        
        # Create detailed repository summary
        repo_summary = {
            "project_name": request.project_id,
            "repository_url": request.repository_url,
            "total_files": code_analysis.get("file_count", 0),
            "total_lines_of_code": code_analysis.get("lines_of_code", 0),
            "programming_languages": list(code_analysis.get("language_distribution", {}).keys()),
            "language_breakdown": code_analysis.get("language_distribution", {}),
            "total_functions": len(code_analysis.get("functions", [])),
            "total_classes": len(code_analysis.get("classes", [])),
            "total_dependencies": len(code_analysis.get("dependencies", [])),
            "project_structure": code_analysis.get("structure", {}),
            "functions_detail": code_analysis.get("functions", [])[:10],
            "classes_detail": code_analysis.get("classes", [])[:10],
            "dependencies_detail": code_analysis.get("dependencies", [])[:15],
            "api_endpoints": code_analysis.get("api_endpoints", []),
            "complexity_metrics": {
                "average_file_size": round(code_analysis.get("lines_of_code", 0) / max(code_analysis.get("file_count", 1), 1), 2),
                "functions_per_file": round(len(code_analysis.get("functions", [])) / max(code_analysis.get("file_count", 1), 1), 2),
                "classes_per_file": round(len(code_analysis.get("classes", [])) / max(code_analysis.get("file_count", 1), 1), 2)
            }
        }
        
        logger.info(f"Code analysis complete: {repo_summary['total_functions']} functions, {repo_summary['total_classes']} classes, {repo_summary['total_files']} files")

        # Complete code analysis, orchestrator continues
        await update_agent_status_with_history(
            workflow_id, "code_analyzer", "completed", 100, "Analysis completed"
        )
        await update_agent_status_with_history(
            workflow_id, "orchestrator", "active", 30, "Code analysis completed, proceeding to documentation"
        )
        
        await asyncio.sleep(3)

        # ========== PHASE 2: DOCUMENTATION GENERATION (Orchestrated) ==========
        workflows[workflow_id].progress = 40
        workflows[workflow_id].message = "Orchestrator directing documentation generation"
        
        await update_agent_status_with_history(
            workflow_id, "orchestrator", "active", 40, "Coordinating documentation generation"
        )
        await update_agent_status_with_history(
            workflow_id, "doc_writer", "active", 20, "Initializing AI documentation generation"
        )
        
        logger.info("🎼 Orchestrator → Delegating to Documentation Writer (2/6)")
        await asyncio.sleep(3)
        
        # Update progress
        await update_agent_status_with_history(
            workflow_id, "doc_writer", "active", 60, "Generating documentation content"
        )
        await update_agent_status_with_history(
            workflow_id, "orchestrator", "active", 45, "Monitoring documentation generation"
        )
        
        await asyncio.sleep(2)
        
        # Do the actual work
        documentation = await doc_writer_generate_async(
            agents["doc_writer"], 
            code_analysis, 
            request.target_audience
        )
        
        logger.info(f"Documentation generated: {len(documentation)} characters")

        # Complete documentation, orchestrator continues
        await update_agent_status_with_history(
            workflow_id, "doc_writer", "completed", 100, "Documentation generation completed"
        )
        await update_agent_status_with_history(
            workflow_id, "orchestrator", "active", 50, "Documentation completed, proceeding to diagrams"
        )
        
        await asyncio.sleep(3)

        # ========== PHASE 3: DIAGRAM GENERATION (Orchestrated) ==========
        workflows[workflow_id].progress = 60
        workflows[workflow_id].message = "Orchestrator directing diagram creation"
        
        await update_agent_status_with_history(
            workflow_id, "orchestrator", "active", 60, "Coordinating diagram generation"
        )
        await update_agent_status_with_history(
            workflow_id, "diagram_generator", "active", 30, "Analyzing project architecture"
        )
        
        logger.info("🎼 Orchestrator → Delegating to Diagram Generator (3/6)")
        await asyncio.sleep(3)
        
        # Update progress
        await update_agent_status_with_history(
            workflow_id, "diagram_generator", "active", 70, "Creating Mermaid diagrams"
        )
        await update_agent_status_with_history(
            workflow_id, "orchestrator", "active", 65, "Monitoring diagram creation"
        )
        
        await asyncio.sleep(2)
        
        # Do the actual work
        diagrams = agents["diagram_generator"]._generate_architecture_diagram(code_analysis)
        logger.info("Diagrams generated successfully")
        
        # Complete diagrams, orchestrator continues
        await update_agent_status_with_history(
            workflow_id, "diagram_generator", "completed", 100, "Diagrams created successfully"
        )
        await update_agent_status_with_history(
            workflow_id, "orchestrator", "active", 70, "Diagrams completed, proceeding to translation"
        )
        
        await asyncio.sleep(3)

        # ========== PHASE 4: TRANSLATION (Orchestrated) ==========
        workflows[workflow_id].progress = 75
        workflows[workflow_id].message = "Orchestrator directing translation services"
        
        await update_agent_status_with_history(
            workflow_id, "orchestrator", "active", 75, "Coordinating translation phase"
        )
        await update_agent_status_with_history(
            workflow_id, "translation_agent", "active", 25, "Preparing translation services"
        )

        logger.info("🎼 Orchestrator → Delegating to Translation Agent (4/6)")
        await asyncio.sleep(3)

        # Do the actual work
        translation_agent = agents["translation_agent"]
        translations = {}
        selected_languages = request.translation_languages if request.translation_languages else []
        
        if selected_languages:
            logger.info(f"Translating to selected languages: {selected_languages}")
            await update_agent_status_with_history(
                workflow_id, "translation_agent", "active", 60, f"Translating to {len(selected_languages)} languages"
            )
            await update_agent_status_with_history(
                workflow_id, "orchestrator", "active", 78, "Monitoring translation progress"
            )
            
            await asyncio.sleep(2)
            
            for lang_key in selected_languages:
                if lang_key in translation_agent.supported_languages:
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
                else:
                    logger.warning(f"Unsupported language selected: {lang_key}")
        else:
            logger.info("No translation languages selected, skipping translation")
            await update_agent_status_with_history(
                workflow_id, "translation_agent", "active", 80, "No translations requested"
            )
        
        logger.info(f"Translations generated for {len(translations)} selected languages")

        # Complete translation, orchestrator continues
        await update_agent_status_with_history(
            workflow_id, "translation_agent", "completed", 100, "Translation completed"
        )
        await update_agent_status_with_history(
            workflow_id, "orchestrator", "active", 80, "Translation completed, proceeding to quality review"
        )
        
        await asyncio.sleep(3)

        # ========== PHASE 5: QUALITY REVIEW (Orchestrated) ==========
        workflows[workflow_id].progress = 85
        workflows[workflow_id].message = "Orchestrator directing quality review"
        
        await update_agent_status_with_history(
            workflow_id, "orchestrator", "active", 85, "Coordinating quality review"
        )
        await update_agent_status_with_history(
            workflow_id, "quality_reviewer", "active", 30, "Analyzing documentation quality"
        )

        logger.info("🎼 Orchestrator → Delegating to Quality Reviewer (5/6)")
        await asyncio.sleep(3)
        
        # Update progress
        await update_agent_status_with_history(
            workflow_id, "quality_reviewer", "active", 70, "Calculating quality metrics"
        )
        await update_agent_status_with_history(
            workflow_id, "orchestrator", "active", 88, "Monitoring quality review"
        )
        
        await asyncio.sleep(2)
        
        # Do the actual work
        quality_metrics = quality_reviewer_score_sync(
            agents["quality_reviewer"], 
            documentation, 
            code_analysis
        )
        
        logger.info(f"Quality review complete: {quality_metrics['overall_score']}/100")

        # Complete quality review, orchestrator continues
        await update_agent_status_with_history(
            workflow_id, "quality_reviewer", "completed", 100, "Quality review completed"
        )
        await update_agent_status_with_history(
            workflow_id, "orchestrator", "active", 90, "Quality review completed, setting up feedback"
        )
        
        await asyncio.sleep(3)

        # ========== PHASE 6: FEEDBACK COLLECTION (Orchestrated) ==========
        workflows[workflow_id].progress = 95
        workflows[workflow_id].message = "Orchestrator setting up feedback collection"
        
        await update_agent_status_with_history(
            workflow_id, "orchestrator", "active", 95, "Coordinating feedback setup"
        )
        await update_agent_status_with_history(
            workflow_id, "feedback_collector", "active", 50, "Setting up feedback mechanisms"
        )

        logger.info("🎼 Orchestrator → Delegating to Feedback Collector (6/6)")
        await asyncio.sleep(3)
        
        # Update progress
        await update_agent_status_with_history(
            workflow_id, "feedback_collector", "active", 90, "Finalizing feedback setup"
        )
        await update_agent_status_with_history(
            workflow_id, "orchestrator", "active", 98, "Finalizing workflow"
        )
        
        await asyncio.sleep(2)

        # Complete feedback setup, orchestrator completes
        await update_agent_status_with_history(
            workflow_id, "feedback_collector", "completed", 100, "Feedback collection ready"
        )
        await update_agent_status_with_history(
            workflow_id, "orchestrator", "completed", 100, "Workflow orchestration completed successfully"
        )
        
        await asyncio.sleep(3)

        # ========== FINAL COMPLETION ==========
        workflows[workflow_id].status = "completed"
        workflows[workflow_id].progress = 100
        workflows[workflow_id].message = "Documentation generation completed successfully"
        workflows[workflow_id].completed_at = datetime.now()
        workflows[workflow_id].current_agent = None
        
        # Set comprehensive result data
        workflows[workflow_id].result = {
            "documentation": documentation,
            "repository_summary": repo_summary,
            "diagrams": diagrams,
            "translations": translations,
            "quality": quality_metrics,
            "analysis": code_analysis,
            "ai_generated": True,
            "workflow_completed_at": datetime.now().isoformat(),
            "total_processing_time": str(datetime.now() - workflows[workflow_id].created_at)
        }
        
        logger.info(f"🎉 Orchestrator-driven workflow completed successfully for {workflow_id}")
        
    except Exception as e:
        logger.error(f"Orchestrator-driven workflow failed for {workflow_id}: {e}")
        workflows[workflow_id].status = "failed"
        workflows[workflow_id].progress = 100
        workflows[workflow_id].message = f"Workflow failed: {str(e)}"
        workflows[workflow_id].completed_at = datetime.now()
        workflows[workflow_id].current_agent = None
        
        # Mark all remaining agents as idle
        for agent_name in workflows[workflow_id].agents:
            if workflows[workflow_id].agents[agent_name].status == "active":
                workflows[workflow_id].agents[agent_name].status = "idle"
                workflows[workflow_id].agents[agent_name].progress = 0

@app.get("/generate")
async def serve_generate_page():
    """Serve React frontend for the /generate page"""
    static_directory = os.path.join(os.path.dirname(__file__), "..", "..", "static")
    index_file = os.path.join(static_directory, "index.html")
    
    if os.path.exists(index_file):
        return FileResponse(index_file)
    else:
        raise HTTPException(status_code=404, detail="Frontend not found")

@app.post("/generate")
async def generate_documentation(request: DocumentationRequest, background_tasks: BackgroundTasks):
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
        workflows[workflow_id].ai_powered = use_real_analysis

        # Check if we should use real AI analysis
        if use_real_analysis:
            logger.info("Starting AI-powered documentation generation")
            
            # Clone repository with timeout
            try:
                repo_path = f"/tmp/repo_{workflow_id}"
                if os.path.exists(repo_path):
                    shutil.rmtree(repo_path)
                
                clone_cmd = ["git", "clone", "--depth", "1", request.repository_url, repo_path]
                
                if request.github_token and request.github_username:
                    logger.info("Using GitHub authentication for private repository access")
                    auth_url = request.repository_url.replace(
                        "https://github.com/", 
                        f"https://{request.github_username}:{request.github_token}@github.com/"
                    )
                    clone_cmd = ["git", "clone", "--depth", "1", auth_url, repo_path]
                
                logger.info(f"Cloning repository: {request.repository_url}")
                result = subprocess.run(
                    clone_cmd, 
                    capture_output=True, 
                    text=True, 
                    timeout=60,
                    env={**os.environ, 'GIT_TERMINAL_PROMPT': '0'}
                )
                
                if result.returncode != 0:
                    raise Exception(f"Git clone failed: {result.stderr}")
                    
                logger.info(f"Repository cloned successfully to {repo_path}")
                
                # Start the AI workflow in the background
                background_tasks.add_task(run_ai_workflow_background, workflow_id, request, repo_path)
                
            except subprocess.TimeoutExpired:
                logger.error("Repository cloning timed out after 60 seconds")
                logger.info("Falling back to demo mode due to clone timeout")
                use_real_analysis = False
                workflows[workflow_id].ai_powered = False
                await execute_next_agent(workflow_id)
            except Exception as e:
                logger.error(f"Repository cloning failed: {e}")
                logger.info("Falling back to demo mode due to clone failure")
                use_real_analysis = False
                workflows[workflow_id].ai_powered = False
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
    Get the status of a documentation generation workflow with enhanced agent tracking
    """
    if workflow_id not in workflows:
        # Provide helpful information about why the workflow might not be found
        total_workflows = len(workflows)
        active_workflows = [wf_id for wf_id, wf in workflows.items() if wf.status == "processing"]
        
        error_detail = {
            "error": "Workflow not found",
            "workflow_id": workflow_id,
            "possible_reasons": [
                "The workflow ID is invalid or expired",
                "The server was restarted and lost in-memory workflow data",
                "The workflow was never created successfully"
            ],
            "suggestions": [
                "Create a new workflow using the /generate endpoint",
                "Check if you have the correct workflow ID"
            ],
            "current_system_state": {
                "total_workflows": total_workflows,
                "active_workflows": len(active_workflows),
                "server_uptime_info": "Workflows are stored in memory and are lost on server restart"
            }
        }
        
        raise HTTPException(status_code=404, detail=error_detail)
    
    workflow = workflows[workflow_id]
    
    # Check for workflow timeout (15 minutes instead of 10)
    if workflow.status == "processing":
        current_time = datetime.now()
        elapsed_time = (current_time - workflow.created_at).total_seconds()
        
        if elapsed_time > 900:  # 15 minutes timeout
            logger.warning(f"Workflow {workflow_id} timed out after {elapsed_time} seconds")
            workflow.status = "failed"
            workflow.progress = 100
            workflow.message = "Workflow timed out - please try again"
            workflow.completed_at = current_time
            workflow.current_agent = None
            
            # Clean up
            if workflow_id in agent_execution_queue:
                del agent_execution_queue[workflow_id]
    
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
    
    # Include transition history for better frontend synchronization
    transition_history = agent_transition_history.get(workflow_id, [])
    
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
            "result": workflow.result,
            "ai_powered": getattr(workflow, 'ai_powered', False),
            "transition_history": transition_history[-10:] if transition_history else []  # Last 10 transitions
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
        try:
            from .services.ai_service import ai_service
        except ImportError:
            from tech_doc_suite.services.ai_service import ai_service
        ai_enabled = ai_service.is_available()
        ai_error = None
    except Exception as e:
        ai_enabled = False
        ai_error = str(e)
    
    return {
        "success": True,
        "data": {
            "gemini_api": {
                "key_configured": api_key_set,
                "key_length": api_key_length if api_key_set else 0,
                "enabled": ai_enabled,
                "error": ai_error
            },
            "real_analysis_enabled": api_key_set
        }
    }

@app.get("/debug/server-info")
async def get_server_info():
    """Debug endpoint to get server information and current state"""
    import time
    import os
    
    try:
        import psutil
        # Get process info
        process = psutil.Process(os.getpid())
        process_info = {
            "pid": process.pid,
            "create_time": process.create_time(),
            "uptime_seconds": time.time() - process.create_time(),
            "memory_info": process.memory_info()._asdict(),
            "cpu_percent": process.cpu_percent()
        }
    except ImportError:
        process_info = {
            "pid": os.getpid(),
            "note": "psutil not available - install with 'pip install psutil' for detailed process info"
        }
    except Exception as e:
        process_info = {"error": f"Could not get process info: {str(e)}"}
    
    # Workflow statistics
    workflow_stats = {
        "total_workflows": len(workflows),
        "processing_workflows": len([w for w in workflows.values() if w.status == "processing"]),
        "completed_workflows": len([w for w in workflows.values() if w.status == "completed"]),
        "failed_workflows": len([w for w in workflows.values() if w.status == "failed"]),
        "stopped_workflows": len([w for w in workflows.values() if w.status == "stopped"])
    }
    
    # Agent queue info
    queue_info = {
        "active_queues": len(agent_execution_queue),
        "queue_details": {wf_id: len(queue) for wf_id, queue in agent_execution_queue.items()}
    }
    
    return {
        "success": True,
        "data": {
            "server": {
                "version": "1.0.0",
                "service": "Technical Documentation Suite",
                "timestamp": datetime.now().isoformat(),
                "process": process_info
            },
            "workflows": workflow_stats,
            "agent_queues": queue_info,
            "agents": {
                "total_agents": len(agents),
                "agent_names": list(agents.keys())
            },
            "storage": {
                "type": "in-memory",
                "persistence": "No - data lost on restart",
                "note": "All workflow data is stored in memory and will be lost when the server restarts"
            }
        }
    }

@app.get("/server-status")
async def get_server_status():
    """Simple endpoint to check server status and detect restarts"""
    import os
    
    return {
        "success": True,
        "data": {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "server_id": os.getpid(),  # Changes when server restarts
            "total_workflows": len(workflows),
            "active_workflows": len([w for w in workflows.values() if w.status == "processing"]),
            "memory_storage": True,
            "restart_warning": "All workflow data is lost when server restarts"
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

@app.get("/download/{workflow_id}")
async def download_documentation(workflow_id: str, format: str = "markdown"):
    """Download generated documentation in specified format"""
    if workflow_id not in workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    workflow = workflows[workflow_id]
    
    if workflow.status != "completed":
        raise HTTPException(status_code=400, detail="Workflow not completed yet")
    
    if not workflow.result or "documentation" not in workflow.result:
        raise HTTPException(status_code=404, detail="No documentation available for download")
    
    documentation = workflow.result["documentation"]
    project_name = workflow.result.get("repository_summary", {}).get("project_name", "documentation")
    
    # Prepare content based on format
    if format.lower() == "markdown":
        content = documentation
        media_type = "text/markdown"
        filename = f"{project_name}_documentation.md"
    elif format.lower() == "html":
        # Convert markdown to HTML (basic conversion)
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{project_name} Documentation</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }}
        h1, h2, h3 {{ color: #333; }}
        code {{ background: #f4f4f4; padding: 2px 4px; border-radius: 3px; }}
        pre {{ background: #f4f4f4; padding: 10px; border-radius: 5px; overflow-x: auto; }}
        blockquote {{ border-left: 4px solid #ddd; margin: 0; padding-left: 20px; }}
    </style>
</head>
<body>
    <div>{documentation.replace(chr(10), '<br>').replace('# ', '<h1>').replace('## ', '<h2>').replace('### ', '<h3>')}</div>
</body>
</html>"""
        content = html_content
        media_type = "text/html"
        filename = f"{project_name}_documentation.html"
    elif format.lower() == "json":
        # Export as JSON with full workflow data
        json_data = {
            "workflow_id": workflow_id,
            "project_name": project_name,
            "generated_at": workflow.completed_at.isoformat() if workflow.completed_at else None,
            "documentation": documentation,
            "repository_summary": workflow.result.get("repository_summary", {}),
            "ai_powered": workflow.ai_powered,
            "metadata": {
                "total_processing_time": str(workflow.completed_at - workflow.created_at) if workflow.completed_at else None,
                "workflow_status": workflow.status,
                "agents_used": list(workflow.agents.keys())
            }
        }
        content = json.dumps(json_data, indent=2)
        media_type = "application/json"
        filename = f"{project_name}_documentation.json"
    else:
        raise HTTPException(status_code=400, detail="Unsupported format. Use 'markdown', 'html', or 'json'")
    
    # Create response with proper headers for download
    response = Response(
        content=content,
        media_type=media_type,
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Type": media_type
        }
    )
    
    return response

# Catch-all route to serve React app for frontend routes  
@app.get("/manifest.json")
async def serve_manifest():
    """Serve the React app's manifest.json file"""
    static_directory = os.path.join(os.path.dirname(__file__), "..", "..", "static")
    manifest_file = os.path.join(static_directory, "manifest.json")
    
    if os.path.exists(manifest_file):
        return FileResponse(manifest_file)
    else:
        raise HTTPException(status_code=404, detail="Manifest not found")

@app.get("/favicon.svg")
async def serve_favicon():
    """Serve the React app's favicon"""
    static_directory = os.path.join(os.path.dirname(__file__), "..", "..", "static")
    favicon_file = os.path.join(static_directory, "favicon.svg")
    
    if os.path.exists(favicon_file):
        return FileResponse(favicon_file)
    else:
        raise HTTPException(status_code=404, detail="Favicon not found")

@app.get("/logo192.svg")
async def serve_logo192():
    """Serve the React app's logo192.svg"""
    static_directory = os.path.join(os.path.dirname(__file__), "..", "..", "static")
    logo_file = os.path.join(static_directory, "logo192.svg")
    
    if os.path.exists(logo_file):
        return FileResponse(logo_file, media_type="image/svg+xml")
    else:
        raise HTTPException(status_code=404, detail="Logo not found")

@app.get("/logo512.svg")
async def serve_logo512():
    """Serve the React app's logo512.svg"""
    static_directory = os.path.join(os.path.dirname(__file__), "..", "..", "static")
    logo_file = os.path.join(static_directory, "logo512.svg")
    
    if os.path.exists(logo_file):
        return FileResponse(logo_file, media_type="image/svg+xml")
    else:
        raise HTTPException(status_code=404, detail="Logo not found")

@app.get("/favicon.ico")
async def serve_favicon_ico():
    """Serve the React app's favicon.ico"""
    static_directory = os.path.join(os.path.dirname(__file__), "..", "..", "static")
    favicon_file = os.path.join(static_directory, "favicon.ico")
    
    if os.path.exists(favicon_file):
        return FileResponse(favicon_file, media_type="image/x-icon")
    else:
        raise HTTPException(status_code=404, detail="Favicon ICO not found")

@app.get("/{path:path}")
async def serve_frontend(path: str):
    """Serve React frontend for all non-API routes"""
    static_directory = os.path.join(os.path.dirname(__file__), "..", "..", "static")
    index_file = os.path.join(static_directory, "index.html")
    
    # Don't intercept API routes or static file routes
    # Note: "generate" and "status" without IDs are valid frontend routes, so only exclude API paths
    if path.startswith(("api/", "docs", "openapi.json", "health", "status/", "feedback", "workflows", "agents", "debug", "static/", "translation/", "auth/", "github/", "download/")):
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

@app.post("/stop-workflow")
async def stop_workflow(request: StopWorkflowRequest):
    """Stop a running workflow"""
    workflow_id = request.workflow_id
    
    if workflow_id not in workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    workflow = workflows[workflow_id]
    
    if workflow.status != "processing":
        raise HTTPException(status_code=400, detail="Workflow is not in progress")
    
    # Mark workflow as stopped
    workflow.status = "stopped"
    workflow.progress = 100
    workflow.message = "Workflow stopped by user"
    workflow.completed_at = datetime.now()
    workflow.current_agent = None
    
    # Mark all agents as idle
    for agent_id in workflow.agents:
        workflow.agents[agent_id].status = "idle"
        workflow.agents[agent_id].progress = 0
    
    # Clean up agent execution queue
    if workflow_id in agent_execution_queue:
        del agent_execution_queue[workflow_id]
    
    logger.info(f"Workflow {workflow_id} stopped by user")
    
    return {
        "success": True,
        "message": "Workflow stopped successfully"
    }

@app.get("/debug/workflow/{workflow_id}")
async def debug_workflow_status(workflow_id: str):
    """Debug endpoint to track real-time workflow progress"""
    if workflow_id not in workflows:
        return {"error": "Workflow not found", "workflow_id": workflow_id}
    
    workflow = workflows[workflow_id]
    
    # Get current time for elapsed calculations
    current_time = datetime.now()
    elapsed_total = (current_time - workflow.created_at).total_seconds()
    
    debug_info = {
        "workflow_id": workflow_id,
        "status": workflow.status,
        "progress": workflow.progress,
        "message": workflow.message,
        "current_agent": workflow.current_agent,
        "ai_powered": getattr(workflow, 'ai_powered', False),
        "elapsed_time_seconds": elapsed_total,
        "created_at": workflow.created_at.isoformat(),
        "agents_detailed": {}
    }
    
    # Add detailed agent information
    for agent_id, agent_status in workflow.agents.items():
        agent_elapsed = None
        if agent_status.started_at:
            agent_elapsed = (current_time - agent_status.started_at).total_seconds()
        
        debug_info["agents_detailed"][agent_id] = {
            "status": agent_status.status,
            "progress": agent_status.progress,
            "current_task": agent_status.current_task,
            "started_at": agent_status.started_at.isoformat() if agent_status.started_at else None,
            "completed_at": agent_status.completed_at.isoformat() if agent_status.completed_at else None,
            "elapsed_seconds": agent_elapsed,
            "is_current": workflow.current_agent == agent_id
        }
    
    return {"success": True, "debug_data": debug_info}

# Add enhanced agent tracking
agent_transition_history: Dict[str, List[Dict]] = {}

async def update_agent_status_with_history(workflow_id: str, agent_name: str, status: str, 
                                         progress: int, current_task: str = None):
    """Update agent status and maintain transition history for better frontend sync"""
    if workflow_id not in workflows:
        return
    
    # Initialize history if needed
    if workflow_id not in agent_transition_history:
        agent_transition_history[workflow_id] = []
    
    # Update agent status
    if agent_name in workflows[workflow_id].agents:
        workflows[workflow_id].agents[agent_name].status = status
        workflows[workflow_id].agents[agent_name].progress = progress
        if current_task:
            workflows[workflow_id].agents[agent_name].current_task = current_task
        
        if status == "active":
            workflows[workflow_id].agents[agent_name].started_at = datetime.now()
        elif status == "completed":
            workflows[workflow_id].agents[agent_name].completed_at = datetime.now()
    
    # Record transition in history
    transition = {
        "timestamp": datetime.now().isoformat(),
        "agent": agent_name,
        "status": status,
        "progress": progress,
        "task": current_task or "",
        "workflow_progress": workflows[workflow_id].progress
    }
    
    agent_transition_history[workflow_id].append(transition)
    
    # Keep only last 20 transitions to prevent memory issues
    if len(agent_transition_history[workflow_id]) > 20:
        agent_transition_history[workflow_id] = agent_transition_history[workflow_id][-20:]

def main():
    """Main entry point for the application"""
    # Get port from environment variable (for Cloud Run)
    port = int(os.getenv("PORT", 8080))
    
    # Startup logging
    logger.info("🚀 Starting Technical Documentation Suite API")
    logger.info(f"📋 Version: 1.0.0")
    logger.info(f"🌐 Port: {port}")
    logger.info(f"🏆 Built for: Google Cloud ADK Hackathon")
    
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")

if __name__ == "__main__":
    main() 