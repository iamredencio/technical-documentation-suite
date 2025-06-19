"""
Configuration settings for Technical Documentation Suite
"""

import os
import logging
from pathlib import Path

# Environment detection
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
DEBUG = ENVIRONMENT == 'development'

# Server configuration
PORT = int(os.getenv('PORT', 8080))
HOST = os.getenv('HOST', '0.0.0.0')

# API Configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
API_TIMEOUT = int(os.getenv('API_TIMEOUT', 300))  # 5 minutes default

# Logging configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO' if not DEBUG else 'DEBUG')
LOG_FILE = os.getenv('LOG_FILE', 'app.log')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT = os.getenv('GOOGLE_CLOUD_PROJECT')
GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

# CORS Configuration
ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000').split(',')

# Security
SECRET_KEY = os.getenv('SECRET_KEY', 'development-key-change-in-production')

# File paths
BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / 'frontend' / 'build'
LOG_DIR = BASE_DIR / 'logs'

# Ensure log directory exists
LOG_DIR.mkdir(exist_ok=True)

def setup_logging():
    """Configure application logging"""
    
    # Set log level
    level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
    
    # Configure logging
    handlers = []
    
    # Console handler for development
    if DEBUG:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        handlers.append(console_handler)
    
    # File handler for production
    if not DEBUG or os.getenv('LOG_TO_FILE'):
        file_handler = logging.FileHandler(LOG_DIR / LOG_FILE)
        file_handler.setLevel(level)
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        handlers.append(file_handler)
    
    # Basic config
    logging.basicConfig(
        level=level,
        format=LOG_FORMAT,
        handlers=handlers,
        force=True
    )
    
    # Suppress noisy third-party loggers in production
    if not DEBUG:
        logging.getLogger('uvicorn.access').setLevel(logging.WARNING)
        logging.getLogger('httpx').setLevel(logging.WARNING)
        logging.getLogger('urllib3').setLevel(logging.WARNING)

def get_ai_status():
    """Get AI service status"""
    return {
        "enabled": GEMINI_API_KEY is not None,
        "api_key_set": bool(GEMINI_API_KEY),
        "environment": ENVIRONMENT,
        "timeout": API_TIMEOUT
    }

# Application metadata
APP_INFO = {
    "name": "Technical Documentation Suite",
    "version": "1.0.0",
    "description": "AI-Powered Multi-Agent Documentation Generator",
    "author": "Google Cloud ADK Hackathon Team",
    "built_for": "Google Cloud ADK Hackathon 2024"
} 