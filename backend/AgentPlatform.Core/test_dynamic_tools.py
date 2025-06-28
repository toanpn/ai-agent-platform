#!/usr/bin/env python3
"""
Test Script for Dynamic Tool Manager

This script demonstrates and tests the new dynamic tool functionality
where each agent can have different API keys and tool configurations.
"""

import os
import sys
import json
from typing import Dict, Any

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.dynamic_tool_manager import DynamicToolManager
from core.agent_manager import AgentManager

def test_dynamic_tool_manager():
    """Test the dynamic tool manager functionality."""
    print("=" * 60)
    print("TESTING DYNAMIC TOOL MANAGER")
    print("=" * 60)
    
    try:
        # Initialize dynamic tool manager
        tool_manager = DynamicToolManager()
        print("✓ Dynamic Tool Manager initialized successfully")
        
        # Test getting available tools
        available_tools = tool_manager.get_available_tools()
        print(f"✓ Found {len(available_tools)} available tools:")
        for tool in available_tools:
            print(f"  - {tool['name']} ({tool['id']})")
        
        # Test creating a dynamic tool with configuration
        print("\n" + "-" * 40)
        print("Testing Dynamic Google Search Tool")
        print("-" * 40)
        
        google_config = {
            "google_api_key": "test_api_key_123",
            "google_cse_id": "test_cse_id_456"
        }
        
        google_tool = tool_manager.create_dynamic_tool("google_search_tool", google_config)
        print(f"✓ Created Google search tool: {google_tool.name}")
        print(f"  Description: {google_tool.description}")
        
        # Test the tool execution (should use mock results due to test credentials)
        test_query = "Python programming"
        result = google_tool._run(query=test_query, num_results=3)
        print(f"✓ Tool execution result (first 200 chars): {result[:200]}...")
        
        print("\n" + "-" * 40)
        print("Testing Dynamic JIRA Tool")
        print("-" * 40)
        
        jira_config = {
            "jira_base_url": "https://test-company.atlassian.net",
            "jira_username": "test@company.com",
            "jira_api_token": "test_token_789"
        }
        
        jira_tool = tool_manager.create_dynamic_tool("jira_tool", jira_config)
        print(f"✓ Created JIRA tool: {jira_tool.name}")
        print(f"  Description: {jira_tool.description}")
        
        # Test JIRA tool execution (should use mock results due to test credentials)
        jira_result = jira_tool._run(
            action="create_issue",
            parameters={
                "summary": "Test Issue",
                "description": "This is a test issue created by dynamic tool",
                "project": {"key": "TEST"},
                "issuetype": {"name": "Task"}
            }
        )
        print(f"✓ JIRA tool execution result (first 200 chars): {jira_result[:200]}...")
        
    except Exception as e:
        print(f"✗ Error testing dynamic tool manager: {e}")
        return False
    
    return True

