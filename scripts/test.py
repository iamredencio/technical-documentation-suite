#!/usr/bin/env python3
"""
Test script for the Technical Documentation Suite
"""

import asyncio
import aiohttp
import json
import time
from typing import Dict, Any

class DocSuiteClient:
    """Client for testing the Technical Documentation Suite API"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
    
    async def health_check(self) -> Dict[str, Any]:
        """Check if the service is healthy"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/health") as response:
                return await response.json()
    
    async def generate_documentation(self, repository_url: str, project_id: str) -> Dict[str, Any]:
        """Generate documentation for a repository"""
        payload = {
            "repository_url": repository_url,
            "project_id": project_id,
            "output_formats": ["markdown", "html"],
            "include_diagrams": True,
            "target_audience": "developers"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/generate",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                return await response.json()
    
    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get the status of a workflow"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/status/{workflow_id}") as response:
                return await response.json()
    
    async def submit_feedback(self, workflow_id: str, rating: int = 4) -> Dict[str, Any]:
        """Submit feedback for a workflow"""
        payload = {
            "workflow_id": workflow_id,
            "user_id": "test_user",
            "rating": rating,
            "usefulness_score": 4,
            "accuracy_score": 5,
            "completeness_score": 3,
            "comments": "Test feedback from automated test"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/feedback",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                return await response.json()

async def run_tests(service_url: str):
    """Run comprehensive tests of the documentation suite"""
    client = DocSuiteClient(service_url)
    
    print("🧪 Starting Technical Documentation Suite Tests")
    print(f"🌐 Service URL: {service_url}")
    print("-" * 60)
    
    # Test 1: Health Check
    print("1️⃣  Testing health check...")
    try:
        health = await client.health_check()
        print(f"✅ Health check passed: {health['status']}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return
    
    # Test 2: Documentation Generation
    print("\n2️⃣  Testing documentation generation...")
    try:
        result = await client.generate_documentation(
            repository_url="https://github.com/fastapi/fastapi",
            project_id="fastapi-test-docs"
        )
        print(f"✅ Documentation generation initiated")
        print(f"📊 Result: {json.dumps(result, indent=2)}")
        
        if result.get("success") and "data" in result:
            workflow_id = result["data"].get("workflow_id")
            if workflow_id:
                print(f"📝 Workflow ID: {workflow_id}")
                
                # Test 3: Workflow Status
                print("\n3️⃣  Testing workflow status...")
                status = await client.get_workflow_status(workflow_id)
                print(f"✅ Status retrieved: {status}")
                
                # Test 4: Feedback Submission
                print("\n4️⃣  Testing feedback submission...")
                feedback_result = await client.submit_feedback(workflow_id)
                print(f"✅ Feedback submitted: {feedback_result}")
            
    except Exception as e:
        print(f"❌ Documentation generation failed: {e}")
    
    print("\n🎉 All tests completed!")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python test.py <service_url>")
        print("Example: python test.py https://technical-documentation-suite-xyz.run.app")
        sys.exit(1)
    
    service_url = sys.argv[1]
    asyncio.run(run_tests(service_url)) 