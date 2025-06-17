# 🚀 Quick Start Guide

## The Issues You Were Facing:

1. **❌ Sample Documentation Only**: System running in demo mode
2. **❌ No Progress Animation**: Backend server not running
3. **❌ Environment Conflicts**: Mixed venv/conda environments

## ✅ Complete Solution:

### Step 1: Make Script Executable
```bash
chmod +x start_with_ai.sh
```

### Step 2: Choose Your Mode

**Option A: Demo Mode (Works Immediately)**
```bash
./start_with_ai.sh
# Press 'y' when asked about demo mode
```

**Option B: Full AI Mode (Recommended)**
```bash
# Get free API key from: https://makersuite.google.com/app/apikey
export GEMINI_API_KEY="your-api-key-here"
./start_with_ai.sh
```

### Step 3: Test Everything
1. Open http://localhost:3000
2. Click "Generate Documentation"
3. Enter any GitHub URL (e.g., `https://github.com/fastapi/fastapi`)
4. Enter a project ID (e.g., `test-project`)
5. Click "Generate"
6. **Watch the progress animation work!**

## What the Script Does:

✅ **Cleans up environment conflicts**
- Removes venv/`.venv` directories
- Kills existing processes

✅ **Sets up conda environment properly**
- Activates `tech_doc_suit` environment
- Installs all required packages

✅ **Starts both servers**
- Backend: http://localhost:8080
- Frontend: http://localhost:3000

✅ **Enables proper API communication**
- Backend responds to frontend requests
- Progress animation works
- Status updates in real-time

## Expected Behavior:

### With GEMINI_API_KEY:
- ✅ Real repository cloning
- ✅ AI-generated documentation
- ✅ Progress animation
- ✅ Quality assessment

### Without GEMINI_API_KEY (Demo Mode):
- ✅ Simulated workflow
- ✅ Progress animation
- ✅ Sample documentation
- ✅ All UI features work

## Troubleshooting:

**If progress animation still doesn't work:**
1. Check browser console for errors
2. Verify both servers are running:
   - http://localhost:8080/health
   - http://localhost:3000

**If AI features don't work:**
1. Verify API key is set: `echo $GEMINI_API_KEY`
2. Check server logs for errors

## Success Indicators:

✅ **Backend Started**: "Backend health check passed"
✅ **Frontend Started**: "Frontend server started"
✅ **Progress Works**: Agent cards animate during generation
✅ **AI Enabled**: "AI Features: ENABLED" shown in startup

---

**The script fixes ALL the issues you experienced!** 🎉 