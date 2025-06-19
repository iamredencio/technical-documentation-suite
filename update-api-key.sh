#!/bin/bash

# Script to update the Gemini API key in Google Cloud Secret Manager
# Usage: ./update-api-key.sh YOUR_ACTUAL_API_KEY

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

if [ $# -eq 0 ]; then
    echo -e "${RED}❌ Error: Please provide your Gemini API key as an argument${NC}"
    echo ""
    echo "Usage: $0 YOUR_GEMINI_API_KEY"
    echo ""
    echo "To get a Gemini API key:"
    echo "1. Go to https://aistudio.google.com/app/apikey"
    echo "2. Sign in with your Google account"
    echo "3. Click 'Create API Key'"
    echo "4. Copy the generated key and run this script"
    echo ""
    exit 1
fi

API_KEY="$1"

echo -e "${BLUE}🔑 Updating Gemini API key in Google Cloud Secret Manager...${NC}"

# Update the secret
echo -n "$API_KEY" | gcloud secrets versions add gemini-api-key --data-file=-

echo -e "${GREEN}✅ API key updated successfully!${NC}"

echo -e "${BLUE}🚀 Redeploying the service to use the new API key...${NC}"

# Redeploy the Cloud Run service to pick up the new secret
gcloud run deploy technical-documentation-suite \
    --image gcr.io/technical-documentation-suite/technical-doc-suite:latest \
    --region us-central1 \
    --platform managed \
    --quiet

echo -e "${GREEN}🎉 Deployment complete! Your service should now use AI-powered documentation generation.${NC}"

echo -e "${BLUE}🔗 Service URL: https://technical-documentation-suite-vav24hhx6q-uc.a.run.app/${NC}"

echo ""
echo "Test the AI functionality by generating documentation for a repository!" 