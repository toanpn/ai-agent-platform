Technical Specification: Dynamic Multi-Agent System

1. Overview
This document describes the technical architecture and design for a flexible Multi-Agent system. The primary goal is to build a Master Agent (Coordinator Agent) capable of automatically recognizing, loading, and dispatching tasks to a set of Sub-Agents (Specialized Agents for departments).

These Sub-Agents are defined entirely in an external JSON configuration file. When this JSON file changes (adding, deleting, or modifying an agent), the system will update automatically without requiring a restart or intervention in the source code, creating a dynamic and easily expandable architecture.

2. System Architecture
The system is built on a Hierarchical Agent model, where the Master Agent acts as the central brain, deciding which task should be assigned to which Sub-Agent.

Key Components:
User Interface: The communication channel for end-users to submit queries.

Master Agent (Coordinator Agent):

The highest-level agent, receiving all user requests.

Does not directly execute tasks.

Its sole responsibility is to analyze the request and route it to the most suitable Sub-Agent.

It treats each Sub-Agent as a special "tool".

Agent Loader:

An intermediary module that monitors the agents.json file.

Responsible for reading the configuration file, initializing Sub-Agents, and providing them to the Master Agent.

When the file changes, it reloads the configuration and updates the Master Agent.

Configuration File (agents.json):

A JSON file that defines the list of Sub-Agents, including their name, description (instruction), and the list of tools they are allowed to use.

Sub-Agents (Specialized Agents):

Represent various departments (e.g., HR, IT, Sales).

Each agent is equipped with a specific set of tools from the Toolkit to handle specialized tasks.

Tool Kit:

A directory containing Python files, each defining one or more reusable tools (e.g., search_tool.py, jira_tool.py, calendar_tool.py).

3. Detailed Specification
3.1. agents.json File Structure
This is the "soul" of the system, allowing for the dynamic definition of agents without code.

[
  {
    "agent_name": "IT_Support_Agent",
    "description": "Useful for resolving technical support requests, troubleshooting software and hardware issues, and handling Jira-related problems. The input must be a complete question.",
    "tools": [
      "jira_ticket_creator",
      "it_knowledge_base_search"
    ],
    "llm_config": {
      "model_name": "gemini-1.5-pro-latest",
      "temperature": 0.0
    }
  },
  {
    "agent_name": "HR_Agent",
    "description": "Useful for questions about HR policies, leave procedures, and recruitment information. The input must be a complete question.",
    "tools": [
      "policy_document_search",
      "leave_request_tool"
    ],
    "llm_config": {
      "model_name": "gemini-1.5-pro-latest",
      "temperature": 0.7
    }
  },
  {
    "agent_name": "General_Search_Agent",
    "description": "Useful for searching for general information on the Internet or for questions that do not fall under the expertise of other agents. The input is a search query string.",
    "tools": [
      "internet_search"
    ],
    "llm_config": {
      "model_name": "gemini-pro",
      "temperature": 0.5
    }
  }
]

agent_name: A unique identifier.

description: Most important. This description helps the Master Agent understand the Sub-Agent's function and decide when to call it. The description must be clear and detailed.

tools: An array of tool names that this agent has access to. The names must match the tool names defined in the Tool Kit.

llm_config: (Optional) Allows for customizing the LLM model and its parameters for each agent.

3.2. Tool Kit Definition
Each tool is a Python function decorated with LangChain's @tool.

Location: toolkit/

Example: toolkit/jira_tool.py

from langchain.tools import tool

@tool
def jira_ticket_creator(issue_summary: str, issue_description: str, project_key: str = "IT") -> str:
    """
    Creates a new ticket in Jira.
    Use this tool when a user wants to report a new IT issue.
    Returns the ID of the newly created ticket, e.g., 'IT-1234'.
    """
    # ... (Logic to connect to Jira API and create a ticket) ...
    print(f"Creating Jira ticket in project {project_key} with summary: {issue_summary}")
    # This is a mock response
    new_ticket_id = "IT-1235"
    return f"Successfully created Jira ticket with ID: {new_ticket_id}"

@tool
def it_knowledge_base_search(query: str) -> str:
    """
    Searches the IT knowledge base for solutions to common problems.
    Use this to find instruction documents or troubleshooting guides.
    """
    # ... (Logic to search a local database or a specific document store) ...
    return f"Found 3 articles related to '{query}'. The most relevant is: 'How to fix printer connection issues'."

Important:

The function must have a docstring that clearly describes its functionality, inputs, and outputs. The LangChain Agent will use this docstring to decide how to use the tool.

The function name (jira_ticket_creator) is the tool_name referenced in agents.json.

3.3. AgentManager Module
This is the core module responsible for dynamically creating and managing agents.

Location: core/agent_manager.py

# Logical diagram of agent_manager.py

import json
from typing import List, Dict, Any
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.tools import BaseTool, tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

# --- 1. Tool Loading ---
from toolkit import jira_tool, search_tool # Assume all tools are imported

# Create a registry for easy access to tools by name
AVAILABLE_TOOLS = {
    "jira_ticket_creator": jira_tool.jira_ticket_creator,
    "it_knowledge_base_search": jira_tool.it_knowledge_base_search,
    "internet_search": search_tool.internet_search,
    # ... add other tools here
}

