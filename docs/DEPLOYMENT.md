# 🚀 Google Cloud Deployment Guide

This guide will help you deploy the Technical Documentation Suite to Google Cloud using **Cloud Run with continuous deployment** from your GitHub repository.

## 📋 Prerequisites

Before you begin, ensure you have:

1. **Google Cloud SDK** installed and authenticated
   ```bash
   # Install Google Cloud SDK
   curl https://sdk.cloud.google.com | bash
   exec -l $SHELL
   gcloud init
   ```

2. **A Google Cloud Project** with billing enabled
   ```bash
   # Create a new project (optional)
   gcloud projects create YOUR_PROJECT_ID
   gcloud config set project YOUR_PROJECT_ID
   ```

3. **GitHub repository** with your code
4. **Gemini API Key** from Google AI Studio

## 🔧 Deployment Options

### Option 1: Automated Deployment (Recommended)

This is the **continuous deployment from repository** approach that automatically deploys when you push to GitHub.

#### Step 1: Set up Service Account
```bash
./setup-service-account.sh
```

#### Step 2: Deploy to Google Cloud
```bash
./deploy-to-gcp.sh
```

This script will:
- ✅ Enable required Google Cloud APIs
- ✅ Create Cloud Storage bucket for artifacts
- ✅ Set up BigQuery dataset for analytics
- ✅ Configure Secret Manager for API keys
- ✅ Set up GitHub integration with Cloud Build
- ✅ Deploy the initial version to Cloud Run

### Option 2: Manual Deployment

If you prefer to deploy manually or from a container image:

#### Step 1: Build and push the container
```bash
# Set your project ID
export PROJECT_ID=your-project-id

# Build the container image
docker build -t gcr.io/$PROJECT_ID/technical-doc-suite:latest .

# Push to Container Registry
docker push gcr.io/$PROJECT_ID/technical-doc-suite:latest
```

#### Step 2: Deploy to Cloud Run
```bash
gcloud run deploy technical-documentation-suite \
  --image gcr.io/$PROJECT_ID/technical-doc-suite:latest \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --port 8080 \
  --memory 2Gi \
  --cpu 2 \
  --max-instances 10 \
  --set-env-vars GOOGLE_CLOUD_PROJECT=$PROJECT_ID \
  --set-secrets GEMINI_API_KEY=gemini-api-key:latest
```

## 🔑 Environment Variables

The application uses these environment variables:

| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_CLOUD_PROJECT` | Your Google Cloud Project ID | Yes |
| `GEMINI_API_KEY` | Google Gemini API Key (from Secret Manager) | Yes |
| `STORAGE_BUCKET` | Cloud Storage bucket for artifacts | Yes |
| `BIGQUERY_DATASET` | BigQuery dataset for analytics | Yes |
| `ENVIRONMENT` | Environment (production/development) | No |
| `LOG_LEVEL` | Logging level (INFO/DEBUG) | No |

## 🏗️ Architecture Overview

```
GitHub Repository
       ↓
   Cloud Build (CI/CD)
       ↓
  Container Registry
       ↓
    Cloud Run Service
       ↓
┌──────────────────────────┐
│  Technical Doc Suite     │
│  ├── FastAPI Backend    │
│  ├── React Frontend     │
│  └── AI Agents          │
└──────────────────────────┘
       ↓
┌──────────────────────────┐
│  Google Cloud Services   │
│  ├── Gemini AI API      │
│  ├── Cloud Storage      │
│  ├── BigQuery           │
│  └── Secret Manager     │
└──────────────────────────┘
```

## 🔄 Continuous Deployment

Once set up, the deployment process is automated:

1. **Push to GitHub** → Triggers Cloud Build
2. **Cloud Build** → Builds container image
3. **Container Registry** → Stores the image
4. **Cloud Run** → Deploys the new version
5. **Live Application** → Available at your service URL

## 📊 Monitoring and Logging

- **Cloud Run Logs**: `https://console.cloud.google.com/run/detail/us-central1/technical-documentation-suite/logs`
- **Build History**: `https://console.cloud.google.com/cloud-build/builds`
- **Metrics**: `https://console.cloud.google.com/run/detail/us-central1/technical-documentation-suite/metrics`

## 🛠️ Configuration Files

- **`cloudbuild.yaml`**: Cloud Build configuration for CI/CD
- **`Dockerfile`**: Multi-stage container build
- **`deployment/cloud-run-service.yaml`**: Cloud Run service configuration
- **`deploy-to-gcp.sh`**: Automated deployment script
- **`setup-service-account.sh`**: Service account setup script

## 🚨 Troubleshooting

### Common Issues

1. **Build Failures**
   ```bash
   # Check build logs
   gcloud builds list
   gcloud builds log BUILD_ID
   ```

2. **Permission Errors**
   ```bash
   # Verify service account permissions
   gcloud iam service-accounts get-iam-policy tech-doc-suite-sa@PROJECT_ID.iam.gserviceaccount.com
   ```

3. **Application Errors**
   ```bash
   # Check Cloud Run logs
   gcloud run services logs read technical-documentation-suite --region=us-central1
   ```

### Service URLs

After deployment, you'll get URLs like:
- **Service URL**: `https://technical-documentation-suite-HASH-uc.a.run.app`
- **Health Check**: `https://your-service-url/health`
- **API Docs**: `https://your-service-url/docs`

## 🔧 Local Development

To run locally with Google Cloud services:

```bash
# Set up service account key
export GOOGLE_APPLICATION_CREDENTIALS=./service-account-key.json

# Run the application
python -m uvicorn main:app --reload
```

## 📈 Scaling Configuration

The current configuration:
- **Memory**: 2GB
- **CPU**: 2 vCPUs
- **Max Instances**: 10
- **Concurrency**: 4 requests per instance
- **Timeout**: 15 minutes

Adjust these values in `cloudbuild.yaml` as needed.

## 🔒 Security

- ✅ Non-root container user
- ✅ Secrets managed via Secret Manager
- ✅ IAM roles with least privilege
- ✅ Service account authentication
- ✅ HTTPS-only traffic

## 💰 Cost Optimization

- **Cold starts**: Minimized with optimized container
- **Scaling**: Auto-scales to zero when not in use
- **Resource limits**: Set to prevent unexpected costs
- **Regional deployment**: Single region (us-central1) for lower latency

---

## 🎯 Quick Start

1. **Clone the repository**
2. **Run**: `./setup-service-account.sh`
3. **Run**: `./deploy-to-gcp.sh`
4. **Visit your service URL** and start generating documentation!

For questions or issues, check the [troubleshooting section](#🚨-troubleshooting) or create an issue in the repository. 