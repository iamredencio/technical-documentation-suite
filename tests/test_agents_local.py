# test_agents_local.py
import asyncio
import sys
import os

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from tech_doc_suite.main import agents
from tech_doc_suite.agents.base_agent import Message

async def test_individual_agents():
    """Test each agent individually"""
    print("🧪 Testing Individual Agents Locally")
    print("=" * 50)
    
    # Test 1: Code Analyzer Agent
    print("\n1️⃣ Testing Code Analyzer Agent...")
    try:
        code_analyzer = agents["code_analyzer"]
        print("✅ Code Analyzer Agent initialized successfully")
        print(f"✅ Agent ID: {code_analyzer.agent_id}")
        print(f"✅ Agent Name: {code_analyzer.name}")
        print(f"✅ Agent State: {code_analyzer.state}")
        print(f"✅ Supported Languages: {code_analyzer.supported_languages}")
        
        # Test health check
        health = await code_analyzer.health_check()
        print(f"✅ Health Check: {'Healthy' if health else 'Unhealthy'}")
        
    except Exception as e:
        print(f"❌ Code Analyzer Agent failed: {e}")
    
    # Test 2: Documentation Writer Agent
    print("\n2️⃣ Testing Documentation Writer Agent...")
    try:
        doc_writer = agents["doc_writer"]
        print("✅ Documentation Writer Agent initialized successfully")
        print(f"✅ Agent ID: {doc_writer.agent_id}")
        print(f"✅ Agent Name: {doc_writer.name}")
        print(f"✅ Supported Formats: {doc_writer.supported_formats}")
        print("✅ Templates loaded:", list(doc_writer.templates.keys()))
        
        # Test health check
        health = await doc_writer.health_check()
        print(f"✅ Health Check: {'Healthy' if health else 'Unhealthy'}")
        
    except Exception as e:
        print(f"❌ Documentation Writer Agent failed: {e}")
    
    # Test 3: Translation Agent
    print("\n3️⃣ Testing Translation Agent...")
    try:
        translation_agent = agents["translation_agent"]
        print("✅ Translation Agent initialized successfully")
        print(f"✅ Agent ID: {translation_agent.agent_id}")
        print(f"✅ Agent Name: {translation_agent.name}")
        print(f"✅ Supported Languages: {list(translation_agent.supported_languages.keys())}")
        print(f"✅ Language Details: {translation_agent.supported_languages}")
        
        # Test health check
        health = await translation_agent.health_check()
        print(f"✅ Health Check: {'Healthy' if health else 'Unhealthy'}")
        
    except Exception as e:
        print(f"❌ Translation Agent failed: {e}")
    
    # Test 4: Diagram Generator Agent
    print("\n4️⃣ Testing Diagram Generator Agent...")
    try:
        diagram_gen = agents["diagram_generator"]
        print("✅ Diagram Generator Agent initialized successfully")
        print(f"✅ Agent ID: {diagram_gen.agent_id}")
        print(f"✅ Agent Name: {diagram_gen.name}")
        print(f"✅ Diagram Types: {diagram_gen.diagram_types}")
        
        # Test health check
        health = await diagram_gen.health_check()
        print(f"✅ Health Check: {'Healthy' if health else 'Unhealthy'}")
        
    except Exception as e:
        print(f"❌ Diagram Generator Agent failed: {e}")
    
    # Test 5: Quality Reviewer Agent
    print("\n5️⃣ Testing Quality Reviewer Agent...")
    try:
        quality_reviewer = agents["quality_reviewer"]
        print("✅ Quality Reviewer Agent initialized successfully")
        print(f"✅ Agent ID: {quality_reviewer.agent_id}")
        print(f"✅ Agent Name: {quality_reviewer.name}")
        print("✅ Quality metrics template:", list(quality_reviewer.quality_metrics.keys()))
        
        # Test health check
        health = await quality_reviewer.health_check()
        print(f"✅ Health Check: {'Healthy' if health else 'Unhealthy'}")
        
    except Exception as e:
        print(f"❌ Quality Reviewer Agent failed: {e}")
    
    # Test 6: Content Orchestrator Agent
    print("\n6️⃣ Testing Content Orchestrator Agent...")
    try:
        orchestrator = agents["orchestrator"]
        print("✅ Content Orchestrator Agent initialized successfully")
        print(f"✅ Agent ID: {orchestrator.agent_id}")
        print(f"✅ Agent Name: {orchestrator.name}")
        print(f"✅ Workflow Steps: {orchestrator.workflow_steps}")
        print("✅ Workflow status tracking ready")
        
        # Test health check
        health = await orchestrator.health_check()
        print(f"✅ Health Check: {'Healthy' if health else 'Unhealthy'}")
        
    except Exception as e:
        print(f"❌ Content Orchestrator Agent failed: {e}")
    
    # Test 7: User Feedback Agent
    print("\n7️⃣ Testing User Feedback Agent...")
    try:
        feedback_agent = agents["feedback_collector"]
        print("✅ User Feedback Agent initialized successfully")
        print(f"✅ Agent ID: {feedback_agent.agent_id}")
        print(f"✅ Agent Name: {feedback_agent.name}")
        print(f"✅ Feedback Store: {len(feedback_agent.feedback_store)} items")
        
        # Test health check
        health = await feedback_agent.health_check()
        print(f"✅ Health Check: {'Healthy' if health else 'Unhealthy'}")
        
    except Exception as e:
        print(f"❌ User Feedback Agent failed: {e}")
    
    print("\n🎉 Individual agent testing complete!")
    print(f"📊 Total agents tested: 7")

async def test_agent_communication():
    """Test basic agent-to-agent communication"""
    print("\n📨 Testing Agent Communication")
    print("=" * 35)
    
    try:
        code_analyzer = agents["code_analyzer"]
        doc_writer = agents["doc_writer"]
        
        # Create a test message
        test_message = Message(
            type="analyze_repository",
            data={
                "repository_url": "https://github.com/test/repo",
                "project_id": "test-project"
            },
            sender="test_client",
            recipient=code_analyzer.agent_id
        )
        
        print(f"✅ Test message created: {test_message.type}")
        print(f"✅ Message ID: {test_message.message_id}")
        print(f"✅ Sender: {test_message.sender}")
        print(f"✅ Recipient: {test_message.recipient}")
        
        # Test message handling (without starting the agent loop)
        response = await code_analyzer.handle_message(test_message)
        
        if response:
            print(f"✅ Message processed successfully")
            print(f"✅ Response type: {response.type}")
            print(f"✅ Response data keys: {list(response.data.keys())}")
        else:
            print("❌ No response received")
        
    except Exception as e:
        print(f"❌ Agent communication test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_individual_agents())
    asyncio.run(test_agent_communication()) 