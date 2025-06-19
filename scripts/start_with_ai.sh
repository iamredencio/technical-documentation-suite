#!/bin/bash

# Technical Documentation Suite - AI Enabled Startup
# Google Cloud ADK Hackathon 2024

echo "🚀 Starting Technical Documentation Suite with AI..."
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check for GEMINI_API_KEY
check_api_key() {
    if [ -z "$GEMINI_API_KEY" ]; then
        echo -e "${YELLOW}⚠️  GEMINI_API_KEY not set${NC}"
        echo -e "${YELLOW}💡 To enable AI features:${NC}"
        echo -e "${YELLOW}   1. Get free API key from: https://makersuite.google.com/app/apikey${NC}"
        echo -e "${YELLOW}   2. Export it: export GEMINI_API_KEY='your-key-here'${NC}"
        echo -e "${YELLOW}   3. Run this script again${NC}"
        echo ""
        read -p "Continue in demo mode? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
        echo -e "${BLUE}🎭 Running in demo mode${NC}"
    else
        echo -e "${GREEN}✅ GEMINI_API_KEY detected - AI features enabled${NC}"
    fi
}

# Kill existing processes
cleanup_processes() {
    echo -e "${BLUE}🧹 Cleaning up existing processes...${NC}"
    pkill -f "uvicorn main:app" 2>/dev/null || true
    pkill -f "npm start" 2>/dev/null || true
    lsof -ti:3000 | xargs kill -9 2>/dev/null || true
    lsof -ti:8080 | xargs kill -9 2>/dev/null || true
    
    # Remove venv directories
    if [ -d "venv" ]; then
        rm -rf venv
        echo -e "${GREEN}✅ Removed venv directory${NC}"
    fi
    
    if [ -d ".venv" ]; then
        rm -rf .venv
        echo -e "${GREEN}✅ Removed .venv directory${NC}"
    fi
}

# Setup conda environment
setup_conda() {
    echo -e "${BLUE}🔧 Setting up conda environment...${NC}"
    
    # Source conda
    source $(conda info --base)/etc/profile.d/conda.sh
    
    # Activate environment
    conda activate tech_doc_suit
    
    # Install/update packages
    echo -e "${BLUE}📦 Installing Python packages...${NC}"
    pip install --upgrade pip
    pip install fastapi==0.104.1 uvicorn[standard]==0.24.0 pydantic==2.5.0
    pip install google-generativeai==0.8.5 requests==2.31.0 python-multipart==0.0.6
    pip install google-cloud-storage google-cloud-bigquery aiofiles jinja2
    
    echo -e "${GREEN}✅ Conda environment ready${NC}"
}

# Start backend
start_backend() {
    echo -e "${BLUE}🔧 Starting backend server...${NC}"
    
    # Activate conda and start server in background
    source $(conda info --base)/etc/profile.d/conda.sh
    conda activate tech_doc_suit
    
    # Export environment variable for this session
    if [ ! -z "$GEMINI_API_KEY" ]; then
        export GEMINI_API_KEY="$GEMINI_API_KEY"
    fi
    
    # Start server
    uvicorn main:app --host 0.0.0.0 --port 8080 --reload &
    BACKEND_PID=$!
    
    echo -e "${GREEN}✅ Backend server started (PID: $BACKEND_PID)${NC}"
    
    # Wait and test with multiple attempts
    echo -e "${YELLOW}⏳ Waiting for backend to start...${NC}"
    sleep 3
    
    # Try health check multiple times with longer delay
    for i in {1..15}; do
        if curl -s http://localhost:8080/health > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Backend health check passed on attempt $i${NC}"
            return 0
        else
            echo -e "${YELLOW}⏳ Health check attempt $i/15...${NC}"
            sleep 2
        fi
    done
    
    # Final attempt - warn but don't exit
    if curl -s http://localhost:8080/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend server is ready${NC}"
    else
        echo -e "${YELLOW}⚠️  Backend health check failed but continuing...${NC}"
        echo -e "${YELLOW}   Server may still be starting - check http://localhost:8080/health manually${NC}"
    fi
}

# Start frontend
start_frontend() {
    echo -e "${BLUE}🎨 Starting frontend server...${NC}"
    
    cd frontend
    
    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        echo -e "${BLUE}📦 Installing npm packages...${NC}"
        npm install
    fi
    
    # Start frontend
    npm start &
    FRONTEND_PID=$!
    cd ..
    
    echo -e "${GREEN}✅ Frontend server started (PID: $FRONTEND_PID)${NC}"
}

# Show final info
show_success() {
    echo ""
    echo -e "${GREEN}🎉 Technical Documentation Suite is running!${NC}"
    echo "=============================================="
    echo -e "${BLUE}Frontend:${NC} http://localhost:3000"
    echo -e "${BLUE}Backend API:${NC} http://localhost:8080"
    echo -e "${BLUE}API Docs:${NC} http://localhost:8080/docs"
    echo -e "${BLUE}Health Check:${NC} http://localhost:8080/health"
    echo ""
    
    if [ ! -z "$GEMINI_API_KEY" ]; then
        echo -e "${GREEN}🤖 AI Features: ENABLED${NC}"
        echo -e "${GREEN}   • Real repository analysis${NC}"
        echo -e "${GREEN}   • AI-generated documentation${NC}"
        echo -e "${GREEN}   • Quality assessment${NC}"
    else
        echo -e "${YELLOW}🎭 AI Features: DEMO MODE${NC}"
        echo -e "${YELLOW}   • Sample documentation${NC}"
        echo -e "${YELLOW}   • Simulated workflows${NC}"
    fi
    
    echo ""
    echo -e "${YELLOW}📱 Test it now:${NC}"
    echo -e "${YELLOW}   1. Open http://localhost:3000${NC}"
    echo -e "${YELLOW}   2. Click 'Generate Documentation'${NC}"
    echo -e "${YELLOW}   3. Enter a GitHub URL${NC}"
    echo -e "${YELLOW}   4. Watch the progress animation!${NC}"
    echo ""
    echo -e "${RED}Press Ctrl+C to stop both servers${NC}"
}

# Cleanup on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Shutting down servers...${NC}"
    
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
    fi
    
    lsof -ti:3000 | xargs kill -9 2>/dev/null || true
    lsof -ti:8080 | xargs kill -9 2>/dev/null || true
    
    echo -e "${GREEN}✅ Servers stopped${NC}"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Main execution
main() {
    check_api_key
    cleanup_processes
    setup_conda
    start_backend
    start_frontend
    show_success
    
    # Keep script running
    while true; do
        sleep 1
    done
}

# Run main function
main 