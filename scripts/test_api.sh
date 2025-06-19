#!/bin/bash

echo "🧪 Testing Technical Documentation Suite API"
echo "============================================="

# Test health endpoint
echo "1. Testing health endpoint..."
curl -s http://localhost:8080/health | jq '.'

echo ""
echo "2. Testing AI status endpoint..."
curl -s http://localhost:8080/debug/ai-status | jq '.'

echo ""
echo "3. Starting a test workflow..."
WORKFLOW_RESPONSE=$(curl -s -X POST http://localhost:8080/generate \
  -H "Content-Type: application/json" \
  -d '{
    "repository_url": "https://github.com/octocat/Hello-World",
    "project_id": "test-project",
    "output_formats": ["markdown"],
    "include_diagrams": true,
    "target_audience": "developers"
  }')

echo "Workflow Response:"
echo $WORKFLOW_RESPONSE | jq '.'

# Extract workflow ID
WORKFLOW_ID=$(echo $WORKFLOW_RESPONSE | jq -r '.data.workflow_id')

if [ "$WORKFLOW_ID" != "null" ] && [ -n "$WORKFLOW_ID" ]; then
  echo ""
  echo "4. Monitoring workflow progress (ID: $WORKFLOW_ID)..."
  
  for i in {1..30}; do
    echo "Check $i/30..."
    STATUS_RESPONSE=$(curl -s http://localhost:8080/status/$WORKFLOW_ID)
    STATUS=$(echo $STATUS_RESPONSE | jq -r '.data.status')
    PROGRESS=$(echo $STATUS_RESPONSE | jq -r '.data.progress')
    MESSAGE=$(echo $STATUS_RESPONSE | jq -r '.data.message')
    CURRENT_AGENT=$(echo $STATUS_RESPONSE | jq -r '.data.current_agent')
    
    echo "  Status: $STATUS | Progress: $PROGRESS% | Agent: $CURRENT_AGENT"
    echo "  Message: $MESSAGE"
    
    if [ "$STATUS" = "completed" ] || [ "$STATUS" = "failed" ]; then
      echo ""
      echo "5. Final workflow status:"
      echo $STATUS_RESPONSE | jq '.'
      
      if [ "$STATUS" = "completed" ]; then
        HAS_RESULT=$(echo $STATUS_RESPONSE | jq -r '.data.result != null')
        if [ "$HAS_RESULT" = "true" ]; then
          echo ""
          echo "✅ Workflow completed with results!"
          echo "   - AI Generated: $(echo $STATUS_RESPONSE | jq -r '.data.result.ai_generated')"
          echo "   - Documentation Length: $(echo $STATUS_RESPONSE | jq -r '.data.result.documentation | length') characters"
          echo "   - Quality Score: $(echo $STATUS_RESPONSE | jq -r '.data.result.quality.overall_score')"
        else
          echo "⚠️  Workflow completed but no results found"
        fi
      fi
      break
    fi
    
    sleep 5
  done
else
  echo "❌ Failed to start workflow"
fi

echo ""
echo "🏁 Test complete!" 