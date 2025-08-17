#!/usr/bin/env python3
"""
Test the DSQL Assistant agent
"""

import sys
import os

# Add the agentcore path to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
agentcore_path = os.path.join(current_dir, 'agentcore-strands-db-mcp-assistant')
sys.path.insert(0, agentcore_path)

def test_agent_imports():
    """Test if we can import all required components"""
    print("=== Testing Agent Imports ===")
    
    try:
        from agent_config.memory_hook_provider import MemoryHook
        print("✅ Successfully imported MemoryHook")
    except ImportError as e:
        print(f"❌ Failed to import MemoryHook: {e}")
        return False
        
    try:
        from agent_config.tools.dsql_mcp_assistant import dsql_assistant
        print("✅ Successfully imported dsql_assistant")
    except ImportError as e:
        print(f"❌ Failed to import dsql_assistant: {e}")
        return False
        
    try:
        from strands import Agent
        from strands_tools import think
        from strands.models import BedrockModel
        print("✅ Successfully imported Strands components")
    except ImportError as e:
        print(f"❌ Failed to import Strands components: {e}")
        return False
        
    return True

def test_agent_creation():
    """Test if we can create the DSQLAssistant"""
    print("\n=== Testing Agent Creation ===")
    
    try:
        from agent_config.memory_hook_provider import MemoryHook
        from agent_config.agent import DSQLAssistant
        from bedrock_agentcore.memory import MemoryClient
        
        # Create a mock memory client and hook for testing
        # In real AgentCore, these would be provided by the runtime
        try:
            memory_client = MemoryClient()
            memory_hook = MemoryHook(
                memory_client=memory_client,
                memory_id="test-memory-id",
                actor_id="test-actor-id", 
                session_id="test-session-id"
            )
            print("✅ Created MemoryHook with real MemoryClient")
        except Exception as e:
            print(f"⚠️  Could not create real MemoryClient: {e}")
            # Create a minimal mock for testing
            class MockMemoryClient:
                def get_last_k_turns(self, **kwargs):
                    return []
                def save_conversation(self, **kwargs):
                    pass
            
            memory_hook = MemoryHook(
                memory_client=MockMemoryClient(),
                memory_id="test-memory-id",
                actor_id="test-actor-id", 
                session_id="test-session-id"
            )
            print("✅ Created MemoryHook with mock MemoryClient")
        
        # Create the DSQL Assistant
        assistant = DSQLAssistant(memory_hook=memory_hook)
        print("✅ Successfully created DSQLAssistant")
        
        # Check if the agent has the right tools
        tool_names = [tool.__name__ if hasattr(tool, '__name__') else str(tool) for tool in assistant.tools]
        print(f"✅ Agent tools: {tool_names}")
        
        # Check system prompt
        print(f"✅ System prompt length: {len(assistant.system_prompt)} characters")
        
        return True, assistant
        
    except Exception as e:
        print(f"❌ Failed to create DSQLAssistant: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False, None

def test_agent_invoke():
    """Test if we can invoke the agent with a simple query"""
    print("\n=== Testing Agent Invocation ===")
    
    success, assistant = test_agent_creation()
    if not success:
        return False
        
    try:
        # Test with a simple query
        test_query = "What is the database schema?"
        print(f"Testing query: '{test_query}'")
        
        response = assistant.invoke(test_query)
        print(f"✅ Agent response received (length: {len(response)})")
        print(f"Response preview: {response[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent invocation failed: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    print("=== DSQL Assistant Agent Test ===\n")
    
    imports_ok = test_agent_imports()
    if not imports_ok:
        print("\n❌ Import tests failed. Cannot proceed.")
        sys.exit(1)
    
    creation_ok, _ = test_agent_creation()
    if not creation_ok:
        print("\n❌ Agent creation failed. Cannot proceed.")
        sys.exit(1)
    
    # Only test invocation if user wants to (it will make actual calls)
    print("\n⚠️  Agent invocation test will make actual calls to AWS services.")
    print("This will test the full functionality but may take time and use resources.")
    
    user_input = input("Do you want to test agent invocation? (y/N): ").strip().lower()
    if user_input in ['y', 'yes']:
        invoke_ok = test_agent_invoke()
        if invoke_ok:
            print("\n🎉 All tests passed! The agent is working correctly.")
        else:
            print("\n❌ Agent invocation test failed.")
    else:
        print("\n✅ Basic tests passed. Agent structure is correct.")
        print("To test full functionality, run with invocation test enabled.")