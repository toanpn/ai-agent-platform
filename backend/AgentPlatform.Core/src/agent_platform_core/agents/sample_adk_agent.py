"""
Sample ADK agent for testing AgentPlatform.Core integration.
"""

from adk import LlmAgent
from adk.models import GeminiModel
from adk.tools import SearchTool

def create_sample_agent():
    """Create a sample ADK agent."""
    model = GeminiModel("gemini-pro")
    tools = [SearchTool()]
    
    agent = LlmAgent(
        name="Sample Agent",
        model=model,
        system_prompt="You are a helpful AI assistant.",
        tools=tools,
        description="Sample agent for testing"
    )
    
    return agent

if __name__ == "__main__":
    agent = create_sample_agent()
    print(f"Created sample agent: {agent.name}")
