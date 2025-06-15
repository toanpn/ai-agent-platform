"""
Google ADK Agent implementations for AgentPlatform.Core.
This module replaces the custom agent runtime with Google ADK.
"""

import logging
import os
from typing import Dict, Any, List, Optional
from google.adk.agents import LlmAgent, SequentialAgent, ParallelAgent, LoopAgent
from google.adk.tools import BaseTool
from google.adk.models import Gemini

from ..models.schemas import AgentConfig, ChatRequest, ChatResponse
from ..tools.adk_tools import create_adk_tools_from_registry

logger = logging.getLogger(__name__)


class ADKAgentFactory:
    """
    Factory for creating Google ADK agents based on agent configurations.
    """
    
    def __init__(self, google_api_key: str):
        """
        Initialize the ADK agent factory.
        
        Args:
            google_api_key: Google API key for Gemini
        """
        self.google_api_key = google_api_key
        # ADK handles configuration internally
        self.model = Gemini(model_name="gemini-pro", api_key=google_api_key)
        logger.info("ADK Agent Factory initialized")
    
    def create_agent(
        self,
        agent_config: AgentConfig,
        credentials: Dict[str, Any] = None
    ) -> LlmAgent:
        """
        Create an ADK agent from configuration.
        
        Args:
            agent_config: Agent configuration from database
            credentials: Tool credentials
            
        Returns:
            LlmAgent: Configured ADK agent
        """
        logger.info(f"Creating ADK agent: {agent_config.name}")
        
        # Create tools from agent functions
        tools = self._create_agent_tools(agent_config, credentials)
        
        # Build system prompt
        system_prompt = self._build_system_prompt(agent_config)
        
        # Create LLM agent with ADK
        agent = LlmAgent(
            name=agent_config.name,
            model=self.model,
            system_prompt=system_prompt,
            tools=tools,
            description=agent_config.description or f"AI Assistant for {agent_config.department}"
        )
        
        logger.info(f"Created ADK agent '{agent_config.name}' with {len(tools)} tools")
        return agent
    
    def create_multi_agent_system(
        self,
        agent_configs: List[AgentConfig],
        orchestration_type: str = "sequential",
        credentials: Dict[str, Any] = None
    ):
        """
        Create a multi-agent system using ADK workflow agents.
        
        Args:
            agent_configs: List of agent configurations
            orchestration_type: "sequential", "parallel", or "loop"
            credentials: Tool credentials
            
        Returns:
            Agent: ADK workflow agent
        """
        logger.info(f"Creating {orchestration_type} multi-agent system with {len(agent_configs)} agents")
        
        # Create individual agents
        agents = []
        for config in agent_configs:
            agent = self.create_agent(config, credentials)
            agents.append(agent)
        
        # Create workflow agent based on type
        if orchestration_type == "sequential":
            workflow_agent = SequentialAgent(
                name="Agent Platform Sequential Workflow",
                agents=agents,
                description="Sequential execution of specialized agents"
            )
        elif orchestration_type == "parallel":
            workflow_agent = ParallelAgent(
                name="Agent Platform Parallel Workflow", 
                agents=agents,
                description="Parallel execution of specialized agents"
            )
        elif orchestration_type == "loop":
            workflow_agent = LoopAgent(
                name="Agent Platform Loop Workflow",
                agents=agents,
                description="Loop-based execution of specialized agents"
            )
        else:
            raise ValueError(f"Unsupported orchestration type: {orchestration_type}")
        
        logger.info(f"Created {orchestration_type} workflow agent")
        return workflow_agent
    
    def _create_agent_tools(
        self,
        agent_config: AgentConfig,
        credentials: Dict[str, Any] = None
    ) -> List[BaseTool]:
        """
        Create ADK tools from agent configuration.
        
        Args:
            agent_config: Agent configuration
            credentials: Tool credentials
            
        Returns:
            List[BaseTool]: ADK tools
        """
        return create_adk_tools_from_registry(agent_config.functions, credentials)
    
    def _build_system_prompt(self, agent_config: AgentConfig) -> str:
        """
        Build system prompt for the agent.
        
        Args:
            agent_config: Agent configuration
            
        Returns:
            str: System prompt
        """
        prompt_parts = [
            f"You are {agent_config.name}, an AI agent from the {agent_config.department} department.",
        ]
        
        if agent_config.description:
            prompt_parts.append(f"Your role: {agent_config.description}")
        
        if agent_config.instructions:
            prompt_parts.append(f"Instructions: {agent_config.instructions}")
        
        prompt_parts.extend([
            "You have access to various tools to help users accomplish their tasks.",
            "Always be helpful, accurate, and professional in your responses.",
            "Use the available tools when they can help provide better answers or complete tasks.",
            "If you need clarification, ask specific questions to better understand the request."
        ])
        
        return "\n".join(prompt_parts)


