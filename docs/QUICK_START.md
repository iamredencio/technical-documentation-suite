# 🚀 Quick Start Guide

Get the Technical Documentation Suite running in minutes!

## 📋 Prerequisites

- Python 3.10+ 
- Node.js 16+
- Git

## ⚡ Fast Setup

1. **Clone & Setup**
   ```bash
   git clone <your-repo-url>
   cd tech-doc-suite
   make setup
   ```

2. **Start Development Servers**
   ```bash
   # Terminal 1: Backend
   make dev
   
   # Terminal 2: Frontend  
   make frontend
   ```

3. **Open Your Browser**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8080
   - API Docs: http://localhost:8080/docs

## 🎯 Alternative Ways to Run

### Option 1: Simple Python Script (Recommended)
```bash
python run.py
```

### Option 2: Using Uvicorn Directly
```bash
cd src
python -m uvicorn tech_doc_suite.main:app --reload --host 0.0.0.0 --port 8080
```

### Option 3: Using Make Commands
```bash
make dev           # Uses run.py
make dev-uvicorn   # Uses uvicorn directly
```

## 🔧 Configuration

1. **Copy Environment Template**
   ```bash
   cp env.example .env
   ```

2. **Add Your API Keys** (optional for demo mode)
   ```bash
   # Edit .env file
   GEMINI_API_KEY=your_google_gemini_api_key_here
   GOOGLE_CLOUD_PROJECT=your_gcp_project_id
   ```

## 🧪 Test It Works

```bash
# Test backend
curl http://localhost:8080/health

# Run tests  
make test

# Check code quality
make lint
```

## 📱 Usage

1. Open http://localhost:3000
2. Enter a GitHub repository URL
3. Click "Generate Documentation"  
4. Watch the AI agents work!

## 🆘 Troubleshooting

**Import Errors?**
- Make sure you're running from the project root
- Use `python run.py` instead of running main.py directly

**Port Already in Use?**
- Change port in env file: `PORT=8081`
- Or kill existing processes: `pkill -f uvicorn`

**Frontend Won't Load?**  
- Make sure both backend and frontend are running
- Check that backend is serving on port 8080

---

Need help? Check the [CONTRIBUTING.md](CONTRIBUTING.md) for detailed setup instructions! 