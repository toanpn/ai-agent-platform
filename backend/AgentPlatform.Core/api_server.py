"""
Flask API Server for AgentPlatform.Core

This module creates a Flask API server that exposes the Dynamic Multi-Agent System
functionality as REST endpoints for integration with the AgentPlatform.API.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, List
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Import our custom modules
from core.agent_manager import AgentManager
from core.master_agent import MasterAgent, create_master_agent

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Global system manager instance
system_manager = None

class AgentSystemManager:
    """Manages the overall agent system including loading, reloading, and coordination."""
    
    def __init__(self, config_path: str = "agents.json"):
        self.config_path = config_path
        self.agent_manager = AgentManager()
        self.master_agent: MasterAgent = None
        
    def initialize_system(self):
        """Initialize the agent system with initial configuration."""
        try:
            logger.info("🚀 Initializing Dynamic Multi-Agent System...")
            
            # Check if Google API key is available
            if not os.getenv('GOOGLE_API_KEY'):
                raise RuntimeError("GOOGLE_API_KEY not found in environment variables")
            
            # Load agents from configuration
            sub_agents = self.agent_manager.load_agents_from_config(self.config_path)
            
            if not sub_agents:
                raise RuntimeError("No agents could be loaded from configuration")
            
            # Create master agent
            self.master_agent = create_master_agent(sub_agents)
            
            logger.info(f"✅ System initialized with {len(sub_agents)} agents")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize system: {e}")
            raise
    
    def process_user_request(self, user_input: str) -> str:
        """Process a user request through the master agent."""
        if not self.master_agent:
            return "❌ System not initialized properly"
        
        try:
            return self.master_agent.process_request(user_input)
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            return f"❌ Error processing request: {str(e)}"
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about the current agent configuration."""
        if not self.master_agent:
            return {"total_agents": 0, "agents": []}
        
        return self.master_agent.get_agent_info()


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "AgentPlatform.Core"
    })


@app.route('/api/chat', methods=['POST'])
def chat():
    """Main chat endpoint that processes user messages through the agent system."""
    try:
        # Parse request data
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                "success": False,
                "error": "Message is required",
                "response": "Please provide a message to process."
            }), 400
        
        message = data['message']
        user_id = data.get('userId', 'anonymous')
        session_id = data.get('sessionId')
        agent_name = data.get('agentName')
        
        logger.info(f"Processing message from user {user_id}: {message[:100]}...")
        
        # Process the message through the agent system
        if not system_manager or not system_manager.master_agent:
            return jsonify({
                "success": False,
                "error": "Agent system not initialized",
                "response": "The agent system is not ready. Please try again later."
            }), 500
        
        response = system_manager.process_user_request(message)
        
        # Return response in expected format
        return jsonify({
            "success": True,
            "response": response,
            "agentName": "MasterAgent",
            "sessionId": session_id,
            "metadata": {
                "timestamp": datetime.utcnow().isoformat(),
                "userId": user_id
            }
        })
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "response": "I apologize, but I'm having trouble processing your request right now. Please try again later."
        }), 500


@app.route('/api/agents', methods=['GET'])
def get_agents():
    """Get information about available agents."""
    try:
        if not system_manager:
            return jsonify({
                "success": False,
                "error": "System not initialized"
            }), 500
        
        agent_info = system_manager.get_agent_info()
        return jsonify({
            "success": True,
            "data": agent_info
        })
        
    except Exception as e:
        logger.error(f"Error getting agent info: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/reload', methods=['POST'])
def reload_agents():
    """Reload the agent configuration."""
    try:
        if not system_manager:
            return jsonify({
                "success": False,
                "error": "System not initialized"
            }), 500
        
        # Reinitialize the system
        system_manager.initialize_system()
        
        return jsonify({
            "success": True,
            "message": "Agents reloaded successfully"
        })
        
    except Exception as e:
        logger.error(f"Error reloading agents: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


def initialize_system():
    """Initialize the agent system on startup."""
    global system_manager
    
    try:
        system_manager = AgentSystemManager()
        system_manager.initialize_system()
        logger.info("✅ Agent system initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize agent system: {e}")
        # Don't exit here - let the API server start but return errors for requests
        pass


if __name__ == '__main__':
    # Initialize the system
    initialize_system()
    
    # Start the Flask server
    port = int(os.getenv('PORT', 5001))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    logger.info(f"🚀 Starting Flask API server on port {port}")
    logger.info(f"📡 API endpoints available at: http://localhost:{port}")
    logger.info(f"   - Health check: GET /health")
    logger.info(f"   - Chat: POST /api/chat")
    logger.info(f"   - Agents info: GET /api/agents")
    logger.info(f"   - Reload: POST /api/reload")
    
    app.run(host='0.0.0.0', port=port, debug=debug) 