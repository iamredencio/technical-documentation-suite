#!/bin/bash

# Simple deployment script for Technical Documentation Suite
set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🚀 Deploying Technical Documentation Suite to Google Cloud${NC}"
echo "================================================================"

# Get project ID
PROJECT_ID=$(gcloud config get-value project)
echo -e "${GREEN}Using project: $PROJECT_ID${NC}"

# Check if Gemini API key secret exists
if ! gcloud secrets describe gemini-api-key &> /dev/null; then
    echo -e "${BLUE}Setting up Gemini API key...${NC}"
    echo "Please enter your Gemini API key (get one from https://aistudio.google.com/app/apikey):"
    read -s GEMINI_API_KEY
    echo -n "$GEMINI_API_KEY" | gcloud secrets create gemini-api-key --data-file=-
    echo -e "${GREEN}✅ Gemini API key stored in Secret Manager${NC}"
else
    echo -e "${GREEN}✅ Gemini API key already exists${NC}"
fi

# Build and deploy
echo -e "${BLUE}Building and deploying application...${NC}"
gcloud builds submit --config cloudbuild.yaml

# Get service URL
SERVICE_URL=$(gcloud run services describe technical-documentation-suite \
    --region=us-central1 --format="value(status.url)" 2>/dev/null || echo "")

if [ -n "$SERVICE_URL" ]; then
    echo -e "${GREEN}🎉 Deployment successful!${NC}"
    echo -e "${GREEN}Service URL: $SERVICE_URL${NC}"
    echo -e "${GREEN}Health Check: $SERVICE_URL/health${NC}"
    echo -e "${GREEN}API Docs: $SERVICE_URL/docs${NC}"
else
    echo -e "${RED}❌ Deployment failed or service URL not found${NC}"
    exit 1
fi 