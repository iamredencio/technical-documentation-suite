.PHONY: help install install-dev test test-cov lint format clean build deploy dev frontend docs

# Default target
help:  ## Show this help message
	@echo "Technical Documentation Suite - Development Commands"
	@echo "=================================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Environment setup
install:  ## Install production dependencies
	pip install -e .

install-dev:  ## Install development dependencies
	pip install -e ".[dev,test,docs]"
	pre-commit install

# Development
dev:  ## Start development server
	python run.py

dev-uvicorn:  ## Start development server with uvicorn
	cd src && python -m uvicorn tech_doc_suite.main:app --reload --host 0.0.0.0 --port 8080

frontend:  ## Start frontend development server
	cd frontend && npm start

# Testing
test:  ## Run tests
	pytest tests/ -v

test-cov:  ## Run tests with coverage
	pytest tests/ -v --cov=src/tech_doc_suite --cov-report=html --cov-report=term

test-integration:  ## Run integration tests
	pytest tests/ -v -m integration

# Code quality
lint:  ## Run linting
	ruff check src/ tests/
	mypy src/

format:  ## Format code
	black src/ tests/
	isort src/ tests/
	ruff check --fix src/ tests/

# Cleaning
clean:  ## Clean up build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Building
build:  ## Build the package
	python -m build

# Deployment
deploy-gcp:  ## Deploy to Google Cloud Run
	./scripts/deploy-to-gcp.sh

deploy-docker:  ## Build and run Docker container
	docker build -f deployment/Dockerfile -t tech-doc-suite .
	docker run -p 8080:8080 --env-file .env tech-doc-suite

# Infrastructure
terraform-init:  ## Initialize Terraform
	cd terraform && terraform init

terraform-plan:  ## Plan Terraform changes
	cd terraform && terraform plan

terraform-apply:  ## Apply Terraform changes
	cd terraform && terraform apply

# Documentation
docs:  ## Build documentation
	cd docs && mkdocs build

docs-serve:  ## Serve documentation locally
	cd docs && mkdocs serve

# Security
security-check:  ## Run security checks
	safety check
	bandit -r src/

# Database/Setup
setup:  ## Initial project setup
	cp env.example .env
	@echo "Please edit .env with your configuration"
	make install-dev
	@echo "Setup complete! Run 'make dev' to start development server" 