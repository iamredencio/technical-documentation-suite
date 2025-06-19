#!/bin/bash

# Test AI Mode - Diagnostic Script
echo "🔍 Diagnosing AI Mode Issues..."
echo "================================="

# Check if API key is set
echo "1. Environment Variable Check:"
if [ -z "$GEMINI_API_KEY" ]; then
    echo "   ❌ GEMINI_API_KEY is NOT set"
    echo "   💡 Set it with: export GEMINI_API_KEY='your-key'"
else
    echo "   ✅ GEMINI_API_KEY is SET (length: ${#GEMINI_API_KEY})"
fi

echo ""

# Check if servers are running
echo "2. Server Status Check:"
if curl -s http://localhost:8080/health > /dev/null; then
    echo "   ✅ Backend server is running"
else
    echo "   ❌ Backend server is NOT running"
    echo "   💡 Start with: ./start_with_ai.sh"
fi

if curl -s http://localhost:3000 > /dev/null; then
    echo "   ✅ Frontend server is running"
else
    echo "   ❌ Frontend server is NOT running"
fi

echo ""

# Test AI service
echo "3. AI Service Check:"
ai_status=$(curl -s http://localhost:8080/debug/ai-status 2>/dev/null)
if [ $? -eq 0 ]; then
    echo "   ✅ AI status endpoint accessible"
    echo "   📊 AI Status:"
    echo "$ai_status" | python3 -m json.tool 2>/dev/null || echo "$ai_status"
else
    echo "   ❌ Cannot access AI status endpoint"
fi

echo ""

# Test a quick generation
echo "4. Quick Generation Test:"
echo "   📝 Testing documentation generation..."

test_payload='{
    "repository_url": "https://github.com/fastapi/fastapi",
    "project_id": "test-ai-mode",
    "output_formats": ["markdown"],
    "include_diagrams": true,
    "target_audience": "developers"
}'

response=$(curl -s -X POST http://localhost:8080/generate \
    -H "Content-Type: application/json" \
    -d "$test_payload" 2>/dev/null)

if [ $? -eq 0 ]; then
    echo "   ✅ Generation request sent successfully"
    workflow_id=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['workflow_id'])" 2>/dev/null)
    
    if [ ! -z "$workflow_id" ]; then
        echo "   📋 Workflow ID: $workflow_id"
        echo "   🔗 Check status at: http://localhost:3000/status/$workflow_id"
        
        # Wait and check status
        echo "   ⏳ Waiting 3 seconds for status update..."
        sleep 3
        
        status=$(curl -s http://localhost:8080/status/$workflow_id 2>/dev/null)
        if [ $? -eq 0 ]; then
            echo "   📊 Current Status:"
            echo "$status" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)['data']
    print(f\"      Status: {data['status']}\")
    print(f\"      Progress: {data['progress']}%\")
    print(f\"      Message: {data['message']}\")
    print(f\"      Current Agent: {data.get('current_agent', 'None')}\")
except:
    print('      Error parsing status')
" 2>/dev/null
        fi
    fi
else
    echo "   ❌ Generation request failed"
fi

echo ""
echo "🎯 Summary:"
echo "   • If GEMINI_API_KEY is set and servers are running, AI mode should work"
echo "   • Check the workflow status URL above for real-time progress"
echo "   • Look for 'AI-powered' in the status messages"
echo "   • Agent cards should show which agent is currently active" 