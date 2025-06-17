#!/bin/bash

# Clean Environment Script
# Removes virtual environments and prepares for conda usage

echo "🧹 Cleaning up virtual environments..."

# Remove venv directories
if [ -d "venv" ]; then
    echo "🗑️  Removing venv directory..."
    rm -rf venv
    echo "✅ venv removed"
fi

if [ -d ".venv" ]; then
    echo "🗑️  Removing .venv directory..."
    rm -rf .venv
    echo "✅ .venv removed"
fi

# Kill any running processes on ports 3000 and 8080
echo "🛑 Stopping any running servers..."
lsof -ti:3000 | xargs kill -9 2>/dev/null
lsof -ti:8080 | xargs kill -9 2>/dev/null

echo "✅ Environment cleaned!"
echo ""
echo "Now you can run:"
echo "  conda activate tech_doc_suit"
echo "  ./start_application.sh" 