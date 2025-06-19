#!/bin/bash

# Quick Start Script for Technical Documentation Suite
# Robust startup with comprehensive error handling

set -e  # Exit on any error

echo "🚀 Technical Documentation Suite - Quick Start"
echo "=============================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
BACKEND_PORT=8080
FRONTEND_PORT=3000
MAX_STARTUP_TIME=60

# Cleanup function
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Cleaning up...${NC}"
    pkill -f "uvicorn main:app" 2>/dev/null || true
    pkill -f "npm start" 2>/dev/null || true
    lsof -ti:${BACKEND_PORT} | xargs kill -9 2>/dev/null || true
    lsof -ti:${FRONTEND_PORT} | xargs kill -9 2>/dev/null || true
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Check prerequisites
check_prerequisites() {
    echo -e "${BLUE}🔍 Checking prerequisites...${NC}"
    
    # Check conda
    if ! command -v conda &> /dev/null; then
        echo -e "${RED}❌ Conda not found. Please install Anaconda/Miniconda first.${NC}"
        exit 1
    fi
    
    # Check node/npm for frontend
    if [ -d "frontend" ]; then
        if ! command -v node &> /dev/null; then
            echo -e "${YELLOW}⚠️  Node.js not found. Frontend will be skipped.${NC}"
            SKIP_FRONTEND=true
        fi
    fi
    
    echo -e "${GREEN}✅ Prerequisites checked${NC}"
}

# Environment setup
setup_environment() {
    echo -e "${BLUE}🔧 Setting up environment...${NC}"
    
    # Source conda
    source $(conda info --base)/etc/profile.d/conda.sh || {
        echo -e "${RED}❌ Failed to source conda${NC}"
        exit 1
    }
    
    # Check if environment exists
    if ! conda env list | grep -q "tech_doc_suit"; then
        echo -e "${YELLOW}⚠️  Creating conda environment...${NC}"
        conda create -n tech_doc_suit python=3.12 -y
    fi
    
    # Activate environment
    conda activate tech_doc_suit || {
        echo -e "${RED}❌ Failed to activate conda environment${NC}"
        exit 1
    }
    
    # Clean conflicting venv directories
    rm -rf venv .venv 2>/dev/null || true
    
    echo -e "${GREEN}✅ Environment ready${NC}"
}

# Install dependencies
install_dependencies() {
    echo -e "${BLUE}📦 Installing/updating dependencies...${NC}"
    
    # Python packages
    pip install --quiet --upgrade pip || {
        echo -e "${YELLOW}⚠️  Pip upgrade failed, continuing...${NC}"
    }
    
    # Essential packages
    pip install --quiet \
        fastapi==0.104.1 \
        uvicorn[standard]==0.24.0 \
        pydantic==2.5.0 \
        python-multipart==0.0.6 \
        requests==2.31.0 \
        aiofiles \
        jinja2 || {
        echo -e "${RED}❌ Failed to install basic packages${NC}"
        exit 1
    }
    
    # AI packages (optional)
    pip install --quiet \
        google-generativeai==0.8.5 \
        google-cloud-storage \
        google-cloud-bigquery 2>/dev/null || {
        echo -e "${YELLOW}⚠️  Some AI packages failed to install, continuing...${NC}"
    }
    
    echo -e "${GREEN}✅ Dependencies installed${NC}"
}

# Start backend with error handling
start_backend() {
    echo -e "${BLUE}🔧 Starting backend server...${NC}"
    
    # Check for port conflicts
    if lsof -i:${BACKEND_PORT} >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Port ${BACKEND_PORT} is busy, cleaning up...${NC}"
        lsof -ti:${BACKEND_PORT} | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
    
    # Set environment variables
    export PYTHONPATH="${PWD}:${PYTHONPATH}"
    if [ -n "$GEMINI_API_KEY" ]; then
        export GEMINI_API_KEY="$GEMINI_API_KEY"
        echo -e "${GREEN}✅ AI features enabled${NC}"
    else
        export GEMINI_API_KEY="demo-mode"
        echo -e "${YELLOW}🎭 Running in demo mode${NC}"
    fi
    
    # Start server
    echo -e "${YELLOW}⏳ Starting uvicorn server...${NC}"
    uvicorn main:app --host 0.0.0.0 --port ${BACKEND_PORT} --reload --log-level info &
    BACKEND_PID=$!
    
    echo -e "${GREEN}✅ Backend server started (PID: $BACKEND_PID)${NC}"
    
    # Wait for server to start
    echo -e "${YELLOW}⏳ Waiting for backend to become ready...${NC}"
    local attempts=0
    local max_attempts=30
    
    while [ $attempts -lt $max_attempts ]; do
        if curl -s -f http://localhost:${BACKEND_PORT}/health >/dev/null 2>&1; then
            echo -e "${GREEN}✅ Backend is ready! (attempt $((attempts+1)))${NC}"
            return 0
        fi
        
        attempts=$((attempts+1))
        echo -e "${YELLOW}⏳ Waiting... ($attempts/$max_attempts)${NC}"
        sleep 2
    done
    
    echo -e "${YELLOW}⚠️  Backend health check timeout, but server may still be starting${NC}"
    echo -e "${YELLOW}   Check http://localhost:${BACKEND_PORT}/health manually${NC}"
}

