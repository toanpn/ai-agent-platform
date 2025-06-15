"""
ADK Tools adapter for converting custom tools to Google ADK format.
This module bridges the existing tool registry with Google ADK tools.
"""

import logging
from typing import Dict, Any, List, Callable
from functools import partial
from google.adk.tools import BaseTool, FunctionTool
from ..models.schemas import AgentFunction
from .registry import get_tool_registry

logger = logging.getLogger(__name__)


def create_adk_tools_from_registry(
    agent_functions: List[AgentFunction],
    credentials: Dict[str, Any] = None
) -> List[BaseTool]:
    """
    Create ADK tools from agent functions and tool registry.
    
    Args:
        agent_functions: Agent functions from database
        credentials: Tool credentials
        
    Returns:
        List[BaseTool]: ADK-compatible tools
    """
    logger.info(f"Creating ADK tools from {len(agent_functions)} agent functions")
    
    tool_registry = get_tool_registry()
    adk_tools = []
    
    for agent_function in agent_functions:
        try:
            # Get tool metadata from registry
            tool_metadata = tool_registry.get_tool(agent_function.name)
            
            if not tool_metadata:
                logger.warning(f"Tool '{agent_function.name}' not found in registry")
                continue
            
            # Create ADK tool from function
            adk_tool = create_adk_tool_from_function(
                tool_metadata.function,
                tool_metadata.name,
                tool_metadata.description,
                tool_metadata.parameters_schema,
                credentials
            )
            
            if adk_tool:
                adk_tools.append(adk_tool)
                logger.debug(f"Created ADK tool: {tool_metadata.name}")
            
        except Exception as e:
            logger.error(f"Error creating ADK tool for '{agent_function.name}': {e}")
            continue
    
    logger.info(f"Created {len(adk_tools)} ADK tools")
    return adk_tools


def create_adk_tool_from_function(
    function: Callable,
    name: str,
    description: str,
    parameters_schema: Dict[str, Any],
    credentials: Dict[str, Any] = None
) -> BaseTool:
    """
    Create an ADK tool from a function.
    
    Args:
        function: The tool function
        name: Tool name
        description: Tool description
        parameters_schema: Parameter schema
        credentials: Tool credentials
        
    Returns:
        BaseTool: ADK tool
    """
    try:
        # If credentials are provided, create partial function with credentials
        if credentials:
            # Extract credentials needed for this function
            function_with_creds = partial(function, **credentials)
        else:
            function_with_creds = function
        
        # Create ADK function tool
        adk_tool = FunctionTool(
            func=function_with_creds,
            name=name,
            description=description
        )
        
        return adk_tool
        
    except Exception as e:
        logger.error(f"Error creating ADK tool '{name}': {e}")
        return None


# Pre-built ADK tools for common functions
class ADKBuiltinTools:
    """
    Collection of ADK-native tools that can replace custom implementations.
    """
    
    @staticmethod
    def get_vertex_search_tool() -> BaseTool:
        """
        Get ADK Vertex AI Search tool.
        
        Returns:
            BaseTool: ADK Vertex AI Search tool
        """
        from google.adk.tools import VertexAiSearchTool
        return VertexAiSearchTool()
    
    @staticmethod
    def get_example_tool() -> BaseTool:
        """
        Get ADK example tool for testing.
        
        Returns:
            BaseTool: ADK example tool
        """
        from google.adk.tools import ExampleTool
        return ExampleTool()


def enhance_with_adk_builtin_tools(
    custom_tools: List[BaseTool],
    enable_vertex_search: bool = True,
    enable_example_tool: bool = False
) -> List[BaseTool]:
    """
    Enhance custom tools with ADK built-in tools.
    
    Args:
        custom_tools: Custom tools list
        enable_vertex_search: Enable Vertex AI Search tool
        enable_example_tool: Enable example tool for testing
        
    Returns:
        List[BaseTool]: Enhanced tools list
    """
    enhanced_tools = custom_tools.copy()
    
    try:
        if enable_vertex_search:
            enhanced_tools.append(ADKBuiltinTools.get_vertex_search_tool())
            logger.info("Added ADK Vertex AI Search tool")
        
        if enable_example_tool:
            enhanced_tools.append(ADKBuiltinTools.get_example_tool())
            logger.info("Added ADK example tool")
            
    except Exception as e:
        logger.error(f"Error adding ADK built-in tools: {e}")
    
    logger.info(f"Enhanced tools: {len(enhanced_tools)} total tools")
    return enhanced_tools


class ADKToolsAdapter:
    """
    Adapter class for converting existing tools to ADK format.
    """
    
    def __init__(self):
        """Initialize the ADK tools adapter."""
        logger.info("ADK Tools Adapter initialized")
    
    def convert_legacy_tools(self, tool_registry) -> List[BaseTool]:
        """
        Convert legacy tools from registry to ADK format.
        
        Args:
            tool_registry: The legacy tool registry
            
        Returns:
            List[BaseTool]: Converted ADK tools
        """
        adk_tools = []
        
        for tool_name in tool_registry.list_tool_names():
            try:
                tool_metadata = tool_registry.get_tool(tool_name)
                if tool_metadata:
                    adk_tool = create_adk_tool_from_function(
                        tool_metadata.function,
                        tool_metadata.name,
                        tool_metadata.description,
                        tool_metadata.parameters_schema
                    )
                    if adk_tool:
                        adk_tools.append(adk_tool)
                        logger.debug(f"Converted tool: {tool_name}")
            except Exception as e:
                logger.error(f"Failed to convert tool '{tool_name}': {e}")
                continue
        
        logger.info(f"Converted {len(adk_tools)} legacy tools")
        return adk_tools 