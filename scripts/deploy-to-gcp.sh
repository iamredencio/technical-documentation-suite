#!/bin/bash

# Technical Documentation Suite - Google Cloud Deployment Script
# This script sets up continuous deployment from GitHub to Google Cloud Run

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required tools are installed
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    if ! command -v gcloud &> /dev/null; then
        print_error "Google Cloud SDK is not installed. Please install it from: https://cloud.google.com/sdk/docs/install"
        exit 1
    fi
    
    if ! command -v git &> /dev/null; then
        print_error "Git is not installed. Please install Git."
        exit 1
    fi
    
    print_success "Prerequisites check passed!"
}

# Get project configuration
get_project_config() {
    print_status "Getting project configuration..."
    
    # Get current project ID
    if [ -z "$PROJECT_ID" ]; then
        PROJECT_ID=$(gcloud config get-value project 2>/dev/null || echo "")
        if [ -z "$PROJECT_ID" ]; then
            read -p "Enter your Google Cloud Project ID: " PROJECT_ID
            gcloud config set project $PROJECT_ID
        fi
    fi
    
    # Get GitHub repository URL
    if [ -z "$GITHUB_REPO" ]; then
        GITHUB_REPO=$(git remote get-url origin 2>/dev/null || echo "")
        if [ -z "$GITHUB_REPO" ]; then
            read -p "Enter your GitHub repository URL (e.g., https://github.com/user/repo): " GITHUB_REPO
        fi
    fi
    
    # Extract owner and repo name from GitHub URL
    if [[ $GITHUB_REPO =~ github\.com[:/]([^/]+)/([^/]+) ]]; then
        GITHUB_OWNER="${BASH_REMATCH[1]}"
        GITHUB_REPO_NAME="${BASH_REMATCH[2]}"
        GITHUB_REPO_NAME="${GITHUB_REPO_NAME%.git}"  # Remove .git if present
    else
        print_error "Invalid GitHub repository URL format"
        exit 1
    fi
    
    print_success "Project ID: $PROJECT_ID"
    print_success "GitHub Repository: $GITHUB_OWNER/$GITHUB_REPO_NAME"
}

# Enable required APIs
enable_apis() {
    print_status "Enabling required Google Cloud APIs..."
    
    gcloud services enable cloudbuild.googleapis.com \
        run.googleapis.com \
        containerregistry.googleapis.com \
        storage.googleapis.com \
        bigquery.googleapis.com \
        secretmanager.googleapis.com \
        aiplatform.googleapis.com
    
    print_success "APIs enabled successfully!"
}

# Create Cloud Storage bucket
create_storage_bucket() {
    print_status "Creating Cloud Storage bucket for artifacts..."
    
    BUCKET_NAME="${PROJECT_ID}-doc-suite-artifacts"
    
    if ! gsutil ls -b gs://$BUCKET_NAME &> /dev/null; then
        gsutil mb gs://$BUCKET_NAME
        gsutil uniformbucketlevelaccess set on gs://$BUCKET_NAME
        print_success "Storage bucket created: gs://$BUCKET_NAME"
    else
        print_warning "Storage bucket already exists: gs://$BUCKET_NAME"
    fi
}

# Create BigQuery dataset
create_bigquery_dataset() {
    print_status "Creating BigQuery dataset for analytics..."
    
    DATASET_NAME="documentation_analytics"
    
    if ! bq ls -d $DATASET_NAME &> /dev/null; then
        bq mk --dataset --location=US $PROJECT_ID:$DATASET_NAME
        print_success "BigQuery dataset created: $DATASET_NAME"
    else
        print_warning "BigQuery dataset already exists: $DATASET_NAME"
    fi
}

# Set up secrets in Secret Manager
setup_secrets() {
    print_status "Setting up secrets in Secret Manager..."
    
    # Check if GEMINI_API_KEY secret exists
    if ! gcloud secrets describe gemini-api-key &> /dev/null; then
        if [ -z "$GEMINI_API_KEY" ]; then
            read -s -p "Enter your Gemini API Key: " GEMINI_API_KEY
            echo
        fi
        
        echo -n "$GEMINI_API_KEY" | gcloud secrets create gemini-api-key --data-file=-
        print_success "Gemini API Key secret created"
    else
        print_warning "Gemini API Key secret already exists"
    fi
}

# Connect GitHub repository to Cloud Build
connect_github() {
    print_status "Setting up GitHub connection..."
    
    print_warning "Manual step required:"
    echo "1. Go to https://console.cloud.google.com/cloud-build/triggers"
    echo "2. Click 'Connect Repository'"
    echo "3. Select GitHub and authenticate"
    echo "4. Select repository: $GITHUB_OWNER/$GITHUB_REPO_NAME"
    echo "5. Create a trigger with the following settings:"
    echo "   - Name: deploy-tech-doc-suite"
    echo "   - Event: Push to a branch"
    echo "   - Branch: ^main$"
    echo "   - Configuration: Cloud Build configuration file (yaml or json)"
    echo "   - File location: /cloudbuild.yaml"
    echo ""
    
    read -p "Press Enter after completing the GitHub connection setup..."
}

# Create initial deployment
initial_deployment() {
    print_status "Creating initial deployment..."
    
    # Build and deploy manually for the first time
    gcloud builds submit --config cloudbuild.yaml \
        --substitutions=_REGION=us-central1,_SERVICE_NAME=technical-documentation-suite
    
    print_success "Initial deployment completed!"
}

# Get service URL
get_service_url() {
    print_status "Getting service URL..."
    
    SERVICE_URL=$(gcloud run services describe technical-documentation-suite \
        --region=us-central1 --format="value(status.url)")
    
    print_success "Service deployed at: $SERVICE_URL"
}

# Main deployment function
main() {
    echo "🚀 Technical Documentation Suite - Google Cloud Deployment"
    echo "=========================================================="
    
    check_prerequisites
    get_project_config
    enable_apis
    create_storage_bucket
    create_bigquery_dataset
    setup_secrets
    connect_github
    initial_deployment
    get_service_url
    
    echo ""
    print_success "Deployment setup completed!"
    echo ""
    echo "📋 Next Steps:"
    echo "1. Your service is available at: $SERVICE_URL"
    echo "2. Push changes to your 'main' branch to trigger automatic deployments"
    echo "3. Monitor deployments at: https://console.cloud.google.com/cloud-build/builds"
    echo "4. View logs at: https://console.cloud.google.com/run/detail/us-central1/technical-documentation-suite/logs"
    echo ""
    echo "🔧 Configuration:"
    echo "- Project ID: $PROJECT_ID"
    echo "- Region: us-central1" 
    echo "- Storage Bucket: gs://${PROJECT_ID}-doc-suite-artifacts"
    echo "- BigQuery Dataset: documentation_analytics"
    echo ""
}

# Run main function
main "$@" 