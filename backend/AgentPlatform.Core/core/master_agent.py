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

IMPORTANT LANGUAGE INSTRUCTION: 
- Always ensure that the final response to the user is provided in Vietnamese
- When delegating to sub-agents, include an instruction that they must respond in Vietnamese
- The user interface expects Vietnamese responses, so this is critical

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
    
    def process_request_with_details(self, user_input: str) -> dict:
        """
        Process a user request and return both response and execution details.
        
        Args:
            user_input: The user's query or request
            
        Returns:
            dict: Contains response, agents used, tools used, and execution details
        """
        try:
            # Log the incoming request
            print(f"Master Agent received request: {user_input}")
            
            # Process the request through the agent executor
            result = self.agent_executor.invoke({"input": user_input})
            
            # Extract the output
            output = result.get("output", "No response generated")
            
            # Extract execution details
            intermediate_steps = result.get("intermediate_steps", [])
            
            # Analyze intermediate steps to extract agents and tools used
            agents_used = set()
            tools_used = set()
            execution_steps = []
            
            for step in intermediate_steps:
                if len(step) >= 2:
                    action, observation = step[0], step[1]
                    
                    # Extract tool/agent name from action
                    if hasattr(action, 'tool'):
                        tool_name = action.tool
                        tools_used.add(tool_name)
                        
                        # Check if this tool is actually a sub-agent
                        for agent in self.sub_agents:
                            if agent.name == tool_name:
                                agents_used.add(tool_name)
                                break
                        else:
                            # It's a regular tool, not a sub-agent
                            pass
                    
                    # Record execution step
                    execution_steps.append({
                        "tool_name": getattr(action, 'tool', 'unknown'),
                        "tool_input": getattr(action, 'tool_input', ''),
                        "observation": str(observation)[:200] + "..." if len(str(observation)) > 200 else str(observation)
                    })
            
            return {
                "response": output,
                "agents_used": list(agents_used),
                "tools_used": list(tools_used),
                "execution_steps": execution_steps,
                "total_steps": len(intermediate_steps)
            }
            
        except Exception as e:
            error_msg = f"Master Agent encountered an error: {str(e)}"
            print(f"Error: {error_msg}")
            return {
                "response": error_msg,
                "agents_used": [],
                "tools_used": [],
                "execution_steps": [],
                "total_steps": 0,
                "error": str(e)
            }
    
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

async def summarize_conversation_async(messages: List[dict]) -> str:
    """
    Generates a concise summary for a given conversation history.

    Args:
        messages: A list of message dictionaries, e.g., [{"role": "user", "content": "..."}]

    Returns:
        A short string summarizing the conversation.
    """
    try:
        # Format the conversation history for the prompt
        history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
        
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", "Based on the following conversation, create a short, descriptive title of 5 words or less. Do not use quotes.\n\n<conversation_history>"),
            ("human", "{history}")
        ])

        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.2)
        
        chain = prompt_template | llm
        
        # Invoke the chain with the conversation history
        response = await chain.ainvoke({"history": history})
        
        # The response from the LLM will be an AIMessage object. We need to get its content.
        summary = response.content.strip().replace('"', '')
        
        return summary
    except Exception as e:
        print(f"Error during conversation summarization: {e}")
        return "New Chat" # Fallback title 