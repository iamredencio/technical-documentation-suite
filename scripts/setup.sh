#!/bin/bash

# Technical Documentation Suite Setup Script

set -e

echo "🚀 Setting up Technical Documentation Suite..."

# Check if required tools are installed
command -v gcloud >/dev/null 2>&1 || { echo "❌ Google Cloud SDK is required but not installed."; exit 1; }
command -v terraform >/dev/null 2>&1 || { echo "❌ Terraform is required but not installed."; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "❌ Docker is required but not installed."; exit 1; }

# Get project ID
if [ -z "$GOOGLE_CLOUD_PROJECT" ]; then
    echo "📝 Please enter your Google Cloud Project ID:"
    read -r PROJECT_ID
    export GOOGLE_CLOUD_PROJECT=$PROJECT_ID
else
    PROJECT_ID=$GOOGLE_CLOUD_PROJECT
fi

echo "📋 Using project: $PROJECT_ID"

# Set default region
REGION=${GOOGLE_CLOUD_REGION:-"us-central1"}
echo "🌍 Using region: $REGION"

# Authenticate with Google Cloud
echo "🔐 Authenticating with Google Cloud..."
gcloud auth login
gcloud config set project $PROJECT_ID

# Initialize Terraform
echo "🏗️  Initializing Terraform..."
cd terraform
terraform init

# Plan Terraform deployment
echo "📋 Planning Terraform deployment..."
terraform plan -var="project_id=$PROJECT_ID" -var="region=$REGION"

echo "❓ Do you want to apply the Terraform configuration? (y/N)"
read -r APPLY_TERRAFORM

if [ "$APPLY_TERRAFORM" = "y" ] || [ "$APPLY_TERRAFORM" = "Y" ]; then
    echo "🚀 Applying Terraform configuration..."
    terraform apply -var="project_id=$PROJECT_ID" -var="region=$REGION" -auto-approve
    echo "✅ Infrastructure created successfully!"
else
    echo "⏸️  Skipping Terraform apply. Run manually when ready:"
    echo "   cd terraform && terraform apply -var=\"project_id=$PROJECT_ID\" -var=\"region=$REGION\""
fi

cd ..

# Build and deploy the application
echo "🐳 Building Docker image..."
docker build -t $REGION-docker.pkg.dev/$PROJECT_ID/technical-doc-suite/app:latest .

echo "📤 Pushing to Artifact Registry..."
gcloud auth configure-docker $REGION-docker.pkg.dev
docker push $REGION-docker.pkg.dev/$PROJECT_ID/technical-doc-suite/app:latest

echo "☁️  Deploying to Cloud Run..."
gcloud run deploy technical-documentation-suite \
    --image $REGION-docker.pkg.dev/$PROJECT_ID/technical-doc-suite/app:latest \
    --region $REGION \
    --platform managed \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --max-instances 10 \
    --set-env-vars GOOGLE_CLOUD_PROJECT=$PROJECT_ID \
    --set-env-vars STORAGE_BUCKET=$PROJECT_ID-doc-suite-artifacts \
    --set-env-vars BIGQUERY_DATASET=documentation_analytics

echo "🎉 Technical Documentation Suite deployed successfully!"
echo "🌐 Service URL: $(gcloud run services describe technical-documentation-suite --region=$REGION --format='value(status.url)')"

echo ""
echo "📚 Next steps:"
echo "1. Test the API endpoints"
echo "2. Submit your project to the ADK hackathon"
echo "3. Monitor usage via BigQuery analytics" 