#!/bin/bash

# Simplified deployment script for Technical Documentation Suite
set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Deploying Technical Documentation Suite to Google Cloud Run${NC}"

# Get project ID
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
if [ -z "$PROJECT_ID" ]; then
    echo "❌ No project set. Please run: gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

echo -e "${GREEN}✅ Project ID: $PROJECT_ID${NC}"

# Submit build to Cloud Build
echo -e "${BLUE}📦 Building and deploying with Cloud Build...${NC}"
gcloud builds submit --config cloudbuild.yaml

# Get service URL
echo -e "${BLUE}🔗 Getting service URL...${NC}"
SERVICE_URL=$(gcloud run services describe technical-documentation-suite \
    --region=us-central1 --format="value(status.url)" 2>/dev/null || echo "")

if [ -n "$SERVICE_URL" ]; then
    echo ""
    echo -e "${GREEN}🎉 Deployment successful!${NC}"
    echo -e "${GREEN}🌐 Service URL: $SERVICE_URL${NC}"
    echo ""
    echo "📋 Next steps:"
    echo "1. Visit your application: $SERVICE_URL"
    echo "2. Test the documentation generation feature"
    echo "3. Monitor logs: https://console.cloud.google.com/run/detail/us-central1/technical-documentation-suite/logs"
else
    echo "❌ Failed to get service URL. Check the Cloud Console for deployment status."
fi 