# --- 2. Sub-Agent Creation ---
def create_sub_agent(config: Dict[str, Any]) -> BaseTool:
    """
    Creates a Sub-Agent from a configuration and wraps it as a BaseTool
    for the Master Agent to use.
    """
    agent_name = config["agent_name"]
    description = config["description"]
    tool_names = config["tools"]
    llm_config = config.get("llm_config", {})

    # Get the actual tool objects from the registry
    agent_tools = [AVAILABLE_TOOLS[name] for name in tool_names]

    # Initialize the LLM for the sub-agent
    llm = ChatGoogleGenerativeAI(model=llm_config.get("model_name", "gemini-pro"),
                               temperature=llm_config.get("temperature", 0.2))

    # Create the prompt for the sub-agent
    prompt = ChatPromptTemplate.from_messages([
        ("system", f"You are a helpful assistant named {agent_name}. Your purpose is: {description}. You have access to the following tools."),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])
    
    # Create the agent executor
    agent = create_tool_calling_agent(llm, agent_tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=agent_tools, verbose=True)

    # **Important**: Wrap the agent executor into a single tool for the Master Agent
    @tool(name=agent_name)
    def agent_as_tool(input: str) -> str:
        """
        Wraps this agent into a tool. The tool's description is the agent's description.
        This description is crucial for the Master Agent to know when to call this tool.
        """
        return agent_executor.invoke({"input": input})
    
    agent_as_tool.description = description # Dynamically assign the description
    return agent_as_tool

# --- 3. Main Loading Function ---
def load_agents_from_config(config_path: str = "agents.json") -> List[BaseTool]:
    """Reads the JSON file and creates a list of sub-agents (wrapped as tools)."""
    with open(config_path, 'r', encoding='utf-8') as f:
        configs = json.load(f)
    
    return [create_sub_agent(config) for config in configs]

3.4. Master Agent (Coordinator Agent)
The Master Agent is initialized with a list of Sub-Agents (which have been wrapped as tools).

Location: core/master_agent.py

# Logical diagram of master_agent.py
from typing import List
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.tools import BaseTool
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

def create_master_agent(sub_agents_as_tools: List[BaseTool]) -> AgentExecutor:
    """Creates the Master Agent with sub-agents as its tools."""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a powerful master agent. Your job is to understand the user's query and delegate it to the correct specialist agent. Do not answer directly. Use the available agents to find the answer."),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])
    
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest", temperature=0)
    
    agent = create_tool_calling_agent(llm, sub_agents_as_tools, prompt)
    
    master_agent_executor = AgentExecutor(
        agent=agent,
        tools=sub_agents_as_tools,
        verbose=True,
        handle_parsing_errors=True
    )
    
    return master_agent_executor

4. Workflow
4.1. Initialization & Monitoring
Location: main.py

Start: The application launches.

Initial Load: Call agent_manager.load_agents_from_config() to read agents.json and create the list of sub_agents_as_tools.

Initialize Master Agent: Call master_agent.create_master_agent() with the tool list from the previous step to create the master_agent_executor.

Listen for Changes: Use the watchdog library to monitor "modified" events on the agents.json file.

Callback Function: When watchdog detects a change, it calls a callback function. This function re-executes steps 2 and 3, creating a new master_agent_executor and replacing the old one.

4.2. User Interaction
A user sends a query, e.g., "My computer is running very slowly, please help me create an IT ticket."

The query is passed to master_agent_executor.invoke({"input": "..."}).

The Master Agent's LLM sees that the query relates to an "IT ticket" and matches it with the description of the IT_Support_Agent.

The Master Agent decides to call the IT_Support_Agent tool with the user's query as input.

The IT_Support_Agent is activated. Its LLM analyzes "My computer is running very slowly, please help me create an IT ticket" and sees that it needs to use the jira_ticket_creator tool.

The IT_Support_Agent calls jira_ticket_creator, possibly extracting the necessary parameters from the query.

The jira_ticket_creator tool executes its logic (calls the Jira API) and returns a result (e.g., "Successfully created Jira ticket with ID: IT-1235").

The result is returned to the Master Agent and finally to the user.

5. Project Directory Structure
/AgentPlatform.Core
|
|-- main.py                 # Entry point, main loop, and file watcher
|-- agents.json             # Dynamic agent configuration file
|-- requirements.txt        # Python dependencies
|-- .env                    # Contains API keys (e.g., GOOGLE_API_KEY)
|
|-- /core
|   |-- __init__.py
|   |-- agent_manager.py      # Logic to load and create agents from JSON
|   `-- master_agent.py       # Logic to create the master agent
|
`-- /toolkit
    |-- __init__.py
    |-- search_tool.py        # Defines search-related tools
    |-- jira_tool.py          # Defines Jira-related tools
    `-- ... (other tool files)

6. Technology and Libraries
Python: 3.9+

LangChain: The main framework for building Agents.

langchain

langchain-google-genai

Watchdog: A library for monitoring file system changes.

python-dotenv: For managing environment variables (API keys).

7. Implementation Steps
Environment Setup: Create a virtual environment, install libraries from requirements.txt.

Develop Toolkit: Write the tool functions in the toolkit/ directory as specified. Each tool needs a clear docstring.

Implement Agent Manager: Fully implement the logic in core/agent_manager.py to load tools and create Sub-Agents.

Implement Master Agent: Implement core/master_agent.py.

Write main.py: Integrate the modules, set up the user input loop, and configure watchdog to monitor agents.json.

Testing: Create an initial agents.json file and test various scenarios. Pay special attention to the Master Agent's routing capabilities.

Refinement: Adjust the description of agents in the JSON file and the docstring of tools to optimize routing and execution.