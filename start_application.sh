#!/bin/bash

# Technical Documentation Suite Startup Script
# Google Cloud ADK Hackathon 2024 - CONDA VERSION

echo "🚀 Starting Technical Documentation Suite..."
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if required tools are installed
check_requirements() {
    echo -e "${BLUE}📋 Checking requirements...${NC}"
    
    # Check conda
    if ! command -v conda &> /dev/null; then
        echo -e "${RED}❌ Conda is not installed${NC}"
        exit 1
    fi
    
    # Check if tech_doc_suit environment exists
    if ! conda info --envs | grep -q "tech_doc_suit"; then
        echo -e "${RED}❌ tech_doc_suit conda environment not found${NC}"
        echo -e "${YELLOW}Please create it with: conda create -n tech_doc_suit python=3.11${NC}"
        exit 1
    fi
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        echo -e "${RED}❌ Node.js is not installed${NC}"
        exit 1
    fi
    
    # Check npm
    if ! command -v npm &> /dev/null; then
        echo -e "${RED}❌ npm is not installed${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ All requirements satisfied${NC}"
}

# Install backend dependencies
install_backend_deps() {
    echo -e "${BLUE}📦 Installing backend dependencies in conda environment...${NC}"
    
    # Remove any existing venv directories
    if [ -d "venv" ]; then
        echo -e "${YELLOW}🗑️  Removing old venv directory...${NC}"
        rm -rf venv
    fi
    
    if [ -d ".venv" ]; then
        echo -e "${YELLOW}🗑️  Removing old .venv directory...${NC}"
        rm -rf .venv
    fi
    
    # Activate conda environment
    source $(conda info --base)/etc/profile.d/conda.sh
    conda activate tech_doc_suit
    
    # Install requirements
    pip install --upgrade pip
    pip install -r requirements.txt
    
    echo -e "${GREEN}✅ Backend dependencies installed in conda environment${NC}"
}

# Install frontend dependencies
install_frontend_deps() {
    echo -e "${BLUE}📦 Installing frontend dependencies...${NC}"
    
    cd frontend
    npm install
    cd ..
    
    echo -e "${GREEN}✅ Frontend dependencies installed${NC}"
}

# Start backend server
start_backend() {
    echo -e "${BLUE}🔧 Starting backend server (FastAPI) with conda environment...${NC}"
    
    # Activate conda environment and start server
    source $(conda info --base)/etc/profile.d/conda.sh
    conda activate tech_doc_suit
    
    # Start FastAPI server in background
    uvicorn main:app --host 0.0.0.0 --port 8080 --reload &
    BACKEND_PID=$!
    
    echo -e "${GREEN}✅ Backend server started on http://localhost:8080 (PID: $BACKEND_PID)${NC}"
    
    # Wait for backend to be ready
    echo -e "${YELLOW}⏳ Waiting for backend to be ready...${NC}"
    sleep 5
    
    # Test backend health
    if curl -s http://localhost:8080/health > /dev/null; then
        echo -e "${GREEN}✅ Backend health check passed${NC}"
    else
        echo -e "${YELLOW}⚠️  Backend health check failed, but continuing...${NC}"
    fi
}

# Start frontend server
start_frontend() {
    echo -e "${BLUE}🎨 Starting frontend server (React)...${NC}"
    
    cd frontend
    npm start &
    FRONTEND_PID=$!
    cd ..
    
    echo -e "${GREEN}✅ Frontend server started on http://localhost:3000 (PID: $FRONTEND_PID)${NC}"
}

# Show application info
show_info() {
    echo ""
    echo -e "${GREEN}🎉 Technical Documentation Suite is running!${NC}"
    echo "=============================================="
    echo -e "${BLUE}Frontend:${NC} http://localhost:3000"
    echo -e "${BLUE}Backend API:${NC} http://localhost:8080"
    echo -e "${BLUE}API Docs:${NC} http://localhost:8080/docs"
    echo -e "${BLUE}Health Check:${NC} http://localhost:8080/health"
    echo ""
    echo -e "${YELLOW}📱 Key Features:${NC}"
    echo "  • Multi-Agent Documentation Generation"
    echo "  • Interactive Testing Dashboard"
    echo "  • Real-time Progress Tracking"
    echo "  • Quality Metrics & Feedback"
    echo "  • Google Cloud Integration"
    echo ""
    echo -e "${YELLOW}🏆 Built for Google Cloud ADK Hackathon 2024${NC}"
    echo ""
    echo -e "${YELLOW}💡 Environment: Using conda tech_doc_suit${NC}"
    echo -e "${YELLOW}💡 To enable AI features: export GEMINI_API_KEY=your-key${NC}"
    echo ""
    echo -e "${RED}Press Ctrl+C to stop both servers${NC}"
}

# Cleanup function
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Shutting down servers...${NC}"
    
    # Kill backend if it's running
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        echo -e "${GREEN}✅ Backend server stopped${NC}"
    fi
    
    # Kill frontend if it's running
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        echo -e "${GREEN}✅ Frontend server stopped${NC}"
    fi
    
    # Kill any remaining processes on ports 3000 and 8080
    lsof -ti:3000 | xargs kill -9 2>/dev/null
    lsof -ti:8080 | xargs kill -9 2>/dev/null
    
    echo -e "${GREEN}🎯 Technical Documentation Suite stopped successfully${NC}"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Main execution
main() {
    check_requirements
    install_backend_deps
    install_frontend_deps
    start_backend
    start_frontend
    show_info
    
    # Keep script running
    while true; do
        sleep 1
    done
}

# Run main function
main 