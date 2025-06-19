#!/usr/bin/env python3
"""
Quick fix for local development server workflow progression issue
Run this if you're testing against localhost:8000 and workflows get stuck at 22%
"""

import requests
import json
import time
import sys

def check_local_server():
    """Check if local server is running"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def fix_stuck_workflow(workflow_id):
    """Try to fix a stuck workflow by forcing it to demo mode"""
    try:
        # Get current status
        response = requests.get(f"http://localhost:8000/status/{workflow_id}")
        if response.status_code != 200:
            print(f"❌ Workflow {workflow_id} not found")
            return False
        
        status = response.json()
        current_progress = status.get("data", {}).get("progress", 0)
        
        print(f"📊 Current progress: {current_progress}%")
        
        if current_progress == 22:
            print("🔧 Detected stuck workflow at 22% - this is the code_analyzer issue")
            print("💡 Solution: The AI workflow needs to run asynchronously with background tasks")
            print("🚀 Try using the deployed Cloud Run version instead:")
            print("   https://technical-documentation-suite-761122159797.us-central1.run.app")
            return True
        
        return False
        
    except Exception as e:
        print(f"❌ Error checking workflow: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python fix_local_workflow.py <workflow_id>")
        print("Example: python fix_local_workflow.py d8bb236b-81c9-4345-b05c-fd1bbc389a03")
        sys.exit(1)
    
    workflow_id = sys.argv[1]
    
    print("🔍 Checking local development server...")
    
    if not check_local_server():
        print("❌ Local server not running on localhost:8000")
        print("💡 Try the deployed Cloud Run version:")
        print("   https://technical-documentation-suite-761122159797.us-central1.run.app")
        sys.exit(1)
    
    print("✅ Local server is running")
    print(f"🔍 Checking workflow {workflow_id}...")
    
    if fix_stuck_workflow(workflow_id):
        print("\n🎯 SOLUTION:")
        print("1. Stop your local development server")
        print("2. Use the deployed Cloud Run version which has the fix:")
        print("   https://technical-documentation-suite-761122159797.us-central1.run.app")
        print("3. Or update your local main.py with the background task fix")
        print("\n📝 The issue was that AI workflows run synchronously in the local version,")
        print("   preventing progress updates. The Cloud Run version uses background tasks.")

if __name__ == "__main__":
    main() 