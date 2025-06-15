"""
Central tool registry for managing all available tools.
This registry allows dynamic tool loading and agent assembly.
"""

import logging
from typing import Dict, List, Callable, Any, Optional
from functools import partial
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ToolMetadata:
    """
    Metadata for a registered tool function.
    """
    name: str
    description: str
    function: Callable
    required_credentials: List[str]
    parameters_schema: Dict[str, Any]
    category: str = "general"


class ToolRegistry:
    """
    Central registry for all available tools.
    """
    
    def __init__(self):
        """Initialize the tool registry."""
        self._tools: Dict[str, ToolMetadata] = {}
        self._categories: Dict[str, List[str]] = {}
        logger.info("Tool registry initialized")
    
    def register_tool(
        self,
        name: str,
        function: Callable,
        description: str,
        required_credentials: List[str] = None,
        parameters_schema: Dict[str, Any] = None,
        category: str = "general"
    ) -> None:
        """
        Register a tool function in the registry.
        
        Args:
            name: Unique name for the tool
            function: The tool function to register
            description: Description of what the tool does
            required_credentials: List of required credential keys
            parameters_schema: JSON schema for function parameters
            category: Tool category (e.g., 'jira', 'calendar', 'confluence')
        """
        if name in self._tools:
            logger.warning(f"Tool '{name}' is already registered. Overwriting...")
        
        tool_metadata = ToolMetadata(
            name=name,
            description=description,
            function=function,
            required_credentials=required_credentials or [],
            parameters_schema=parameters_schema or {},
            category=category
        )
        
        self._tools[name] = tool_metadata
        
        # Update category index
        if category not in self._categories:
            self._categories[category] = []
        if name not in self._categories[category]:
            self._categories[category].append(name)
        
        logger.info(f"Registered tool '{name}' in category '{category}'")
    
    def get_tool(self, name: str) -> Optional[ToolMetadata]:
        """
        Get a tool by name.
        
        Args:
            name: Tool name
            
        Returns:
            ToolMetadata: Tool metadata if found, None otherwise
        """
        return self._tools.get(name)
    
    def get_tools_by_category(self, category: str) -> List[ToolMetadata]:
        """
        Get all tools in a specific category.
        
        Args:
            category: Tool category
            
        Returns:
            List[ToolMetadata]: List of tools in the category
        """
        tool_names = self._categories.get(category, [])
        return [self._tools[name] for name in tool_names if name in self._tools]
    
    def list_all_tools(self) -> List[ToolMetadata]:
        """
        List all registered tools.
        
        Returns:
            List[ToolMetadata]: List of all registered tools
        """
        return list(self._tools.values())
    
    def list_tool_names(self) -> List[str]:
        """
        List all tool names.
        
        Returns:
            List[str]: List of all tool names
        """
        return list(self._tools.keys())
    
    def create_tool_instance(
        self,
        name: str,
        credentials: Dict[str, Any] = None
    ) -> Optional[Callable]:
        """
        Create a tool instance with injected credentials.
        
        Args:
            name: Tool name
            credentials: Dictionary of credentials to inject
            
        Returns:
            Callable: Tool function with credentials injected, or None if not found
        """
        tool_metadata = self.get_tool(name)
        if not tool_metadata:
            logger.error(f"Tool '{name}' not found in registry")
            return None
        
        # Check if all required credentials are provided
        missing_credentials = []
        for required_cred in tool_metadata.required_credentials:
            if not credentials or required_cred not in credentials:
                missing_credentials.append(required_cred)
        
        if missing_credentials:
            logger.error(f"Missing required credentials for tool '{name}': {missing_credentials}")
            return None
        
        # Create partial function with credentials injected
        if credentials:
            try:
                # Create a partial function with credentials
                return partial(tool_metadata.function, **credentials)
            except Exception as e:
                logger.error(f"Error creating tool instance for '{name}': {e}")
                return None
        else:
            return tool_metadata.function
    
    def get_tool_schema(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get the parameter schema for a tool.
        
        Args:
            name: Tool name
            
        Returns:
            Dict[str, Any]: Tool parameter schema if found, None otherwise
        """
        tool_metadata = self.get_tool(name)
        return tool_metadata.parameters_schema if tool_metadata else None
    
    def get_tools_summary(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get a summary of all tools organized by category.
        
        Returns:
            Dict: Tools organized by category with metadata
        """
        summary = {}
        for category, tool_names in self._categories.items():
            summary[category] = []
            for tool_name in tool_names:
                if tool_name in self._tools:
                    tool = self._tools[tool_name]
                    summary[category].append({
                        "name": tool.name,
                        "description": tool.description,
                        "required_credentials": tool.required_credentials,
                        "parameters_schema": tool.parameters_schema
                    })
        return summary


# Global tool registry instance
_global_registry = None


def get_tool_registry() -> ToolRegistry:
    """
    Get the global tool registry instance.
    
    Returns:
        ToolRegistry: Global tool registry
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = ToolRegistry()
        # Register all tools on first access
        _register_all_tools()
    return _global_registry


def _register_all_tools():
    """
    Register all available tools in the registry.
    This function imports and registers tools from all tool modules.
    """
    logger.info("Registering all available tools...")
    
    # Import and register tools from different modules
    try:
        from . import jira
        logger.info("Jira tools registered")
    except ImportError as e:
        logger.warning(f"Could not import Jira tools: {e}")
    
    try:
        from . import google_calendar
        logger.info("Google Calendar tools registered")
    except ImportError as e:
        logger.warning(f"Could not import Google Calendar tools: {e}")
    
    try:
        from . import confluence
        logger.info("Confluence tools registered")
    except ImportError as e:
        logger.warning(f"Could not import Confluence tools: {e}")
  
    registry = get_tool_registry()
    logger.info(f"Total tools registered: {len(registry.list_tool_names())}")
    logger.info(f"Available tools: {registry.list_tool_names()}") 