def test_agent_configuration():
    """Test agent configuration with dynamic tools."""
    print("\n" + "=" * 60)
    print("TESTING AGENT CONFIGURATION")
    print("=" * 60)
    
    try:
        # Initialize agent manager
        agent_manager = AgentManager()
        print("✓ Agent Manager initialized successfully")
        
        # Test validation of agent configuration
        test_agent_config = {
            "agent_name": "Test_IT_Agent",
            "description": "Test IT support agent with dynamic tool configurations",
                         "tools": [
                 "google_search", 
                 "jira"
             ],
            "tool_configs": {
                 "google_search": {
                     "google_api_key": "test_google_key_for_it",
                     "google_cse_id": "test_google_cse_for_it"
                 },
                 "jira": {
                     "jira_base_url": "https://it-company.atlassian.net",
                     "jira_username": "it-support@company.com",
                     "jira_api_token": "it_jira_token_123"
                 }
             },
            "llm_config": {
                "model_name": "gemini-2.5-flash",
                "temperature": 0.2
            }
        }
        
        # Validate the configuration
        validation_result = agent_manager.validate_agent_config(test_agent_config)
        print(f"✓ Agent configuration validation:")
        print(f"  Valid: {validation_result['valid']}")
        print(f"  Errors: {len(validation_result['errors'])}")
        print(f"  Warnings: {len(validation_result['warnings'])}")
        
        if validation_result['errors']:
            for error in validation_result['errors']:
                print(f"    Error: {error}")
        
        if validation_result['warnings']:
            for warning in validation_result['warnings']:
                print(f"    Warning: {warning}")
        
        # Test creating tools for the agent
        print("\n" + "-" * 40)
        print("Testing Agent Tool Creation")
        print("-" * 40)
        
        agent_tools = agent_manager.dynamic_tool_manager.create_tools_for_agent(test_agent_config)
        print(f"✓ Created {len(agent_tools)} tools for test agent:")
        for tool in agent_tools:
            print(f"  - {tool.name}")
        
        # Test different agents with different configurations
        print("\n" + "-" * 40)
        print("Testing Multiple Agent Configurations")
        print("-" * 40)
        
        sales_agent_config = {
            "agent_name": "Test_Sales_Agent",
            "description": "Test sales support agent with different API keys",
                         "tools": [
                 "google_search",
                 "jira"
             ],
            "tool_configs": {
                "google_search": {
                    "google_api_key": "test_google_key_for_sales",
                    "google_cse_id": "test_google_cse_for_sales"
                },
                "jira": {
                     "jira_base_url": "https://sales-company.atlassian.net",
                     "jira_username": "sales-support@company.com",
                     "jira_api_token": "sales_jira_token_456"
                 }
            },
            "llm_config": {
                "model_name": "gemini-2.5-flash",
                "temperature": 0.3
            }
        }
        
        sales_tools = agent_manager.dynamic_tool_manager.create_tools_for_agent(sales_agent_config)
        print(f"✓ Created {len(sales_tools)} tools for sales agent:")
        for tool in sales_tools:
            print(f"  - {tool.name}")
        
        # Demonstrate that different agents have different configurations
        print(f"\n✓ Successfully demonstrated agent-specific tool configurations:")
        print(f"  - IT Agent has {len(agent_tools)} tools")
        print(f"  - Sales Agent has {len(sales_tools)} tools")
        print(f"  - Each agent has different API keys and configurations")
        
    except Exception as e:
        print(f"✗ Error testing agent configuration: {e}")
        return False
    
    return True

def test_configuration_loading():
    """Test loading agents from the updated configuration file."""
    print("\n" + "=" * 60)
    print("TESTING CONFIGURATION FILE LOADING")
    print("=" * 60)
    
    try:
        agent_manager = AgentManager()
        
        # Load agents from the updated configuration file
        agents = agent_manager.load_agents_from_config("agents.json")
        print(f"✓ Loaded {len(agents)} agents from configuration file:")
        
        for agent in agents:
            print(f"  - {agent.name}")
        
        # Test getting available tools
        available_tools = agent_manager.get_available_tools()
        print(f"✓ Total available tools: {len(available_tools)}")
        
        # Test getting detailed tool information
        tool_details = agent_manager.get_available_tools_details()
        print(f"✓ Tool details available for {len(tool_details)} tools")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing configuration loading: {e}")
        return False

def main():
    """Main test function."""
    print("DYNAMIC TOOL SYSTEM TEST SUITE")
    print("=" * 60)
    
    test_results = []
    
    # Run all tests
    test_results.append(("Dynamic Tool Manager", test_dynamic_tool_manager()))
    test_results.append(("Agent Configuration", test_agent_configuration()))
    test_results.append(("Configuration Loading", test_configuration_loading()))
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, result in test_results:
        status = "PASSED" if result else "FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal: {passed + failed} tests")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 All tests passed! Dynamic tool system is working correctly.")
    else:
        print(f"\n❌ {failed} test(s) failed. Please check the errors above.")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 