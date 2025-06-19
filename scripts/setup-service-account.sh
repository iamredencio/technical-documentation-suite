#!/bin/bash

# Setup Service Account and IAM permissions for Technical Documentation Suite
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

# Get project ID
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
if [ -z "$PROJECT_ID" ]; then
    read -p "Enter your Google Cloud Project ID: " PROJECT_ID
    gcloud config set project $PROJECT_ID
fi

print_status "Setting up service account and permissions for project: $PROJECT_ID"

# Service account details
SERVICE_ACCOUNT_NAME="tech-doc-suite-sa"
SERVICE_ACCOUNT_EMAIL="$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com"

# Create service account
print_status "Creating service account..."
if ! gcloud iam service-accounts describe $SERVICE_ACCOUNT_EMAIL &> /dev/null; then
    gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \
        --display-name="Technical Documentation Suite Service Account" \
        --description="Service account for the Technical Documentation Suite application"
    print_success "Service account created: $SERVICE_ACCOUNT_EMAIL"
else
    print_warning "Service account already exists: $SERVICE_ACCOUNT_EMAIL"
fi

# Grant required roles to the service account
print_status "Granting IAM roles to service account..."

ROLES=(
    "roles/storage.admin"
    "roles/bigquery.admin"
    "roles/secretmanager.secretAccessor"
    "roles/aiplatform.user"
    "roles/logging.logWriter"
    "roles/monitoring.metricWriter"
    "roles/cloudtrace.agent"
)

for role in "${ROLES[@]}"; do
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
        --role="$role" \
        --quiet
    print_success "Granted role: $role"
done

# Grant Cloud Build service account permissions
print_status "Setting up Cloud Build permissions..."

CLOUD_BUILD_SA="$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')@cloudbuild.gserviceaccount.com"

# Grant Cloud Build permissions to deploy to Cloud Run
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$CLOUD_BUILD_SA" \
    --role="roles/run.admin" \
    --quiet

# Grant Cloud Build permissions to act as the service account
gcloud iam service-accounts add-iam-policy-binding $SERVICE_ACCOUNT_EMAIL \
    --member="serviceAccount:$CLOUD_BUILD_SA" \
    --role="roles/iam.serviceAccountUser" \
    --quiet

# Grant Cloud Build permissions to access secrets
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$CLOUD_BUILD_SA" \
    --role="roles/secretmanager.secretAccessor" \
    --quiet

print_success "Cloud Build permissions configured"

# Create key file for local development (optional)
print_status "Creating service account key for local development..."
KEY_FILE="service-account-key.json"

if [ ! -f "$KEY_FILE" ]; then
    gcloud iam service-accounts keys create $KEY_FILE \
        --iam-account=$SERVICE_ACCOUNT_EMAIL
    print_success "Service account key created: $KEY_FILE"
    print_warning "Keep this key file secure and do not commit it to version control!"
    
    # Add to .gitignore if not already there
    if ! grep -q "$KEY_FILE" .gitignore 2>/dev/null; then
        echo "$KEY_FILE" >> .gitignore
        print_status "Added $KEY_FILE to .gitignore"
    fi
else
    print_warning "Service account key file already exists: $KEY_FILE"
fi

print_success "Service account setup completed!"
echo ""
echo "📋 Summary:"
echo "- Service Account: $SERVICE_ACCOUNT_EMAIL"
echo "- Key File: $KEY_FILE (for local development)"
echo "- IAM Roles: ${ROLES[*]}"
echo ""
echo "🔧 To use locally, set the environment variable:"
echo "export GOOGLE_APPLICATION_CREDENTIALS=./$KEY_FILE" 