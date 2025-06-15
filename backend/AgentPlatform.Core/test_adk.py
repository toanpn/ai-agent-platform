#!/usr/bin/env python3
"""
Simple test script to verify ADK integration is working.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_adk_imports():
    """Test that ADK can be imported successfully."""
    print("Testing ADK imports...")
    
    try:
        import google.adk
        print("✓ Google ADK imported successfully")
        print(f"  Version: {google.adk.__version__}")
        return True
    except ImportError as e:
        print(f"✗ Failed to import Google ADK: {e}")
        return False

def test_adk_components():
    """Test our ADK components."""
    print("\nTesting ADK components...")
    
    try:
        from agent_platform_core.agents.adk_agents import ADKAgentFactory, ADKAgentRuntime
        print("✓ ADK agent components imported successfully")
        
        # Test agent factory (with required API key)
        factory = ADKAgentFactory("test_api_key")
        print("✓ ADK agent factory created")
        
        # Test agent runtime (with required API key)
        runtime = ADKAgentRuntime("test_api_key")
        print("✓ ADK agent runtime created")
        
        return True
    except ImportError as e:
        print(f"✗ Failed to import ADK components: {e}")
        return False

def test_adk_tools():
    """Test ADK tools adapter."""
    print("\nTesting ADK tools adapter...")
    
    try:
        from agent_platform_core.tools.adk_tools import ADKToolsAdapter
        print("✓ ADK tools adapter imported successfully")
        
        # Test adapter creation
        adapter = ADKToolsAdapter()
        print("✓ ADK tools adapter created")
        
        return True
    except ImportError as e:
        print(f"✗ Failed to import ADK tools adapter: {e}")
        return False

def test_adk_config():
    """Test ADK configuration."""
    print("\nTesting ADK configuration...")
    
    try:
        from agent_platform_core.agents.adk_config import ADKConfig
        print("✓ ADK configuration imported successfully")
        
        # Test config creation
        config = ADKConfig()
        print("✓ ADK configuration created")
        print(f"  Runtime mode: {config.runtime_mode}")
        print(f"  Telemetry enabled: {config.telemetry_enabled}")
        
        return True
    except ImportError as e:
        print(f"✗ Failed to import ADK configuration: {e}")
        return False

def test_tool_registry():
    """Test tool registry."""
    print("\nTesting tool registry...")
    
    try:
        from agent_platform_core.tools.registry import get_tool_registry
        print("✓ Tool registry imported successfully")
        
        # Test registry
        registry = get_tool_registry()
        print("✓ Tool registry created")
        print(f"  Available tools: {len(registry.list_tool_names())}")
        
        return True
    except ImportError as e:
        print(f"✗ Failed to import tool registry: {e}")
        return False

def main():
    """Run all tests."""
    print("Agent Platform Core - ADK Integration Test")
    print("=" * 50)
    
    tests = [
        test_adk_imports,
        test_adk_components,
        test_adk_tools,
        test_adk_config,
        test_tool_registry
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All ADK integration tests passed!")
        return 0
    else:
        print("❌ Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 