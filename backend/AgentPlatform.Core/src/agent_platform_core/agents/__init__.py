"""
Agent modules for AgentPlatform.Core with Google ADK integration.
"""

# ADK Agent Components (New)
from .adk_agents import ADKAgentFactory, ADKAgentRuntime

# Export ADK components
__all__ = [
    "ADKAgentFactory",
    "ADKAgentRuntime"
] 