# Start frontend
start_frontend() {
    if [ "$SKIP_FRONTEND" = true ] || [ ! -d "frontend" ]; then
        echo -e "${YELLOW}⏳ Skipping frontend...${NC}"
        return 0
    fi
    
    echo -e "${BLUE}🎨 Starting frontend server...${NC}"
    
    cd frontend
    
    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        echo -e "${BLUE}📦 Installing npm packages...${NC}"
        npm install --silent
    fi
    
    # Start frontend
    npm start >/dev/null 2>&1 &
    FRONTEND_PID=$!
    cd ..
    
    echo -e "${GREEN}✅ Frontend server started (PID: $FRONTEND_PID)${NC}"
}

# Show status and URLs
show_status() {
    echo ""
    echo -e "${GREEN}🎉 Technical Documentation Suite is running!${NC}"
    echo "=============================================="
    echo -e "${BLUE}🔗 URLs:${NC}"
    echo -e "   • Backend API: ${YELLOW}http://localhost:${BACKEND_PORT}${NC}"
    echo -e "   • API Documentation: ${YELLOW}http://localhost:${BACKEND_PORT}/docs${NC}"
    echo -e "   • Health Check: ${YELLOW}http://localhost:${BACKEND_PORT}/health${NC}"
    echo -e "   • AI Status: ${YELLOW}http://localhost:${BACKEND_PORT}/debug/ai-status${NC}"
    
    if [ "$SKIP_FRONTEND" != true ] && [ -d "frontend" ]; then
        echo -e "   • Frontend: ${YELLOW}http://localhost:${FRONTEND_PORT}${NC}"
    fi
    
    echo ""
    if [ -n "$GEMINI_API_KEY" ] && [ "$GEMINI_API_KEY" != "demo-mode" ]; then
        echo -e "${GREEN}🤖 AI Features: ENABLED${NC}"
        echo -e "${GREEN}   • Real repository analysis${NC}"
        echo -e "${GREEN}   • AI-generated documentation${NC}"
    else
        echo -e "${YELLOW}🎭 AI Features: DEMO MODE${NC}"
        echo -e "${YELLOW}   • Sample documentation${NC}"
        echo -e "${YELLOW}   • Simulated workflows${NC}"
        echo ""
        echo -e "${BLUE}💡 To enable AI features:${NC}"
        echo -e "${BLUE}   export GEMINI_API_KEY='your-api-key'${NC}"
        echo -e "${BLUE}   Get free key at: https://makersuite.google.com/app/apikey${NC}"
    fi
    
    echo ""
    echo -e "${YELLOW}📱 Test the application:${NC}"
    echo -e "${YELLOW}   1. Open the frontend URL above${NC}"
    echo -e "${YELLOW}   2. Click 'Generate Documentation'${NC}"
    echo -e "${YELLOW}   3. Enter a GitHub repository URL${NC}"
    echo -e "${YELLOW}   4. Watch the multi-agent workflow!${NC}"
    echo ""
    echo -e "${RED}Press Ctrl+C to stop all servers${NC}"
}

# Main execution
main() {
    check_prerequisites
    setup_environment
    install_dependencies
    start_backend
    start_frontend
    show_status
    
    # Keep script running
    echo -e "${YELLOW}⏳ Servers running... Press Ctrl+C to stop${NC}"
    while true; do
        sleep 5
        
        # Check if backend is still running
        if ! kill -0 $BACKEND_PID 2>/dev/null; then
            echo -e "${RED}❌ Backend server died, restarting...${NC}"
            start_backend
        fi
    done
}

# Run main function
main "$@" 