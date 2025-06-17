# test_e2e_workflow.py
import asyncio
import aiohttp
import json
import time
import sys
import os

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import agents
from src.agents.base_agent import Message

async def test_complete_agent_workflow():
    """Test the complete multi-agent workflow locally"""
    print("🔄 Testing Complete Multi-Agent Workflow")
    print("=" * 45)
    
    try:
        # Step 1: Code Analysis
        print("\n1️⃣ Testing Code Analysis...")
        code_analyzer = agents["code_analyzer"]
        
        analysis_message = Message(
            type="analyze_repository",
            data={
                "repository_url": "https://github.com/fastapi/fastapi",
                "project_id": "fastapi-test-analysis"
            },
            sender="workflow_test",
            recipient=code_analyzer.agent_id
        )
        
        analysis_response = await code_analyzer.handle_message(analysis_message)
        
        if analysis_response and analysis_response.type == "repository_analysis_complete":
            print("✅ Code analysis completed successfully")
            print(f"   - Project: {analysis_response.data.get('project_id')}")
            print(f"   - Files: {analysis_response.data.get('file_count')}")
            print(f"   - Lines of Code: {analysis_response.data.get('lines_of_code')}")
            print(f"   - Functions: {len(analysis_response.data.get('functions', []))}")
            print(f"   - Classes: {len(analysis_response.data.get('classes', []))}")
            
            analysis_data = analysis_response.data
        else:
            print("❌ Code analysis failed")
            return False
        
        # Step 2: Documentation Generation
        print("\n2️⃣ Testing Documentation Generation...")
        doc_writer = agents["doc_writer"]
        
        doc_message = Message(
            type="generate_documentation",
            data={
                "analysis": analysis_data,
                "format": "markdown",
                "audience": "developers"
            },
            sender="workflow_test",
            recipient=doc_writer.agent_id
        )
        
        doc_response = await doc_writer.handle_message(doc_message)
        
        if doc_response and doc_response.type == "documentation_generated":
            print("✅ Documentation generated successfully")
            print(f"   - Format: {doc_response.data.get('format')}")
            print(f"   - Sections: {doc_response.data.get('sections')}")
            print(f"   - Word Count: {doc_response.data.get('word_count')}")
            print(f"   - Content Length: {len(doc_response.data.get('content', ''))}")
            
            documentation_content = doc_response.data.get('content', '')
        else:
            print("❌ Documentation generation failed")
            return False
        
        # Step 3: Diagram Generation
        print("\n3️⃣ Testing Diagram Generation...")
        diagram_gen = agents["diagram_generator"]
        
        diagram_message = Message(
            type="generate_diagram",
            data={
                "type": "architecture",
                "analysis": analysis_data
            },
            sender="workflow_test",
            recipient=diagram_gen.agent_id
        )
        
        diagram_response = await diagram_gen.handle_message(diagram_message)
        
        if diagram_response and diagram_response.type == "diagram_generated":
            print("✅ Diagram generated successfully")
            print(f"   - Type: {diagram_response.data.get('diagram_type')}")
            print(f"   - Format: {diagram_response.data.get('format')}")
            print(f"   - Content Length: {len(diagram_response.data.get('content', ''))}")
            
            diagram_content = diagram_response.data.get('content', '')
        else:
            print("❌ Diagram generation failed")
            return False
        
        # Step 4: Quality Review
        print("\n4️⃣ Testing Quality Review...")
        quality_reviewer = agents["quality_reviewer"]
        
        quality_message = Message(
            type="review_documentation",
            data={
                "content": documentation_content,
                "analysis": analysis_data
            },
            sender="workflow_test",
            recipient=quality_reviewer.agent_id
        )
        
        quality_response = await quality_reviewer.handle_message(quality_message)
        
        if quality_response and quality_response.type == "quality_review_complete":
            print("✅ Quality review completed successfully")
            print(f"   - Quality Score: {quality_response.data.get('quality_score'):.2f}")
            print(f"   - Metrics: {list(quality_response.data.get('metrics', {}).keys())}")
            print(f"   - Suggestions: {len(quality_response.data.get('suggestions', []))}")
            
            quality_score = quality_response.data.get('quality_score', 0)
        else:
            print("❌ Quality review failed")
            return False
        
        # Step 5: Workflow Orchestration Test
        print("\n5️⃣ Testing Workflow Orchestration...")
        orchestrator = agents["orchestrator"]
        
        workflow_id = f"test-workflow-{int(time.time())}"
        workflow_message = Message(
            type="start_workflow",
            data={
                "workflow_id": workflow_id,
                "repository_url": "https://github.com/fastapi/fastapi",
                "project_id": "fastapi-orchestrated-test"
            },
            sender="workflow_test",
            recipient=orchestrator.agent_id
        )
        
        workflow_response = await orchestrator.handle_message(workflow_message)
        
        if workflow_response and workflow_response.type == "workflow_started":
            print("✅ Workflow orchestration started successfully")
            print(f"   - Workflow ID: {workflow_response.data.get('workflow_id')}")
            print(f"   - Total Steps: {workflow_response.data.get('total_steps')}")
            print(f"   - Current Step: {workflow_response.data.get('current_step')}")
        else:
            print("❌ Workflow orchestration failed")
            return False
        
        # Step 6: Feedback Collection Test
        print("\n6️⃣ Testing Feedback Collection...")
        feedback_agent = agents["feedback_collector"]
        
        feedback_message = Message(
            type="collect_feedback",
            data={
                "workflow_id": workflow_id,
                "rating": 4,
                "usefulness_score": 4,
                "accuracy_score": 5,
                "completeness_score": 3,
                "comments": "Comprehensive E2E test feedback"
            },
            sender="workflow_test",
            recipient=feedback_agent.agent_id
        )
        
        feedback_response = await feedback_agent.handle_message(feedback_message)
        
        if feedback_response and feedback_response.type == "feedback_collected":
            print("✅ Feedback collection completed successfully")
            print(f"   - Feedback ID: {feedback_response.data.get('feedback_id')}")
            print(f"   - Status: {feedback_response.data.get('status')}")
        else:
            print("❌ Feedback collection failed")
            return False
        
        # Final Results Summary
        print("\n🎉 Complete Workflow Test Results:")
        print("=" * 40)
        print(f"✅ Code Analysis: {analysis_data.get('file_count')} files analyzed")
        print(f"✅ Documentation: {len(documentation_content)} characters generated")
        print(f"✅ Diagrams: {len(diagram_content)} characters of Mermaid code")
        print(f"✅ Quality Score: {quality_score:.2f}/1.0")
        print(f"✅ Workflow: {workflow_id} orchestrated")
        print(f"✅ Feedback: Collected and stored")
        
        return True
        
    except Exception as e:
        print(f"❌ Workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_api_workflow_integration(service_url: str = "http://localhost:8080"):
    """Test the API integration with the agent workflow"""
    print("\n🌐 Testing API Integration")
    print("=" * 30)
    
    async with aiohttp.ClientSession() as session:
        try:
            # Test 1: Health Check
            print("1️⃣ Testing health endpoint...")
            async with session.get(f"{service_url}/health") as response:
                if response.status == 200:
                    health_data = await response.json()
                    print(f"✅ Health check successful: {health_data['status']}")
                else:
                    print(f"❌ Health check failed: {response.status}")
                    return False
            
            # Test 2: Generate Documentation
            print("\n2️⃣ Testing documentation generation...")
            
            payload = {
                "repository_url": "https://github.com/python/cpython",  
                "project_id": "python-docs-api-test",
                "output_formats": ["markdown"],
                "include_diagrams": True,
                "target_audience": "developers"
            }
            
            async with session.post(
                f"{service_url}/generate",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✅ Generation initiated: {result.get('success')}")
                    
                    workflow_id = result['data'].get('workflow_id')
                    if workflow_id:
                        print(f"✅ Workflow ID: {workflow_id}")
                    else:
                        print("❌ No workflow ID received")
                        return False
                else:
                    print(f"❌ Generation failed: {response.status}")
                    return False
            
            # Test 3: Check Status
            print("\n3️⃣ Testing status endpoint...")
            async with session.get(f"{service_url}/status/{workflow_id}") as response:
                if response.status == 200:
                    status_result = await response.json()
                    status = status_result['data'].get('status', 'unknown')
                    progress = status_result['data'].get('progress', 0)
                    print(f"✅ Status check successful: {status} ({progress}%)")
                else:
                    print(f"❌ Status check failed: {response.status}")
                    return False
            
            # Test 4: Submit Feedback
            print("\n4️⃣ Testing feedback submission...")
            
            feedback_payload = {
                "workflow_id": workflow_id,
                "user_id": "api_test_user",
                "rating": 5,
                "usefulness_score": 4,
                "accuracy_score": 5,
                "completeness_score": 4,
                "comments": "API integration test feedback"
            }
            
            async with session.post(
                f"{service_url}/feedback",
                json=feedback_payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    feedback_result = await response.json()
                    print(f"✅ Feedback submitted: {feedback_result.get('success')}")
                else:
                    print(f"❌ Feedback submission failed: {response.status}")
                    return False
            
            print("\n🎉 API integration test completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ API integration test failed: {e}")
            return False

if __name__ == "__main__":
    print("🧪 Starting Comprehensive Testing Suite")
    print("=" * 50)
    
    # Test 1: Agent Workflow
    workflow_success = asyncio.run(test_complete_agent_workflow())
    
    # Test 2: API Integration
    api_success = asyncio.run(test_api_workflow_integration())
    
    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 25)
    print(f"Agent Workflow: {'✅ PASS' if workflow_success else '❌ FAIL'}")
    print(f"API Integration: {'✅ PASS' if api_success else '❌ FAIL'}")
    
    if workflow_success and api_success:
        print("\n🏆 All tests passed! Your Technical Documentation Suite is ready for deployment!")
    else:
        print("\n⚠️  Some tests failed. Please review the output above.")
    
    # Exit with proper code
    sys.exit(0 if (workflow_success and api_success) else 1) 