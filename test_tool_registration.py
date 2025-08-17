#!/usr/bin/env python3
"""
Test if the DSQL assistant tool is properly registered in AgentCore
"""

import sys
import os

# Add the agentcore path to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
agentcore_path = os.path.join(current_dir, 'agentcore-strands-db-mcp-assistant')
sys.path.insert(0, agentcore_path)

def test_tool_import():
    """Test if we can import the DSQL assistant tool"""
    print("=== Testing Tool Import ===")
    
    try:
        from agent_config.tools.dsql_mcp_assistant import dsql_assistant
        print("✅ Successfully imported dsql_assistant function")
        
        # Check if it's properly decorated as a tool
        if hasattr(dsql_assistant, '__wrapped__'):
            print("✅ Function is properly decorated with @tool")
        else:
            print("⚠️  Function might not be properly decorated")
            
        # Check function signature
        import inspect
        sig = inspect.signature(dsql_assistant)
        print(f"✅ Function signature: {sig}")
        
        # Check docstring
        if dsql_assistant.__doc__:
            print("✅ Function has docstring")
            print(f"   Docstring: {dsql_assistant.__doc__.strip()[:100]}...")
        else:
            print("⚠️  Function missing docstring")
            
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import dsql_assistant: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_tool_discovery():
    """Test if AgentCore can discover the tool"""
    print("\n=== Testing Tool Discovery ===")
    
    try:
        # Try to discover tools the way AgentCore does
        import importlib.util
        import inspect
        
        tools_dir = os.path.join(agentcore_path, 'agent_config', 'tools')
        print(f"Looking for tools in: {tools_dir}")
        
        if not os.path.exists(tools_dir):
            print(f"❌ Tools directory doesn't exist: {tools_dir}")
            return False
            
        # List Python files in tools directory
        tool_files = [f for f in os.listdir(tools_dir) if f.endswith('.py') and f != '__init__.py']
        print(f"Found tool files: {tool_files}")
        
        # Check if dsql_mcp_assistant.py exists
        if 'dsql_mcp_assistant.py' in tool_files:
            print("✅ dsql_mcp_assistant.py found in tools directory")
        else:
            print("❌ dsql_mcp_assistant.py not found in tools directory")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Tool discovery failed: {e}")
        return False

def test_minimal_execution():
    """Test minimal execution without full MCP setup"""
    print("\n=== Testing Minimal Execution ===")
    
    try:
        # Import just the logging parts
        import logging
        logging.basicConfig(level=logging.INFO)
        
        print("✅ Logging setup successful")
        
        # Test SSM utils import
        from scripts.utils import get_ssm_parameter
        print("✅ SSM utils import successful")
        
        # Test parameter retrieval (this should work in AWS environment)
        try:
            cluster_id = get_ssm_parameter("/agentcore-db-mcp-assistant/DSQL_CLUSTER_ID")
            print(f"✅ Retrieved DSQL_CLUSTER_ID: {cluster_id}")
        except Exception as e:
            print(f"⚠️  SSM parameter retrieval failed: {e}")
            
        return True
        
    except Exception as e:
        print(f"❌ Minimal execution test failed: {e}")
        return False

if __name__ == "__main__":
    print("=== AgentCore Tool Registration Test ===\n")
    
    import_ok = test_tool_import()
    discovery_ok = test_tool_discovery()
    execution_ok = test_minimal_execution()
    
    print(f"\n=== Summary ===")
    print(f"Import Test: {'✅ PASS' if import_ok else '❌ FAIL'}")
    print(f"Discovery Test: {'✅ PASS' if discovery_ok else '❌ FAIL'}")
    print(f"Execution Test: {'✅ PASS' if execution_ok else '❌ FAIL'}")
    
    if all([import_ok, discovery_ok, execution_ok]):
        print("\n🎉 All tests passed! The tool should be working in AgentCore.")
    else:
        print("\n⚠️  Some tests failed. Check the issues above.")