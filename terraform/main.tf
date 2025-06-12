terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

variable "project_id" {
  description = "Google Cloud Project ID"
  type        = string
}

variable "region" {
  description = "Google Cloud Region"
  type        = string
  default     = "us-central1"
}

# Enable required APIs
resource "google_project_service" "required_apis" {
  for_each = toset([
    "run.googleapis.com",
    "cloudbuild.googleapis.com",
    "storage.googleapis.com",
    "bigquery.googleapis.com",
    "artifactregistry.googleapis.com"
  ])
  
  service = each.key
  project = var.project_id
}

# Cloud Storage bucket for documentation artifacts
resource "google_storage_bucket" "doc_artifacts" {
  name     = "${var.project_id}-doc-suite-artifacts"
  location = var.region
  
  uniform_bucket_level_access = true
  
  versioning {
    enabled = true
  }
  
  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      age = 90
    }
  }
}

# BigQuery dataset for analytics
resource "google_bigquery_dataset" "documentation_analytics" {
  dataset_id  = "documentation_analytics"
  location    = var.region
  description = "Analytics data for technical documentation suite"
  
  delete_contents_on_destroy = false
}

# BigQuery table for user feedback
resource "google_bigquery_table" "user_feedback" {
  dataset_id = google_bigquery_dataset.documentation_analytics.dataset_id
  table_id   = "user_feedback"
  
  schema = jsonencode([
    {
      name = "workflow_id"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "timestamp"
      type = "TIMESTAMP"
      mode = "REQUIRED"
    },
    {
      name = "user_id"
      type = "STRING"
      mode = "NULLABLE"
    },
    {
      name = "rating"
      type = "INTEGER"
      mode = "NULLABLE"
    },
    {
      name = "usefulness_score"
      type = "INTEGER"
      mode = "NULLABLE"
    },
    {
      name = "accuracy_score"
      type = "INTEGER"
      mode = "NULLABLE"
    },
    {
      name = "completeness_score"
      type = "INTEGER"
      mode = "NULLABLE"
    },
    {
      name = "comments"
      type = "STRING"
      mode = "NULLABLE"
    }
  ])
}

# Artifact Registry repository
resource "google_artifact_registry_repository" "doc_suite_repo" {
  location      = var.region
  repository_id = "technical-doc-suite"
  description   = "Container repository for technical documentation suite"
  format        = "DOCKER"
}

# Service account for Cloud Run
resource "google_service_account" "doc_suite_sa" {
  account_id   = "doc-suite-service"
  display_name = "Technical Documentation Suite Service Account"
  description  = "Service account for technical documentation suite"
}

# IAM bindings for service account
resource "google_project_iam_member" "doc_suite_permissions" {
  for_each = toset([
    "roles/storage.objectAdmin",
    "roles/bigquery.dataEditor",
    "roles/bigquery.jobUser"
  ])
  
  project = var.project_id
  role    = each.key
  member  = "serviceAccount:${google_service_account.doc_suite_sa.email}"
}

# Cloud Run service
resource "google_cloud_run_service" "doc_suite" {
  name     = "technical-documentation-suite"
  location = var.region
  
  template {
    spec {
      service_account_name = google_service_account.doc_suite_sa.email
      
      containers {
        image = "${var.region}-docker.pkg.dev/${var.project_id}/technical-doc-suite/app:latest"
        
        ports {
          container_port = 8080
        }
        
        env {
          name  = "GOOGLE_CLOUD_PROJECT"
          value = var.project_id
        }
        
        env {
          name  = "STORAGE_BUCKET"
          value = google_storage_bucket.doc_artifacts.name
        }
        
        env {
          name  = "BIGQUERY_DATASET"
          value = google_bigquery_dataset.documentation_analytics.dataset_id
        }
        
        resources {
          limits = {
            cpu    = "2"
            memory = "2Gi"
          }
        }
      }
    }
    
    metadata {
      annotations = {
        "autoscaling.knative.dev/maxScale" = "10"
        "run.googleapis.com/cpu-throttling" = "false"
      }
    }
  }
  
  traffic {
    percent         = 100
    latest_revision = true
  }
  
  depends_on = [google_project_service.required_apis]
}

# Allow public access to Cloud Run service
resource "google_cloud_run_service_iam_member" "public_access" {
  location = google_cloud_run_service.doc_suite.location
  project  = google_cloud_run_service.doc_suite.project
  service  = google_cloud_run_service.doc_suite.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Output the Cloud Run service URL
output "service_url" {
  value = google_cloud_run_service.doc_suite.status[0].url
  description = "URL of the deployed Technical Documentation Suite"
}

output "storage_bucket" {
  value = google_storage_bucket.doc_artifacts.name
  description = "Name of the Cloud Storage bucket for documentation artifacts"
}

output "bigquery_dataset" {
  value = google_bigquery_dataset.documentation_analytics.dataset_id
  description = "BigQuery dataset for analytics"
} 