class ADKAgentRuntime:
    """
    ADK-based agent runtime that replaces the custom runtime.
    """
    
    def __init__(self, google_api_key: str):
        """
        Initialize the ADK agent runtime.
        
        Args:
            google_api_key: Google API key
        """
        self.factory = ADKAgentFactory(google_api_key)
        self._agent_cache: Dict[int, LlmAgent] = {}
        logger.info("ADK Agent Runtime initialized")
    
    async def process_chat(
        self,
        agent_config: AgentConfig,
        chat_request: ChatRequest,
        credentials: Dict[str, Any] = None
    ) -> ChatResponse:
        """
        Process chat request using ADK agent.
        
        Args:
            agent_config: Agent configuration
            chat_request: Chat request
            credentials: Tool credentials
            
        Returns:
            ChatResponse: Agent response
        """
        logger.info(f"Processing chat with ADK agent {agent_config.name}")
        
        try:
            # Get or create agent
            agent = self._get_or_create_agent(agent_config, credentials)
            
            # Process with ADK agent
            result = await agent.run(
                input_data=chat_request.user_message,
                context={
                    "session_id": chat_request.session_id,
                    "chat_history": chat_request.chat_history or []
                }
            )
            
            # Convert ADK result to ChatResponse
            response = ChatResponse(
                response=result.output,
                sources=self._extract_sources_from_result(result),
                session_id=chat_request.session_id or 1
            )
            
            logger.info(f"ADK agent '{agent_config.name}' generated response")
            return response
            
        except Exception as e:
            logger.error(f"Error in ADK agent processing: {e}", exc_info=True)
            return ChatResponse(
                response="I encountered an error while processing your request. Please try again.",
                sources=[],
                session_id=chat_request.session_id or 1
            )
    
    def _get_or_create_agent(
        self,
        agent_config: AgentConfig,
        credentials: Dict[str, Any] = None
    ) -> LlmAgent:
        """
        Get cached agent or create new one.
        
        Args:
            agent_config: Agent configuration
            credentials: Tool credentials
            
        Returns:
            LlmAgent: ADK agent
        """
        agent_id = agent_config.id
        
        if agent_id not in self._agent_cache:
            self._agent_cache[agent_id] = self.factory.create_agent(agent_config, credentials)
        
        return self._agent_cache[agent_id]
    
    def _extract_sources_from_result(self, result) -> List[Dict[str, Any]]:
        """
        Extract sources from ADK agent result.
        
        Args:
            result: ADK agent result
            
        Returns:
            List[Dict[str, Any]]: Sources
        """
        sources = []
        
        # ADK results may contain tool execution information
        if hasattr(result, 'tool_calls') and result.tool_calls:
            for tool_call in result.tool_calls:
                sources.append({
                    "type": "tool_result",
                    "tool": getattr(tool_call, 'name', 'unknown'),
                    "result": getattr(tool_call, 'result', {}),
                    "title": f"Tool: {getattr(tool_call, 'name', 'unknown')}"
                })
        
        return sources
    
    def clear_agent_cache(self) -> None:
        """Clear the agent cache."""
        self._agent_cache.clear()
        logger.info("Agent cache cleared") 