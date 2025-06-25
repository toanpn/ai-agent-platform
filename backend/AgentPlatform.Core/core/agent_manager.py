"""
Agent Manager Module

This module is responsible for dynamically creating and managing agents based on 
the JSON configuration file. It loads tools and creates sub-agents that can be 
used by the master agent.
"""

import json
import importlib
import os
from typing import List, Dict, Any, Optional
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.tools import BaseTool, tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

# Import the new dynamic tool manager
from core.dynamic_tool_manager import DynamicToolManager

# Import all available tools for backward compatibility
from toolkit import jira_tool, rag_tool

class AgentManager:
    def __init__(self):
        """Initialize the Agent Manager with dynamic tool manager."""
        self.dynamic_tool_manager = DynamicToolManager()
        self.available_tools = self._build_tools_registry()  # Keep for backward compatibility
        self.sub_agents = []
    
    def _build_tools_registry(self) -> Dict[str, BaseTool]:
        """Build a registry of all available tools from the toolkit for backward compatibility."""
        tools_registry = {}
        
        # Register RAG tools
        tools_registry["knowledge_lookup"] = rag_tool.knowledge_lookup
        
        return tools_registry
    
    def create_sub_agent(self, config: Dict[str, Any]) -> BaseTool:
        """
        Creates a Sub-Agent from a configuration and wraps it as a BaseTool
        for the Master Agent to use.
        
        Args:
            config: Agent configuration dictionary from agents.json
            
        Returns:
            BaseTool: The sub-agent wrapped as a tool
        """
        agent_name = config["agent_name"]
        description = config["description"]
        tool_names = config["tools"]
        tool_configs = config.get("tool_configs", {})
        llm_config = config.get("llm_config", {})
        
        # Create dynamic tools for this agent using the new tool manager
        agent_tools = []
        
        # Use dynamic tool manager to create tools with agent-specific configurations
        try:
            dynamic_tools = self.dynamic_tool_manager.create_tools_for_agent(config)
            agent_tools.extend(dynamic_tools)
        except Exception as e:
            print(f"Warning: Failed to create dynamic tools for agent '{agent_name}': {e}")
        
        # Fallback to legacy tools if needed
        for tool_name in tool_names:
            if tool_name in self.available_tools:
                # Check if we already have this tool from dynamic creation
                existing_tool_names = [tool.name for tool in agent_tools]
                if tool_name not in existing_tool_names:
                    agent_tools.append(self.available_tools[tool_name])
                    print(f"✓ Added legacy tool: {tool_name}")
            elif tool_name not in [tool.name for tool in agent_tools]:
                print(f"Warning: Tool '{tool_name}' not found in registry or dynamic tools for agent '{agent_name}'")
        
        if not agent_tools:
            raise ValueError(f"No valid tools found for agent '{agent_name}'")
        
        print(f"Agent '{agent_name}' configured with {len(agent_tools)} tools: {[tool.name for tool in agent_tools]}")
        
        # Initialize the LLM for the sub-agent
        try:
            llm = ChatGoogleGenerativeAI(
                model=llm_config.get("model_name", "gemini-2.0-flash"),
                temperature=llm_config.get("temperature", 0.2)
            )
        except Exception as e:
            raise RuntimeError(f"Failed to initialize LLM for {agent_name}: {e}")
        
        # Create the prompt for the sub-agent
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"""You are a helpful assistant named {agent_name}. 

Your purpose is: {description}

You have access to specific tools to help users. Always use the appropriate tools to provide accurate and helpful responses. 
When using tools, make sure to extract the necessary parameters from the user's request.

Important guidelines:
- Always try to use your available tools to provide the best possible assistance
- If you need clarification on any parameters, ask the user for more details
- Provide clear, helpful, and professional responses
- If a task is outside your capabilities, explain what you can help with instead

CRITICAL LANGUAGE REQUIREMENT:
- You MUST respond to users in Vietnamese (tiếng Việt)
- All your responses should be in Vietnamese language
- This is a requirement for the user interface and user experience
- Even if the user asks in English, respond in Vietnamese

AVAILABLE TOOLS:
Your available tools are: {[tool.name for tool in agent_tools]}
Each tool has specific parameters and capabilities. Use them appropriately based on the user's request."""),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])
        
        # Create the agent executor
        try:
            agent = create_tool_calling_agent(llm, agent_tools, prompt)
            agent_executor = AgentExecutor(
                agent=agent, 
                tools=agent_tools, 
                verbose=True,
                handle_parsing_errors=True,
                max_iterations=3
            )
        except Exception as e:
            raise RuntimeError(f"Failed to create agent executor for {agent_name}: {e}")
        
        # Wrap the agent executor into a single tool for the Master Agent
        def create_agent_tool(executor, name, desc):
            @tool
            def agent_tool_func(input_query: str) -> str:
                """
                This is a specialized agent tool. The description is dynamically set based on the agent's capabilities.
                """
                try:
                    result = executor.invoke({"input": input_query})
                    return result.get("output", "No output generated")
                except Exception as e:
                    return f"Error processing request with {name}: {str(e)}"
            
            # Set the name and description
            agent_tool_func.name = name
            agent_tool_func.description = desc
            return agent_tool_func
        
        agent_as_tool = create_agent_tool(agent_executor, agent_name, description)
        
        return agent_as_tool
    
    def load_agents_from_config(self, config_path: str = "agents.json") -> List[BaseTool]:
        """
        Reads the JSON file and creates a list of sub-agents (wrapped as tools).
        
        Args:
            config_path: Path to the agents configuration file
            
        Returns:
            List[BaseTool]: List of sub-agents wrapped as tools
        """
        try:
            if not os.path.exists(config_path):
                raise FileNotFoundError(f"Configuration file not found: {config_path}")
            
            with open(config_path, 'r', encoding='utf-8') as f:
                configs = json.load(f)
            
            if not isinstance(configs, list):
                raise ValueError("Configuration file must contain a list of agent configurations")
            
            self.sub_agents = []
            for config in configs:
                try:
                    agent_tool = self.create_sub_agent(config)
                    self.sub_agents.append(agent_tool)
                    print(f"✓ Successfully loaded agent: {config['agent_name']}")
                except Exception as e:
                    print(f"✗ Failed to load agent '{config.get('agent_name', 'unknown')}': {e}")
            
            print(f"Loaded {len(self.sub_agents)} agents successfully")
            return self.sub_agents
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format in {config_path}: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to load agents from {config_path}: {e}")
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tool names from dynamic tool manager."""
        dynamic_tools = self.dynamic_tool_manager.get_available_tools()
        tool_names = [tool["name"] for tool in dynamic_tools]
        
        # Add legacy tools
        legacy_tools = list(self.available_tools.keys())
        tool_names.extend(legacy_tools)
        
        return tool_names
    
    def get_available_tools_details(self) -> List[Dict[str, Any]]:
        """Get detailed information about available tools from dynamic tool manager."""
        dynamic_tools = self.dynamic_tool_manager.get_available_tools()
        
        # Add legacy tools
        for tool_name, tool_obj in self.available_tools.items():
            dynamic_tools.append({
                "id": f"legacy_{tool_name}",
                "name": tool_name,
                "description": getattr(tool_obj, 'description', 'No description available'),
                "file": "legacy",
                "parameters": {}
            })
        
        return dynamic_tools
    
    def get_loaded_agents(self) -> List[str]:
        """Get list of loaded agent names."""
        return [agent.name for agent in self.sub_agents]
    
    def reload_agents(self, config_path: str = "agents.json") -> List[BaseTool]:
        """
        Reload agents from configuration file.
        
        Args:
            config_path: Path to the agents configuration file
            
        Returns:
            List[BaseTool]: List of reloaded sub-agents wrapped as tools
        """
        print("Reloading agents from configuration...")
        
        # Reload dynamic tool manager configuration
        self.dynamic_tool_manager = DynamicToolManager()
        
        # Load agents
        return self.load_agents_from_config(config_path)
    
    def validate_agent_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate agent configuration and return validation results.
        
        Args:
            config: Agent configuration to validate
            
        Returns:
            Dict containing validation results
        """
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "tool_validation": {}
        }
        
        # Check required fields
        required_fields = ["agent_name", "description", "tools"]
        for field in required_fields:
            if field not in config:
                validation_results["errors"].append(f"Missing required field: {field}")
                validation_results["valid"] = False
        
        # Validate tools
        if "tools" in config:
            available_tool_names = [tool["name"] for tool in self.dynamic_tool_manager.get_available_tools()]
            available_tool_names.extend(self.available_tools.keys())
            
            tool_configs = config.get("tool_configs", {})
            
            for tool_name in config["tools"]:
                tool_validation = {"valid": True, "errors": [], "warnings": []}
                
                # Check if tool exists
                if tool_name not in available_tool_names:
                    tool_validation["errors"].append(f"Tool '{tool_name}' not found in available tools")
                    tool_validation["valid"] = False
                else:
                    # Validate tool configuration
                    tool_config = None
                    for t in self.dynamic_tool_manager.tools_config:
                        if t.get("name") == tool_name:
                            tool_config = t
                            break
                    
                    if tool_config:
                        # Check required credential parameters
                        required_credentials = []
                        for param_name, param_config in tool_config.get("parameters", {}).items():
                            if param_config.get("is_credential", False) and param_config.get("required", False):
                                required_credentials.append(param_name)
                        
                        agent_tool_config = tool_configs.get(tool_name, {})
                        for cred in required_credentials:
                            if cred not in agent_tool_config:
                                tool_validation["warnings"].append(f"Missing credential parameter '{cred}' for tool '{tool_name}'")
                
                validation_results["tool_validation"][tool_name] = tool_validation
                if not tool_validation["valid"]:
                    validation_results["valid"] = False
        
        return validation_results 