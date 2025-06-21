#!/usr/bin/env python3
"""
Test script for the AgentPlatform.Core API Server

This script tests the API endpoints to ensure they are working correctly.
"""

import requests
import json
import time

def test_api_server(base_url="http://localhost:5001"):
    """Test the API server endpoints."""
    
    print("🧪 Testing AgentPlatform.Core API Server")
    print(f"📡 Base URL: {base_url}")
    print("-" * 50)
    
    # Test 1: Health Check
    print("1. Testing Health Check...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ Health check passed")
            print(f"   📊 Response: {response.json()}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
    
    print()
    
    # Test 2: Agent Info
    print("2. Testing Agent Info...")
    try:
        response = requests.get(f"{base_url}/api/agents", timeout=5)
        if response.status_code == 200:
            print("   ✅ Agent info retrieved successfully")
            data = response.json()
            if data.get('success'):
                agent_count = data.get('data', {}).get('total_agents', 0)
                print(f"   🤖 Total agents: {agent_count}")
            else:
                print(f"   ⚠️  Agent info returned success=false: {data.get('error')}")
        else:
            print(f"   ❌ Agent info failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Agent info error: {e}")
    
    print()
    
    # Test 3: Chat Endpoint
    print("3. Testing Chat Endpoint...")
    try:
        test_message = {
            "message": "Hello, can you help me test this system?",
            "userId": "test_user",
            "sessionId": "test_session_123"
        }
        
        response = requests.post(
            f"{base_url}/api/chat", 
            json=test_message,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("   ✅ Chat endpoint working successfully")
                print(f"   🤖 Agent: {data.get('agentName')}")
                print(f"   💬 Response: {data.get('response')[:100]}...")
            else:
                print(f"   ⚠️  Chat returned success=false: {data.get('error')}")
                print(f"   💬 Fallback response: {data.get('response')}")
        else:
            print(f"   ❌ Chat endpoint failed: {response.status_code}")
            print(f"   📝 Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Chat endpoint error: {e}")
    
    print()
    print("🏁 API testing completed!")

def main():
    """Main function to run the tests."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test the AgentPlatform.Core API Server")
    parser.add_argument(
        "--url", 
        default="http://localhost:5001",
        help="Base URL of the API server (default: http://localhost:5001)"
    )
    
    args = parser.parse_args()
    
    print("⏳ Waiting 2 seconds for server to be ready...")
    time.sleep(2)
    
    test_api_server(args.url)

if __name__ == "__main__":
    main() 