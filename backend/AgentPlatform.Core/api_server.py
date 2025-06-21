"""
Flask API Server for AgentPlatform.Core

This module creates a Flask API server that exposes the Dynamic Multi-Agent System
functionality as REST endpoints for integration with the AgentPlatform.API.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
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
        # Convert to absolute path to ensure file can be found regardless of working directory
        if not os.path.isabs(config_path):
            # Get the directory where this script is located
            script_dir = os.path.dirname(os.path.abspath(__file__))
            self.config_path = os.path.join(script_dir, config_path)
        else:
            self.config_path = config_path
            
        self.agent_manager = AgentManager()
        self.master_agent: Optional[MasterAgent] = None
        
    def initialize_system(self):
        """Initialize the agent system with initial configuration."""
        try:
            logger.info("🚀 Initializing Dynamic Multi-Agent System...")
            
            # Check if Google API key is available
            if not os.getenv('GOOGLE_API_KEY'):
                logger.warning("⚠️  GOOGLE_API_KEY not found in environment variables")
                logger.warning("⚠️  Please set your Google API key to enable full functionality")
                logger.warning("⚠️  Get your API key from: https://console.cloud.google.com/apis/credentials")
                logger.warning("⚠️  Set it with: export GOOGLE_API_KEY='your_api_key_here'")
                raise RuntimeError("GOOGLE_API_KEY not found in environment variables. Please set your Google API key to enable agent functionality.")
            
            logger.info("✅ Google API key found")
            
            # Load agents from configuration
            logger.info(f"📋 Loading agents from configuration: {self.config_path}")
            
            if not os.path.exists(self.config_path):
                raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
            
            sub_agents = self.agent_manager.load_agents_from_config(self.config_path)
            
            if not sub_agents:
                raise RuntimeError("No agents could be loaded from configuration")
            
            logger.info(f"✅ Loaded {len(sub_agents)} sub-agents successfully")
            
            # Create master agent
            logger.info("🤖 Creating Master Agent...")
            self.master_agent = create_master_agent(sub_agents)
            
            if self.master_agent is None:
                raise RuntimeError("Failed to create Master Agent - returned None")
            
            logger.info(f"✅ Master Agent created successfully")
            logger.info(f"✅ System initialized with {len(sub_agents)} agents")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize system: {e}")
            logger.error(f"❌ Error type: {type(e).__name__}")
            # Reset master_agent to None on failure
            self.master_agent = None
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
    system_status = {
        "system_manager_initialized": system_manager is not None,
        "master_agent_initialized": system_manager.master_agent is not None if system_manager else False,
        "total_agents": len(system_manager.master_agent.sub_agents) if system_manager and system_manager.master_agent else 0
    }
    
    return jsonify({
        "status": "healthy" if system_status["master_agent_initialized"] else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "AgentPlatform.Core",
        "system_status": system_status
    })


@app.route('/debug', methods=['GET'])
def debug_info():
    """Debug endpoint to help troubleshoot system initialization issues."""
    debug_info = {
        "timestamp": datetime.utcnow().isoformat(),
        "environment": {
            "google_api_key_present": bool(os.getenv('GOOGLE_API_KEY')),
            "config_file_exists": os.path.exists("agents.json"),
            "current_directory": os.getcwd()
        },
        "system_manager": {
            "initialized": system_manager is not None,
            "config_path": system_manager.config_path if system_manager else None,
            "master_agent_present": system_manager.master_agent is not None if system_manager else False
        }
    }
    
    if system_manager and system_manager.master_agent:
        debug_info["master_agent"] = {
            "sub_agents_count": len(system_manager.master_agent.sub_agents),
            "sub_agent_names": [agent.name for agent in system_manager.master_agent.sub_agents]
        }
    
    return jsonify(debug_info)


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
            error_msg = "The agent system is not ready. "
            if not os.getenv('GOOGLE_API_KEY'):
                error_msg += "Please set your GOOGLE_API_KEY environment variable. Get your API key from https://console.cloud.google.com/apis/credentials"
            else:
                error_msg += "Please check the server logs for initialization errors or try the /api/initialize endpoint."
            
            return jsonify({
                "success": False,
                "error": "Agent system not initialized",
                "response": error_msg
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


@app.route('/api/initialize', methods=['POST'])
def manual_initialize():
    """Manual initialization endpoint to retry system setup."""
    global system_manager
    
    try:
        logger.info("🔄 Manual initialization requested...")
        
        # Create or reset system manager
        system_manager = AgentSystemManager()
        
        # Try to initialize
        system_manager.initialize_system()
        
        return jsonify({
            "success": True,
            "message": "System initialized successfully",
            "system_status": {
                "system_manager_initialized": True,
                "master_agent_initialized": system_manager.master_agent is not None,
                "total_agents": len(system_manager.master_agent.sub_agents) if system_manager.master_agent else 0
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Manual initialization failed: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "system_status": {
                "system_manager_initialized": system_manager is not None,
                "master_agent_initialized": system_manager.master_agent is not None if system_manager else False,
                "total_agents": 0
            }
        }), 500


def initialize_system():
    """Initialize the agent system on startup."""
    global system_manager
    
    try:
        logger.info("🚀 Initializing Agent System Manager...")
        system_manager = AgentSystemManager()
        
        logger.info("🔧 Initializing agent system components...")
        system_manager.initialize_system()
        
        logger.info("✅ Agent system initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize agent system: {e}")
        
        # Ensure system_manager is still available for error handling in endpoints
        if system_manager is None:
            logger.info("🔄 Creating fallback system manager...")
            try:
                system_manager = AgentSystemManager()
                logger.info("✅ Fallback system manager created")
            except Exception as fallback_error:
                logger.error(f"❌ Failed to create fallback system manager: {fallback_error}")
                system_manager = None
        
        # Log the specific error for debugging
        logger.error(f"System will start but agents may not be available. Error details: {str(e)}")
        
        # Don't exit here - let the API server start but return errors for requests
        pass


if __name__ == '__main__':
    # Initialize the system
    initialize_system()
    
    # Start the Flask server
    port = int(os.getenv('PORT', 5002))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    logger.info(f"🚀 Starting Flask API server on port {port}")
    logger.info(f"📡 API endpoints available at: http://localhost:{port}")
    logger.info(f"   - Health check: GET /health")
    logger.info(f"   - Debug info: GET /debug")
    logger.info(f"   - Chat: POST /api/chat")
    logger.info(f"   - Agents info: GET /api/agents")
    logger.info(f"   - Reload: POST /api/reload")
    logger.info(f"   - Manual init: POST /api/initialize")
    
    app.run(host='0.0.0.0', port=port, debug=debug) 