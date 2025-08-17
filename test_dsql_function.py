#!/usr/bin/env python3
"""
Test the actual DSQL assistant function
"""

import sys
import os

# Add the agentcore path to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
agentcore_path = os.path.join(current_dir, 'agentcore-strands-db-mcp-assistant')
sys.path.insert(0, agentcore_path)

# Import the DSQL assistant function
from agent_config.tools.dsql_mcp_assistant import dsql_assistant

def test_dsql_assistant():
    """Test the DSQL assistant with a simple query"""
    print("=== Testing DSQL Assistant Function ===")
    
    # Test with a simple schema query
    test_query = "Show me the database schema"
    
    print(f"Testing query: '{test_query}'")
    print("Processing...")
    
    try:
        result = dsql_assistant(test_query)
        print(f"\n✓ Success! Response:")
        print("-" * 50)
        print(result)
        print("-" * 50)
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = test_dsql_assistant()
    if success:
        print("\n🎉 DSQL Assistant is working correctly!")
    else:
        print("\n❌ DSQL Assistant test failed.")