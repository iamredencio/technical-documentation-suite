#!/usr/bin/env python3
"""
Development entry point for Technical Documentation Suite
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import and run the application
from tech_doc_suite.main import main

if __name__ == "__main__":
    main() 