"""
Flask API Server for AgentPlatform.Core

This module creates a Flask API server that exposes the Dynamic Multi-Agent System
functionality as REST endpoints for integration with the AgentPlatform.API.
"""

import os
import sys
import json
import logging
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import asyncio
from werkzeug.utils import secure_filename
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import atexit

# Import our custom modules
from core.agent_manager import AgentManager
from core.master_agent import MasterAgent, create_master_agent, summarize_conversation_async
from core.prompt_enhancer import enhance_prompt_async
from core.rag_service import RAGService

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Global system manager instance
system_manager = None

# Global RAG service instance
rag_service = None

# File upload configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc', 'xlsx', 'xls', 'txt', 'md'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class AgentConfigHandler(FileSystemEventHandler):
    """Handles file system events for the agents configuration file."""
    
    def __init__(self, system_manager: 'AgentSystemManager'):
        self.system_manager = system_manager
        self.last_modified = 0
        self.config_filename = os.path.basename(system_manager.config_path)
        self.config_path = system_manager.config_path
        logger.info(f"🔍 File watcher initialized for: {self.config_path}")
        logger.info(f"🔍 Watching for filename: {self.config_filename}")
        
    def _is_agents_config_file(self, file_path: str) -> bool:
        """Check if the file path represents our agents configuration file."""
        try:
            # Get the filename from the path
            filename = os.path.basename(file_path)
            
            # Check if it's the agents.json file (or our specific config file)
            if filename == self.config_filename:
                return True
            
            # Also check if the full path matches (for absolute path comparisons)
            if os.path.abspath(file_path) == os.path.abspath(self.config_path):
                return True
                
            # Handle temporary files created during atomic operations (common in Docker)
            if filename.startswith(self.config_filename) and ('.tmp' in filename or '.temp' in filename):
                return False  # Don't trigger on temp files
                
            return False
        except Exception as e:
            logger.debug(f"Error checking file path {file_path}: {e}")
            return False
        
    def on_modified(self, event):
        """Called when a file is modified."""
        if event.is_directory:
            return
            
        logger.debug(f"🔍 File modified: {event.src_path}")
        
        if self._is_agents_config_file(event.src_path):
            self._handle_config_change("modified", event.src_path)
    
    def on_created(self, event):
        """Called when a file is created."""
        if event.is_directory:
            return
            
        logger.debug(f"🔍 File created: {event.src_path}")
        
        # In Docker, files are often created new rather than modified
        if self._is_agents_config_file(event.src_path):
            self._handle_config_change("created", event.src_path)
    
    def on_moved(self, event):
        """Called when a file is moved (including atomic renames)."""
        if event.is_directory:
            return
            
        logger.debug(f"🔍 File moved: {event.src_path} -> {event.dest_path}")
        
        # Handle atomic file operations (temp file -> final file)
        if hasattr(event, 'dest_path') and self._is_agents_config_file(event.dest_path):
            self._handle_config_change("moved", event.dest_path)
    
    def _handle_config_change(self, event_type: str, file_path: str):
        """Handle configuration file changes with debouncing."""
        # Prevent multiple rapid reloads
        current_time = time.time()
        if current_time - self.last_modified < 2:  # 2 second cooldown
            logger.debug(f"🔍 Ignoring {event_type} event due to cooldown: {file_path}")
            return
        self.last_modified = current_time
        
        logger.info(f"📁 Configuration file {event_type}: {file_path}")
        logger.info("🔄 Reloading agents...")
        
        try:
            # Add a small delay to ensure file is fully written (especially important in Docker)
            time.sleep(0.5)
            
            # Verify file exists and is readable
            if not os.path.exists(self.config_path):
                logger.warning(f"⚠️  Config file not found after {event_type} event: {self.config_path}")
                return
            
            # Verify file is not empty and has valid content
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if not content:
                        logger.warning(f"⚠️  Config file is empty after {event_type} event, waiting for content...")
                        return
            except Exception as e:
                logger.warning(f"⚠️  Cannot read config file after {event_type} event: {e}")
                return
            
            self.system_manager.reload_agents()
            logger.info("✅ System reloaded successfully!")
        except Exception as e:
            logger.error(f"❌ Failed to reload system after {event_type} event: {e}")

