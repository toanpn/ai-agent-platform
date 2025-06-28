"""
Dynamic Tool Manager Module

This module is responsible for dynamically creating and managing tools with 
agent-specific configurations. It loads tools from the tools.json configuration
and creates tool instances with the appropriate API keys and parameters for each agent.
"""

import json
import os
import importlib
from typing import List, Dict, Any, Optional, Type
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

class DynamicToolManager:
    def __init__(self, tools_config_path: str = "toolkit/tools.json"):
        """Initialize the Dynamic Tool Manager."""
        # Convert to absolute path to ensure file can be found regardless of working directory
        if not os.path.isabs(tools_config_path):
            # Get the directory where this script is located
            script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.tools_config_path = os.path.join(script_dir, tools_config_path)
        else:
            self.tools_config_path = tools_config_path
        self.tools_config = self._load_tools_config()
        
    def _load_tools_config(self) -> List[Dict[str, Any]]:
        """Load tools configuration from JSON file."""
        try:
            if not os.path.exists(self.tools_config_path):
                raise FileNotFoundError(f"Tools configuration file not found: {self.tools_config_path}")
            
            with open(self.tools_config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            if not isinstance(config, list):
                raise ValueError("Tools configuration file must contain a list of tool configurations")
            
            return config
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format in {self.tools_config_path}: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to load tools configuration from {self.tools_config_path}: {e}")
    
    def get_tool_config(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific tool by ID."""
        for tool_config in self.tools_config:
            if tool_config.get("id") == tool_id:
                return tool_config
        return None
    
    def create_dynamic_tool(self, tool_id: str, agent_tool_config: Dict[str, Any]) -> BaseTool:
        """
        Create a dynamic tool instance with agent-specific configuration.
        
        Args:
            tool_id: The ID of the tool to create
            agent_tool_config: Agent-specific configuration for the tool
            
        Returns:
            BaseTool: Configured tool instance
        """
        tool_config = self.get_tool_config(tool_id)
        if not tool_config:
            raise ValueError(f"Tool configuration not found for tool ID: {tool_id}")
        
        # Use tool_id instead of Vietnamese name for Gemini compatibility
        tool_name = tool_id  # Changed from tool_config["name"] to tool_id
        tool_display_name = tool_config["name"]  # Keep display name for reference
        tool_file = tool_config["file"]
        tool_description = tool_config["description"]
        tool_parameters = tool_config.get("parameters", {})
        
        # Create dynamic tool class based on the tool configuration
        return self._create_tool_instance(
            tool_name=tool_name,
            tool_display_name=tool_display_name,
            tool_file=tool_file,
            tool_description=tool_description,
            tool_parameters=tool_parameters,
            agent_config=agent_tool_config
        )
    
    def _create_tool_instance(self, tool_name: str, tool_display_name: str, tool_file: str, tool_description: str, 
                             tool_parameters: Dict[str, Any], agent_config: Dict[str, Any]) -> BaseTool:
        """Create a tool instance with dynamic configuration."""
        
        # Create dynamic input schema
        schema_fields = {}
        for param_name, param_config in tool_parameters.items():
            if not param_config.get("is_credential", False):  # Only include non-credential parameters in schema
                param_type = param_config.get("type", "string")
                param_description = param_config.get("description", "")
                is_required = param_config.get("required", False)
                default_value = param_config.get("default")
                
                if param_type == "string":
                    if is_required and default_value is None:
                        schema_fields[param_name] = (str, Field(description=param_description))
                    else:
                        schema_fields[param_name] = (str, Field(default=default_value, description=param_description))
                elif param_type == "integer":
                    if is_required and default_value is None:
                        schema_fields[param_name] = (int, Field(description=param_description))
                    else:
                        schema_fields[param_name] = (int, Field(default=default_value, description=param_description))
                elif param_type == "object":
                    if is_required and default_value is None:
                        schema_fields[param_name] = (dict, Field(description=param_description))
                    else:
                        schema_fields[param_name] = (dict, Field(default=default_value or {}, description=param_description))
                else:
                    # Default to string type for unknown types
                    if is_required and default_value is None:
                        schema_fields[param_name] = (str, Field(description=param_description))
                    else:
                        schema_fields[param_name] = (str, Field(default=default_value, description=param_description))
        
        # Create dynamic input model using create_model
        from pydantic import create_model
        DynamicInputModel = create_model(f"{tool_name}Input", **schema_fields)
        
        # Create the dynamic tool class
        class DynamicTool(BaseTool):
            name: str = tool_name
            description: str = tool_description
            args_schema: Type[BaseModel] = DynamicInputModel
            
            def __init__(self, agent_config: Dict[str, Any], tool_file: str, tool_parameters: Dict[str, Any], tool_display_name: str = None, **kwargs):
                super().__init__(**kwargs)
                # Store configuration in a way that doesn't conflict with Pydantic
                object.__setattr__(self, '_agent_config', agent_config)
                object.__setattr__(self, '_tool_file', tool_file)
                object.__setattr__(self, '_tool_parameters', tool_parameters)
                object.__setattr__(self, '_tool_display_name', tool_display_name or self.name)
                
            def _run(self, **kwargs) -> str:
                """Execute the tool with dynamic configuration."""
                try:
                    # Merge agent configuration with runtime parameters
                    merged_params = {**self._agent_config, **kwargs}
                    
                    # Import and execute the appropriate tool function
                    return self._execute_tool_function(merged_params)
                    
                except Exception as e:
                    return f"❌ Error executing {self.name}: {str(e)}"
            
            def _execute_tool_function(self, params: Dict[str, Any]) -> str:
                """Execute the specific tool function based on tool file and parameters."""
                try:
                    # Import the tool module
                    module_name = f"toolkit.{self._tool_file.replace('.py', '')}"
                    tool_module = importlib.import_module(module_name)
                    
                    # Map tool IDs to execution methods (using English IDs for Gemini compatibility)
                    if self.name == "google_search_tool":
                        return self._execute_google_search(tool_module, params)
                    elif self.name == "gmail_tool":
                        return self._execute_gmail_tool(tool_module, params)
                    elif self.name == "jira_tool":
                        return self._execute_jira_tool(tool_module, params)
                    elif self.name == "knowledge_search_tool":
                        return self._execute_knowledge_search_tool(tool_module, params)
                    else:
                        # For tools that don't need credentials, use original implementation
                        return self._execute_generic_tool(tool_module, params)
                        
                except Exception as e:
                    raise RuntimeError(f"Failed to execute tool {self.name}: {e}")
            
            def _execute_google_search(self, tool_module, params: Dict[str, Any]) -> str:
                """Execute Google search with dynamic API key."""
                from toolkit.google_search_tool import GoogleSearchTool
                
                # Create tool instance with dynamic configuration
                class ConfiguredGoogleSearchTool(GoogleSearchTool):
                    def _run(self, query: str, num_results: Optional[int] = 5) -> str:
                        api_key = params.get("google_api_key")
                        cse_id = params.get("google_cse_id")
                        
                        if not api_key or not cse_id:
                            return self._mock_search_results(query, num_results)
                        
                        # Temporarily set environment variables for this execution
                        old_api_key = os.environ.get("GOOGLE_API_KEY")
                        old_cse_id = os.environ.get("GOOGLE_CSE_ID")
                        
                        try:
                            os.environ["GOOGLE_API_KEY"] = api_key
                            os.environ["GOOGLE_CSE_ID"] = cse_id
                            return super()._run(query, num_results)
                        finally:
                            # Restore original environment variables
                            if old_api_key is not None:
                                os.environ["GOOGLE_API_KEY"] = old_api_key
                            elif "GOOGLE_API_KEY" in os.environ:
                                del os.environ["GOOGLE_API_KEY"]
                                
                            if old_cse_id is not None:
                                os.environ["GOOGLE_CSE_ID"] = old_cse_id
                            elif "GOOGLE_CSE_ID" in os.environ:
                                del os.environ["GOOGLE_CSE_ID"]
                
                # Try to find query from various possible parameter names
                query = None
                possible_query_keys = ["query", "q", "search_query", "search_term", "text", "input"]
                
                for key in possible_query_keys:
                    if key in params and params[key]:
                        query = params[key]
                        break
                
                # If no query found in standard keys, look for any string value that might be the query
                if not query:
                    for key, value in params.items():
                        if isinstance(value, str) and value.strip() and not key.endswith("_key") and not key.endswith("_id") and not key.endswith("_token"):
                            query = value
                            break
                
                # Final validation
                if not query or not isinstance(query, str) or not query.strip():
                    return f"❌ Lỗi: Không tìm thấy query để tìm kiếm. Params nhận được: {params}"
                
                num_results = params.get("num_results", 5)
                if not isinstance(num_results, int) or num_results < 1:
                    num_results = 5
                
                print(f"Debug: Using query: '{query.strip()}' with {num_results} results")
                
                tool_instance = ConfiguredGoogleSearchTool()
                return tool_instance._run(query.strip(), num_results)
            
            def _execute_gmail_tool(self, tool_module, params: Dict[str, Any]) -> str:
                """Execute unified Gmail tool with dynamic configuration."""
                credentials_path = params.get("gmail_credentials_path")
                
                if not credentials_path:
                    return "❌ Gmail credentials path not provided"
                
                try:
                    from toolkit.gmail_tool import GmailTool
                    
                    # Create Gmail tool instance with credentials
                    tool_instance = GmailTool(gmail_credentials_path=credentials_path)
                    
                    # Execute the Gmail tool with action and parameters
                    action = params.get("action", "")
                    action_params = params.get("parameters", {})
                    
                    return tool_instance._run(action, action_params)
                    
                except Exception as e:
                    return f"❌ Error executing Gmail tool: {str(e)}"
            
            def _execute_jira_tool(self, tool_module, params: Dict[str, Any]) -> str:
                """Execute unified JIRA tool with dynamic configuration."""
                jira_url = params.get("jira_base_url")
                jira_username = params.get("jira_username")
                jira_token = params.get("jira_api_token")
                
                if not all([jira_url, jira_username, jira_token]):
                    return "❌ JIRA configuration not complete (missing URL, username, or token)"
                
                try:
                    from toolkit.jira_tool import JiraTool
                    
                    # Create JIRA tool instance with credentials
                    tool_instance = JiraTool(
                        jira_base_url=jira_url,
                        jira_username=jira_username,
                        jira_api_token=jira_token
                    )
                    
                    # Execute the JIRA tool with action and parameters
                    action = params.get("action", "")
                    action_params = params.get("parameters", {})
                    
                    return tool_instance._run(action, action_params)
                    
                except Exception as e:
                    return f"❌ Error executing JIRA tool: {str(e)}"
            
            def _execute_knowledge_search_tool(self, tool_module, params: Dict[str, Any]) -> str:
                """Execute knowledge search tool (RAG) with dynamic configuration."""
                try:
                    from toolkit.rag_tool import RAGTool
                    
                    # Try to find query from various possible parameter names
                    query = None
                    possible_query_keys = ["query", "q", "search_query", "search_term", "text", "input"]
                    
                    for key in possible_query_keys:
                        if key in params and params[key]:
                            query = params[key]
                            break
                    
                    # If no query found in standard keys, look for any string value that might be the query
                    if not query:
                        for key, value in params.items():
                            if isinstance(value, str) and value.strip() and not key.endswith("_key") and not key.endswith("_id") and not key.endswith("_token"):
                                query = value
                                break
                    
                    # Final validation
                    if not query or not isinstance(query, str) or not query.strip():
                        return f"❌ Lỗi: Không tìm thấy query để tìm kiếm. Params nhận được: {params}"
                    
                    max_results = params.get("max_results", 5)
                    if not isinstance(max_results, int) or max_results < 1:
                        max_results = 5
                    
                    print(f"Debug: Knowledge search using query: '{query.strip()}' with {max_results} results")
                    
                    # Create RAG tool instance
                    tool_instance = RAGTool()
                    
                    # Execute the knowledge search
                    return tool_instance._run(query.strip(), max_results)
                    
                except Exception as e:
                    return f"❌ Error executing knowledge search tool: {str(e)}"
            
            def _execute_generic_tool(self, tool_module, params: Dict[str, Any]) -> str:
                """Execute generic tools that don't need special credential handling."""
                # For tools like calendar, weather, etc. that don't need credentials
                # Use the original tool implementation
                if hasattr(tool_module, self.name):
                    tool_func = getattr(tool_module, self.name)
                    # Extract only non-credential parameters
                    filtered_params = {k: v for k, v in params.items() 
                                     if not self._tool_parameters.get(k, {}).get("is_credential", False)}
                    return tool_func(**filtered_params)
                else:
                    return f"❌ Tool function {self.name} not found in module {tool_module}"
            
            async def _arun(self, **kwargs) -> str:
                """Async version of tool execution."""
                return self._run(**kwargs)
        
        # Return configured tool instance
        return DynamicTool(agent_config, tool_file, tool_parameters, tool_display_name)
    
    def create_tools_for_agent(self, agent_config: Dict[str, Any]) -> List[BaseTool]:
        """
        Create all tools for a specific agent with their configurations.
        
        Args:
            agent_config: Agent configuration including tools and tool_configs
            
        Returns:
            List[BaseTool]: List of configured tools for the agent
        """
        tools = []
        tool_ids = agent_config.get("tools", [])
        tool_configs = agent_config.get("tool_configs", {})
        
        for tool_id in tool_ids:
            try:
                # Get tool configuration by ID
                tool_config = self.get_tool_config(tool_id)
                
                if not tool_config:
                    print(f"Warning: Tool '{tool_id}' not found in tools configuration")
                    continue
                
                # Get agent-specific configuration for this tool (using tool_id as key)
                agent_tool_config = tool_configs.get(tool_id, {})
                
                # Create the dynamic tool
                tool_instance = self.create_dynamic_tool(tool_id, agent_tool_config)
                tools.append(tool_instance)
                print(f"✓ Successfully created dynamic tool: {tool_id} ({tool_config.get('name', 'unknown')})")
                
            except Exception as e:
                print(f"✗ Failed to create tool '{tool_id}': {e}")
        
        return tools
    
    def get_available_tools(self) -> List[Dict[str, str]]:
        """Get list of all available tools with their descriptions."""
        return [
            {
                "id": tool.get("id"),
                "name": tool.get("name"),
                "description": tool.get("description", ""),
                "file": tool.get("file", ""),
                "parameters": tool.get("parameters", {})
            }
            for tool in self.tools_config
        ] 