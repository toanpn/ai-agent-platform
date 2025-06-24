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

# Import all available tools
from toolkit import jira_tool, search_tool, utility_tools, rag_tool

class AgentManager:
    def __init__(self):
        """Initialize the Agent Manager with available tools registry."""
        self.available_tools = self._build_tools_registry()
        self.sub_agents = []
    
    def _build_tools_registry(self) -> Dict[str, BaseTool]:
        """Build a registry of all available tools from the toolkit."""
        tools_registry = {}
        
        # Register tools from jira_tool module
        tools_registry["jira_ticket_creator"] = jira_tool.jira_ticket_creator
        tools_registry["it_knowledge_base_search"] = jira_tool.it_knowledge_base_search
        
        # Register tools from search_tool module  
        tools_registry["internet_search"] = search_tool.internet_search
        tools_registry["policy_document_search"] = search_tool.policy_document_search
        tools_registry["leave_request_tool"] = search_tool.leave_request_tool
        
        # Register tools from utility_tools module
        tools_registry["google_search"] = utility_tools.google_search
        tools_registry["check_calendar"] = utility_tools.check_calendar
        tools_registry["check_weather"] = utility_tools.check_weather
        
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
        llm_config = config.get("llm_config", {})
        
        # Get the actual tool objects from the registry
        agent_tools = []
        for tool_name in tool_names:
            if tool_name in self.available_tools:
                agent_tools.append(self.available_tools[tool_name])
            else:
                print(f"Warning: Tool '{tool_name}' not found in registry for agent '{agent_name}'")
        
        if not agent_tools:
            raise ValueError(f"No valid tools found for agent '{agent_name}'")
        
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
- Even if the user asks in English, respond in Vietnamese"""),
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
        """Get list of available tool names."""
        return list(self.available_tools.keys())
    
    def get_available_tools_details(self) -> List[Dict[str, str]]:
        """Get detailed information about available tools."""
        tools_details = []
        for tool_name, tool_obj in self.available_tools.items():
            tools_details.append({
                "name": tool_name,
                "description": getattr(tool_obj, 'description', 'No description available')
            })
        return tools_details
    
    def get_loaded_agents(self) -> List[str]:
        """Get list of loaded agent names."""
        return [agent.name for agent in self.sub_agents]
    
    def reload_agents(self, config_path: str = "agents.json") -> List[BaseTool]:
        """Reload agents from configuration file."""
        print("Reloading agents from configuration...")
        return self.load_agents_from_config(config_path) 