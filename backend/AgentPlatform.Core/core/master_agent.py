"""
Master Agent Module

This module contains the Master Agent (Coordinator Agent) that receives all user requests
and intelligently routes them to the most appropriate Sub-Agent based on the request content
and agent descriptions.
"""

import os
from typing import List
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.tools import BaseTool
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI


class MasterAgent:
    def __init__(self, sub_agents_as_tools: List[BaseTool]):
        """
        Initialize the Master Agent with sub-agents as tools.
        
        Args:
            sub_agents_as_tools: List of sub-agents wrapped as BaseTool objects
        """
        self.sub_agents = sub_agents_as_tools
        self.agent_executor = self._create_master_agent_executor()
    
    def _create_master_agent_executor(self) -> AgentExecutor:
        """Creates the Master Agent executor with sub-agents as its tools."""
        
        # Create a comprehensive prompt for the master agent
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a powerful Master Agent responsible for coordinating and delegating tasks to specialized agents. 

Your primary responsibilities:
1. Analyze incoming user requests carefully
2. Determine which specialized agent is best suited to handle the request
3. Route the request to the appropriate agent
4. Never attempt to answer directly - always use the available specialist agents

Available Specialist Agents:
{agent_descriptions}

Guidelines for routing requests:
- Read the user's request thoroughly
- Match the request type with agent capabilities based on their descriptions
- Always delegate to the most appropriate specialist agent
- If a request could fit multiple agents, choose the most specific one
- If no agent seems appropriate, use the General_Search_Agent as a fallback
- Pass the complete user question to the selected agent

Remember: Your job is to be a smart router, not to provide direct answers. Trust your specialist agents to handle their domains of expertise."""),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])
        
        # Generate agent descriptions for the prompt
        agent_descriptions = []
        for agent in self.sub_agents:
            agent_descriptions.append(f"- {agent.name}: {agent.description}")
        
        # Format the prompt with agent descriptions
        formatted_prompt = prompt.partial(agent_descriptions="\n".join(agent_descriptions))
        
        # Initialize the LLM for the master agent
        try:
            llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash", 
                temperature=0.1  # Low temperature for consistent routing decisions
            )
        except Exception as e:
            raise RuntimeError(f"Failed to initialize LLM for Master Agent: {e}")
        
        # Create the master agent
        agent = create_tool_calling_agent(llm, self.sub_agents, formatted_prompt)
        
        # Create the agent executor
        master_agent_executor = AgentExecutor(
            agent=agent,
            tools=self.sub_agents,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5,
            return_intermediate_steps=True  # Help with debugging
        )
        
        return master_agent_executor
    
    def process_request(self, user_input: str) -> str:
        """
        Process a user request by routing it to the appropriate sub-agent.
        
        Args:
            user_input: The user's query or request
            
        Returns:
            str: The response from the appropriate sub-agent
        """
        try:
            # Log the incoming request
            print(f"Master Agent received request: {user_input}")
            
            # Process the request through the agent executor
            result = self.agent_executor.invoke({"input": user_input})
            
            # Extract the output
            output = result.get("output", "No response generated")
            
            return output
            
        except Exception as e:
            error_msg = f"Master Agent encountered an error: {str(e)}"
            print(f"Error: {error_msg}")
            return error_msg
    
    def update_sub_agents(self, new_sub_agents: List[BaseTool]):
        """
        Update the sub-agents and recreate the master agent executor.
        This is called when the agents configuration is reloaded.
        
        Args:
            new_sub_agents: Updated list of sub-agents as tools
        """
        print("Updating Master Agent with new sub-agents configuration...")
        self.sub_agents = new_sub_agents
        self.agent_executor = self._create_master_agent_executor()
        print(f"Master Agent updated with {len(new_sub_agents)} sub-agents")
    
    def get_agent_info(self) -> dict:
        """
        Get information about the current configuration of agents.
        
        Returns:
            dict: Information about loaded agents
        """
        agent_info = {
            "total_agents": len(self.sub_agents),
            "agents": []
        }
        
        for agent in self.sub_agents:
            agent_info["agents"].append({
                "name": agent.name,
                "description": agent.description
            })
        
        return agent_info
    
    async def process_request_async(self, user_input: str) -> str:
        """
        Async version of process_request for web applications.
        
        Args:
            user_input: The user's query or request
            
        Returns:
            str: The response from the appropriate sub-agent
        """
        # For now, this just calls the sync version
        # In a production environment, you might want to use async LangChain components
        return self.process_request(user_input)


def create_master_agent(sub_agents_as_tools: List[BaseTool]) -> MasterAgent:
    """
    Factory function to create a Master Agent instance.
    
    Args:
        sub_agents_as_tools: List of sub-agents wrapped as BaseTool objects
        
    Returns:
        MasterAgent: Configured master agent instance
    """
    if not sub_agents_as_tools:
        raise ValueError("At least one sub-agent must be provided")
    
    return MasterAgent(sub_agents_as_tools) 