def init_rag_service():
    """Initialize the RAG service."""
    global rag_service
    try:
        rag_service = RAGService()
        logger.info("✅ RAG service initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize RAG service: {e}")
        rag_service = None

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
        self.observer: Optional[Observer] = None
        
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
    
    def start_file_monitoring(self):
        """Start monitoring the configuration file for changes."""
        try:
            # Set up file monitoring
            self.observer = Observer()
            event_handler = AgentConfigHandler(self)
            
            # Monitor the directory containing the agents.json file
            config_dir = os.path.dirname(self.config_path)
            if not config_dir:
                config_dir = '.'
            
            # Convert to absolute path for consistency
            config_dir = os.path.abspath(config_dir)
            
            logger.info(f"👁️  Starting file monitoring...")
            logger.info(f"👁️  Config file path: {self.config_path}")
            logger.info(f"👁️  Monitoring directory: {config_dir}")
            logger.info(f"👁️  Config file exists: {os.path.exists(self.config_path)}")
            logger.info(f"👁️  Directory exists: {os.path.exists(config_dir)}")
            
            # Check if directory exists
            if not os.path.exists(config_dir):
                logger.error(f"❌ Monitoring directory does not exist: {config_dir}")
                return
            
            self.observer.schedule(event_handler, path=config_dir, recursive=False)
            self.observer.start()
            
            logger.info("👁️  File monitoring started - agents.json changes will trigger automatic reload")
            logger.info(f"👁️  Watching for file changes in: {config_dir}")
            
        except Exception as e:
            logger.warning(f"⚠️  Warning: Could not start file monitoring: {e}")
            logger.warning(f"⚠️  File monitoring will be disabled. Manual reload will be required.")
    
    def stop_monitoring(self):
        """Stop file monitoring."""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            logger.info("🛑 File monitoring stopped")
    
    def reload_agents(self):
        """Reload the entire agent system with new configuration."""
        try:
            # Reload agents
            new_sub_agents = self.agent_manager.reload_agents(self.config_path)
            
            if not new_sub_agents:
                logger.warning("⚠️  No agents loaded after reload - keeping existing configuration")
                return
            
            # Update master agent
            if self.master_agent:
                self.master_agent.update_sub_agents(new_sub_agents)
            else:
                self.master_agent = create_master_agent(new_sub_agents)
            
            logger.info(f"✅ System reloaded with {len(new_sub_agents)} agents")
            
        except Exception as e:
            logger.error(f"❌ Error during system reload: {e}")
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
    
    def process_user_request_with_details(self, user_input: str, history: List[Dict[str, Any]] = None, user_id: str = None) -> Dict[str, Any]:
        """Process a user request with conversation history and return detailed execution information."""
        if not self.agent_manager or not self.agent_manager.sub_agents_config:
            return {
                "response": "❌ System not initialized properly, no agent configurations loaded.",
                "error": "System not initialized"
            }

        try:
            # Filter agents based on user_id and is_public flag
            permitted_configs = []
            if user_id:
                for config in self.agent_manager.sub_agents_config:
                    is_public = config.get('is_public', False)
                    owner_id = config.get('created_by_id')
                    if is_public or (owner_id and owner_id == user_id):
                        permitted_configs.append(config)
            else: # For anonymous or system requests, only allow public agents
                permitted_configs = [config for config in self.agent_manager.sub_agents_config if config.get('is_public', False)]

            if not permitted_configs:
                return {
                    "response": "You do not have permission to use any agents, or no agents are available, if no have agent, please direct to agent management page to create new agent",
                    "error": "No permitted agents found for this user."
                }

            # Create agent tools from the permitted configurations
            permitted_agents = []
            for config in permitted_configs:
                try:
                    agent_tool = self.agent_manager.create_sub_agent(config)
                    permitted_agents.append(agent_tool)
                except Exception as e:
                    logger.error(f"Failed to create agent {config.get('agent_name')}: {e}")

            if not permitted_agents:
                 return {
                    "response": "Could not create any permitted agents.",
                    "error": "Agent creation failed."
                }

            # Create a temporary master agent for this request
            master_agent = create_master_agent(permitted_agents)
            
            # Process with conversation history if provided
            if history:
                result = master_agent.process_request_with_details_and_history(user_input, history)
            else:
                result = master_agent.process_request_with_details(user_input)
            
            # Add available agents list to the result
            result["available_agents"] = self.get_agent_info()
            
            # Add available tools list to the result (with detailed information)
            result["available_tools"] = self.agent_manager.get_available_tools_details()
            
            return result
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            return {
                "response": f"❌ Error processing request: {str(e)}",
                "agents_used": [],
                "tools_used": [],
                "execution_steps": [],
                "total_steps": 0,
                "available_agents": self.get_agent_info(),
                "available_tools": self.agent_manager.get_available_tools_details() if self.agent_manager else [],
                "error": str(e)
            }
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about the current agent configuration."""
        if not self.master_agent:
            return {"total_agents": 0, "agents": []}
        
        return self.master_agent.get_agent_info()
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information including agents and tools."""
        system_info = {
            "system_manager_initialized": True,
            "master_agent_initialized": self.master_agent is not None,
            "available_agents": self.get_agent_info(),
            "available_tools": self.agent_manager.get_available_tools_details() if self.agent_manager else []
        }
        
        return system_info


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
            "current_directory": os.getcwd(),
            "python_path": sys.path
        },
        "system_manager": {
            "initialized": system_manager is not None,
            "config_path": system_manager.config_path if system_manager else None,
            "master_agent_present": system_manager.master_agent is not None if system_manager else False
        }
    }
    
    if system_manager:
        # Add file monitoring information
        debug_info["file_monitoring"] = {
            "observer_active": system_manager.observer is not None and system_manager.observer.is_alive() if system_manager.observer else False,
            "config_path": system_manager.config_path,
            "config_path_absolute": os.path.abspath(system_manager.config_path),
            "config_file_exists": os.path.exists(system_manager.config_path),
            "config_dir": os.path.dirname(system_manager.config_path),
            "config_dir_exists": os.path.exists(os.path.dirname(system_manager.config_path)),
            "config_file_readable": True,
            "config_file_size": None,
            "config_file_modified": None
        }
        
        # Try to read config file info
        try:
            if os.path.exists(system_manager.config_path):
                stat_info = os.stat(system_manager.config_path)
                debug_info["file_monitoring"]["config_file_size"] = stat_info.st_size
                debug_info["file_monitoring"]["config_file_modified"] = datetime.fromtimestamp(stat_info.st_mtime).isoformat()
                
                # Test file readability
                with open(system_manager.config_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    debug_info["file_monitoring"]["config_file_content_length"] = len(content)
                    debug_info["file_monitoring"]["config_file_valid_json"] = True
                    try:
                        import json
                        json.loads(content)
                    except json.JSONDecodeError:
                        debug_info["file_monitoring"]["config_file_valid_json"] = False
        except Exception as e:
            debug_info["file_monitoring"]["config_file_readable"] = False
            debug_info["file_monitoring"]["read_error"] = str(e)
        
        if system_manager.master_agent:
            debug_info["master_agent"] = {
                "sub_agents_count": len(system_manager.master_agent.sub_agents),
                "sub_agent_names": [agent.name for agent in system_manager.master_agent.sub_agents]
            }
    
    return jsonify(debug_info)


@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Main chat endpoint that processes user messages through the agent system.
    
    Expected Request Format:
    {
        "message": "User's message",
        "userId": "user_id", 
        "sessionId": "session_id",
        "agentName": "agent_name",
        "history": [
            {
                "role": "user",
                "content": "Previous user message",
                "agentName": null,
                "timestamp": "2024-01-01T12:00:00.000Z"
            },
            {
                "role": "assistant", 
                "content": "Previous assistant response",
                "agentName": "AgentName",
                "timestamp": "2024-01-01T12:00:30.000Z"
            }
        ]
    }
    
    Enhanced Response Format:
    {
        "success": true,
        "response": "The actual response from the agent",
        "agentName": "MasterAgent",
        "sessionId": "session_id_if_provided",
        "agents_used": ["Agent1", "Agent2"],  // List of sub-agents that were used
        "tools_used": ["tool1", "tool2"],     // List of tools that were invoked
        "available_agents": {                 // All available agents in the system
            "total_agents": 3,
            "agents": [
                {"name": "Agent1", "description": "Description of Agent1"},
                {"name": "Agent2", "description": "Description of Agent2"}
            ]
        },
        "available_tools": [                  // All available tools in the system
            {"name": "tool1", "description": "Description of tool1"},
            {"name": "tool2", "description": "Description of tool2"}
        ],
        "execution_details": {               // Detailed execution information
            "execution_steps": [
                {
                    "tool_name": "Agent1",
                    "tool_input": "User query passed to agent",
                    "observation": "Response from the agent..."
                }
            ],
            "total_steps": 1
        },
        "metadata": {
            "timestamp": "2024-01-01T12:00:00.000Z",
            "userId": "user123",
            "error": null
        }
    }
    """
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
        history = data.get('history', [])
        
        logger.info(f"Processing message from user {user_id}: {message[:100]}...")
        logger.info(f"Session ID: {session_id}")
        logger.info(f"Conversation history length: {len(history)} messages")
        
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
                "response": error_msg,
                "agents_used": [],
                "tools_used": [],
                "available_agents": {"total_agents": 0, "agents": []},
                "available_tools": [],
                "execution_details": {
                    "execution_steps": [],
                    "total_steps": 0
                }
            }), 500
        
        # Use the detailed processing method with conversation history
        execution_result = system_manager.process_user_request_with_details(message, history, user_id=user_id)
        
        # Return enhanced response with detailed information
        return jsonify({
            "success": True,
            "response": execution_result.get("response", "No response generated"),
            "agentName": "MasterAgent",
            "sessionId": session_id,
            "agents_used": execution_result.get("agents_used", []),
            "tools_used": execution_result.get("tools_used", []),
            "available_agents": execution_result.get("available_agents", {"total_agents": 0, "agents": []}),
            "available_tools": execution_result.get("available_tools", []),
            "execution_details": {
                "execution_steps": execution_result.get("execution_steps", []),
                "total_steps": execution_result.get("total_steps", 0)
            },
            "metadata": {
                "timestamp": datetime.utcnow().isoformat(),
                "userId": user_id,
                "error": execution_result.get("error")
            }
        })
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "response": "I apologize, but I'm having trouble processing your request right now. Please try again later.",
            "agents_used": [],
            "tools_used": [],
            "available_tools": [],
            "execution_details": {
                "execution_steps": [],
                "total_steps": 0
            }
        }), 500


@app.route('/api/enhance-prompt', methods=['POST'])
def enhance_prompt():
    """
    Receives a raw user query, enhances it, and returns the structured result.
    """
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({"success": False, "error": "Query is required"}), 400

        raw_query = data['query']
        
        if not system_manager or not system_manager.master_agent:
            return jsonify({"success": False, "error": "System not initialized"}), 503

        # Get agent information needed for enhancement
        agent_info = system_manager.get_agent_info()

        # Run the async enhancement function
        enhanced_prompt = asyncio.run(enhance_prompt_async(raw_query, agent_info))
        
        return jsonify({"success": True, "enhanced_prompt": enhanced_prompt})

    except Exception as e:
        logger.error(f"Error in /api/enhance-prompt endpoint: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Internal Server Error",
            "response": str(e)
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


@app.route('/api/tools', methods=['GET'])
def get_tools():
    """Get information about available tools."""
    try:
        if not system_manager:
            return jsonify({
                "success": False,
                "error": "System not initialized"
            }), 500
        
        tools_info = system_manager.agent_manager.get_available_tools_details() if system_manager.agent_manager else []
        return jsonify({
            "success": True,
            "data": tools_info,
            "total_tools": len(tools_info)
        })
        
    except Exception as e:
        logger.error(f"Error getting tools info: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/reload', methods=['POST'])
def reload_agents_endpoint():
    """Reload the agent configuration."""
    try:
        if not system_manager:
            return jsonify({
                "success": False,
                "error": "System not initialized"
            }), 500
        
        # Use the new reload_agents method
        system_manager.reload_agents()
        
        # Get updated agent info
        agent_info = system_manager.get_agent_info()
        
        return jsonify({
            "success": True,
            "message": f"Successfully reloaded {agent_info['total_agents']} agents",
            "agents": agent_info['agents']
        })
        
    except Exception as e:
        logger.error(f"Error reloading agents: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/agents/sync', methods=['POST'])
def sync_agents():
    """Sync agent configurations from the API service."""
    try:
        if not system_manager:
            return jsonify({
                "success": False,
                "error": "System not initialized"
            }), 500
        
        data = request.get_json()
        
        if not data or 'agents' not in data:
            return jsonify({
                "success": False,
                "error": "Agents data is required"
            }), 400
        
        agents_data = data['agents']
        
        # Validate agents data structure
        if not isinstance(agents_data, list):
            return jsonify({
                "success": False,
                "error": "Agents data must be an array"
            }), 400
        
        # Validate each agent in the array
        for agent in agents_data:
            if not isinstance(agent, dict):
                return jsonify({
                    "success": False,
                    "error": "Each agent must be an object"
                }), 400
            
            if 'agent_name' not in agent:
                return jsonify({
                    "success": False,
                    "error": "Each agent must have an 'agent_name' field"
                }), 400
        
        # Write agents data to agents.json file
        try:
            # Ensure the directory exists
            config_dir = os.path.dirname(system_manager.config_path)
            if not os.path.exists(config_dir):
                os.makedirs(config_dir, exist_ok=True)
            
            # Write to a temporary file first, then rename (atomic operation)
            temp_path = system_manager.config_path + '.tmp'
            
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(agents_data, f, indent=2, ensure_ascii=False)
            
            # Atomic rename
            if os.path.exists(system_manager.config_path):
                os.remove(system_manager.config_path)
            os.rename(temp_path, system_manager.config_path)
            
            logger.info(f"✅ Successfully updated agents.json with {len(agents_data)} agents")
            
            # Reload the agents to reflect the changes
            system_manager.reload_agents()
            
            # Get updated agent info
            agent_info = system_manager.get_agent_info()
            
            return jsonify({
                "success": True,
                "message": f"Successfully synced {len(agents_data)} agents",
                "agents_synced": len(agents_data),
                "agents_loaded": agent_info['total_agents'],
                "agents": agent_info['agents']
            })
            
        except Exception as e:
            logger.error(f"Error writing agents.json: {e}")
            return jsonify({
                "success": False,
                "error": f"Failed to write agents configuration: {str(e)}"
            }), 500
        
    except Exception as e:
        logger.error(f"Error syncing agents: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/test-file-monitoring', methods=['POST'])
def test_file_monitoring():
    """Test endpoint to manually trigger file monitoring and check system status."""
    try:
        if not system_manager:
            return jsonify({
                "success": False,
                "error": "System not initialized"
            }), 500
        
        # Check current file monitoring status
        monitoring_status = {
            "observer_exists": system_manager.observer is not None,
            "observer_alive": system_manager.observer.is_alive() if system_manager.observer else False,
            "config_path": system_manager.config_path,
            "config_exists": os.path.exists(system_manager.config_path),
        }
        
        # Try to read current file content
        current_content = None
        try:
            with open(system_manager.config_path, 'r', encoding='utf-8') as f:
                current_content = f.read()
                monitoring_status["file_readable"] = True
                monitoring_status["file_size"] = len(current_content)
        except Exception as e:
            monitoring_status["file_readable"] = False
            monitoring_status["read_error"] = str(e)
        
        # Try manual reload
        reload_success = False
        reload_error = None
        try:
            system_manager.reload_agents()
            reload_success = True
        except Exception as e:
            reload_error = str(e)
        
        return jsonify({
            "success": True,
            "monitoring_status": monitoring_status,
            "manual_reload": {
                "success": reload_success,
                "error": reload_error
            },
            "message": "File monitoring test completed"
        })
        
    except Exception as e:
        logger.error(f"Error testing file monitoring: {e}")
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
        
        # Start file monitoring
        system_manager.start_file_monitoring()
        
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
        
        logger.info("👁️  Starting file monitoring...")
        system_manager.start_file_monitoring()
        
        logger.info("🧠 Initializing RAG service...")
        init_rag_service()
        
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


@app.get("/system/graph-visualization")
async def get_graph_visualization():
    """Get graph visualization data including structure and execution flow."""
    try:
        # Get system information
        system_info = system_manager.get_system_info()
        
        # Get graph structure if master agent exists
        graph_structure = None
        mermaid_diagram = None
        
        if system_manager.master_agent:
            try:
                # Get LangChain graph structure
                graph = system_manager.master_agent.agent_executor
                
                # Get the graph representation
                if hasattr(graph, 'get_graph'):
                    graph_obj = graph.get_graph()
                    
                    # Get nodes and edges
                    nodes = []
                    edges = []
                    
                    # Extract nodes
                    for node_id, node_data in graph_obj.nodes.items():
                        nodes.append({
                            "id": node_id,
                            "label": node_data.get("name", node_id),
                            "type": node_data.get("type", "node"),
                            "description": getattr(node_data.get("data", {}), "description", ""),
                        })
                    
                    # Extract edges
                    for edge in graph_obj.edges:
                        edges.append({
                            "from": edge.source,
                            "to": edge.target,
                            "label": getattr(edge, "data", {}).get("label", "")
                        })
                    
                    graph_structure = {
                        "nodes": nodes,
                        "edges": edges
                    }
                    
                    # Get Mermaid diagram if available
                    if hasattr(graph_obj, 'draw_mermaid'):
                        mermaid_diagram = graph_obj.draw_mermaid()
                        
            except Exception as e:
                logger.warning(f"Could not extract graph structure: {e}")
        
        # Create agent flow visualization data
        agent_nodes = []
        agent_edges = []
        
        if system_info.get("available_agents"):
            agents = system_info["available_agents"]["agents"]
            
            # Add master agent node
            agent_nodes.append({
                "id": "master_agent",
                "label": "Master Agent",
                "type": "master",
                "description": "Routes requests to appropriate sub-agents",
                "color": "#4CAF50"
            })
            
            # Add sub-agent nodes
            for i, agent in enumerate(agents):
                agent_nodes.append({
                    "id": f"agent_{i}",
                    "label": agent["name"],
                    "type": "sub_agent",
                    "description": agent["description"],
                    "color": "#2196F3"
                })
                
                # Add edge from master to sub-agent
                agent_edges.append({
                    "from": "master_agent",
                    "to": f"agent_{i}",
                    "label": "routes to"
                })
        
        # Add tools visualization
        tools_data = []
        if system_info.get("available_tools"):
            for tool in system_info["available_tools"]:
                tools_data.append({
                    "name": tool["name"],
                    "description": tool["description"],
                    "type": "tool"
                })
                
                # Add tool nodes to agent flow
                tool_id = f"tool_{tool['name']}"
                agent_nodes.append({
                    "id": tool_id,
                    "label": tool["name"],
                    "type": "tool",
                    "description": tool["description"],
                    "color": "#FF9800"
                })
        
        return {
            "success": True,
            "data": {
                "langchain_graph": {
                    "structure": graph_structure,
                    "mermaid": mermaid_diagram
                },
                "agent_flow": {
                    "nodes": agent_nodes,
                    "edges": agent_edges
                },
                "tools": tools_data,
                "system_info": system_info
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting graph visualization data: {e}")
        return {
            "success": False,
            "error": str(e),
            "data": None
        }

@app.get("/system/execution-trace/{session_id}")
async def get_execution_trace(session_id: str):
    """Get execution trace for visualization of a specific conversation."""
    try:
        # This would integrate with your conversation history
        # For now, return mock execution trace data
        return {
            "success": True,
            "data": {
                "session_id": session_id,
                "execution_steps": [
                    {
                        "step": 1,
                        "node": "master_agent",
                        "type": "decision",
                        "input": "User query received",
                        "output": "Routing to HR_Agent",
                        "timestamp": "2024-01-01T10:00:00Z"
                    },
                    {
                        "step": 2,
                        "node": "HR_Agent",
                        "type": "agent",
                        "input": "HR query about leave policy",
                        "output": "Calling policy_document_search tool",
                        "timestamp": "2024-01-01T10:00:01Z"
                    },
                    {
                        "step": 3,
                        "node": "policy_document_search",
                        "type": "tool",
                        "input": "leave policy search",
                        "output": "Found relevant policy documents",
                        "timestamp": "2024-01-01T10:00:02Z"
                    }
                ]
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting execution trace: {e}")
        return {
            "success": False,
            "error": str(e)
        }

# ==================== RAG ENDPOINTS ====================

@app.route('/api/rag/upload', methods=['POST'])
def upload_document():
    """Upload and process a document for RAG."""
    try:
        # Check if RAG service is available
        if not rag_service:
            return jsonify({
                'success': False,
                'error': 'RAG service not initialized'
            }), 500
        
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
        
        file = request.files['file']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        # Check file size
        if len(file.read()) > MAX_FILE_SIZE:
            return jsonify({
                'success': False,
                'error': f'File too large. Maximum size is {MAX_FILE_SIZE / 1024 / 1024}MB'
            }), 413
        
        # Reset file pointer
        file.seek(0)
        
        # Check if file type is allowed
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': f'File type not supported. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        # Get additional parameters
        agent_id = request.form.get('agent_id')
        metadata = {}
        
        # Parse metadata if provided
        if 'metadata' in request.form:
            try:
                metadata = json.loads(request.form['metadata'])
            except json.JSONDecodeError:
                return jsonify({
                    'success': False,
                    'error': 'Invalid metadata JSON format'
                }), 400
        
        # Save file temporarily
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
        
        file.save(filepath)
        
        try:
            # Process document with RAG service
            result = rag_service.add_document(filepath, agent_id, metadata)
            
            # Clean up temporary file
            os.remove(filepath)
            
            return jsonify({
                'success': True,
                'result': result
            })
            
        except Exception as e:
            # Clean up temporary file on error
            if os.path.exists(filepath):
                os.remove(filepath)
            raise e
            
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/rag/web-content', methods=['POST'])
def add_web_content():
    """Add web content to the knowledge base."""
    try:
        # Check if RAG service is available
        if not rag_service:
            return jsonify({
                'success': False,
                'error': 'RAG service not initialized'
            }), 500
        
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({
                'success': False,
                'error': 'URL is required'
            }), 400
        
        url = data['url']
        agent_id = data.get('agent_id')
        metadata = data.get('metadata', {})
        
        # Process web content
        result = rag_service.add_web_content(url, agent_id, metadata)
        
        return jsonify({
            'success': True,
            'result': result
        })
        
    except Exception as e:
        logger.error(f"Error adding web content: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/rag/search', methods=['POST'])
def search_knowledge():
    """Search the knowledge base."""
    try:
        # Check if RAG service is available
        if not rag_service:
            return jsonify({
                'success': False,
                'error': 'RAG service not initialized'
            }), 500
        
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                'success': False,
                'error': 'Query is required'
            }), 400
        
        query = data['query']
        agent_id = data.get('agent_id')
        max_results = data.get('max_results', 5)
        
        # Search knowledge base
        results = rag_service.search_knowledge(query, agent_id, max_results)
        
        return jsonify({
            'success': True,
            'results': results,
            'query': query,
            'total_results': len(results)
        })
        
    except Exception as e:
        logger.error(f"Error searching knowledge base: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/rag/stats', methods=['GET'])
def get_knowledge_stats():
    """Get knowledge base statistics."""
    try:
        # Check if RAG service is available
        if not rag_service:
            return jsonify({
                'success': False,
                'error': 'RAG service not initialized'
            }), 500
        
        stats = rag_service.get_collection_stats()
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"Error getting knowledge stats: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/rag/agent/<agent_id>/documents', methods=['DELETE'])
def delete_agent_documents(agent_id: str):
    """Delete all documents for a specific agent."""
    try:
        # Check if RAG service is available
        if not rag_service:
            return jsonify({
                'success': False,
                'error': 'RAG service not initialized'
            }), 500
        
        result = rag_service.delete_agent_documents(agent_id)
        
        return jsonify({
            'success': True,
            'result': result
        })
        
    except Exception as e:
        logger.error(f"Error deleting agent documents: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/rag/supported-formats', methods=['GET'])
def get_supported_formats():
    """Get list of supported file formats."""
    return jsonify({
        'success': True,
        'supported_formats': list(ALLOWED_EXTENSIONS),
        'max_file_size_mb': MAX_FILE_SIZE / 1024 / 1024,
        'additional_sources': ['web_urls']
    })


@app.route('/v1/chat/summarize', methods=['POST'])
async def summarize_chat():
    """
    Summarizes a chat conversation.
    """
    try:
        data = request.get_json()
        if not data or 'messages' not in data:
            return jsonify({"success": False, "error": "Messages are required"}), 400

        messages = data['messages']
        
        # Ensure system is initialized for logging/consistency, even if not directly used
        if not system_manager:
            return jsonify({"success": False, "error": "System not initialized"}), 503

        summary = await summarize_conversation_async(messages)
        
        return jsonify({"summary": summary})

    except Exception as e:
        logger.error(f"Error in /v1/chat/summarize endpoint: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Internal Server Error",
            "summary": None
        }), 500


def cleanup_system():
    """Cleanup function called on application shutdown."""
    global system_manager
    if system_manager:
        logger.info("🧹 Cleaning up system...")
        system_manager.stop_monitoring()
        logger.info("✅ System cleanup completed")


# Register cleanup function
atexit.register(cleanup_system)


if __name__ == '__main__':
    # This will only run if the script is executed directly
    # In production, the Flask app is typically run via WSGI server
    initialize_system()
    app.run(debug=True, host='0.0.0.0', port=8000) 