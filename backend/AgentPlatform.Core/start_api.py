#!/usr/bin/env python3
"""
Startup script for the AgentPlatform.Core API Server

This script starts the Flask API server that exposes the agent system functionality.
"""

import os
import sys
from api_server import app, initialize_system

def main():
    """Main entry point for the API server."""
    print("🚀 Starting AgentPlatform.Core API Server...")
    
    # Initialize the system
    initialize_system()
    
    # Get configuration
    port = int(os.getenv('PORT', 8000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    print(f"📡 API Server starting on port {port}")
    print(f"🔗 Health check: http://localhost:{port}/health")
    print(f"💬 Chat endpoint: http://localhost:{port}/api/chat")
    print(f"🤖 Agent info: http://localhost:{port}/api/agents")
    print(f"🔄 Reload endpoint: http://localhost:{port}/api/reload")
    print("-" * 60)
    
    try:
        app.run(host='0.0.0.0', port=port, debug=debug)
    except KeyboardInterrupt:
        print("\n👋 API Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 