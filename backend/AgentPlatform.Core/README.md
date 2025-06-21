# Dynamic Multi-Agent System

A flexible and extensible multi-agent system that can dynamically load and manage specialized agents based on JSON configuration. The system features a Master Agent that intelligently routes user requests to appropriate Sub-Agents based on their capabilities.

## 🏗️ Architecture Overview

The system follows a hierarchical agent model:

- **Master Agent (Coordinator)**: Routes user requests to appropriate sub-agents
- **Sub-Agents**: Specialized agents for different domains (IT, HR, Search, Personal Assistant, etc.)
- **Agent Manager**: Dynamically loads and manages agents from JSON configuration
- **Tool Kit**: Reusable tools that agents can use to perform specific tasks
- **File Monitoring**: Automatically reloads configuration when `agents.json` changes

## 📁 Project Structure

```
AgentPlatform.Core/
├── main.py                 # Entry point and main application logic
├── agents.json             # Dynamic agent configuration file
├── requirements.txt        # Python dependencies
├── run.sh                  # Easy startup script
├── README.md              # This file
├── core/
│   ├── __init__.py
│   ├── agent_manager.py   # Agent loading and management logic
│   └── master_agent.py    # Master agent implementation
└── toolkit/
    ├── __init__.py
    ├── jira_tool.py       # Jira-related tools
    ├── search_tool.py     # Search and HR-related tools
    └── utility_tools.py   # Google search, calendar, weather tools
```

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Navigate to project directory
cd backend/AgentPlatform.Core

# Create and activate virtual environment (if not done already)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Running the Application

**Option A: Use the startup script (recommended)**
```bash
# Make script executable (first time only)
chmod +x run.sh

# Run the system
./run.sh
```

**Option B: Manual setup**
```bash
# Activate virtual environment
source venv/bin/activate

# Set Google API key
export GOOGLE_API_KEY=AIzaSyAS9BiTbdCqlAZNfNtxMzuGvmOAEZlVqFE

# Run the application
python3 main.py
```

**Option C: One-line command**
```bash
source venv/bin/activate && export GOOGLE_API_KEY=AIzaSyAS9BiTbdCqlAZNfNtxMzuGvmOAEZlVqFE && python3 main.py
```

### 3. Troubleshooting Common Issues

**Error: "ModuleNotFoundError: No module named 'watchdog'"**
- Solution: Make sure the virtual environment is activated with `source venv/bin/activate`

**Error: "GOOGLE_API_KEY not found"**
- Solution: Set the API key with `export GOOGLE_API_KEY=AIzaSyAS9BiTbdCqlAZNfNtxMzuGvmOAEZlVqFE`

**The system loads but agents don't work properly**
- Solution: Ensure both the virtual environment is active AND the API key is set

## 🤖 Available Agents

The system comes pre-configured with five agents:

### IT Support Agent
- **Purpose**: Technical support, troubleshooting, Jira ticket creation
- **Tools**: `jira_ticket_creator`, `it_knowledge_base_search`
- **Example queries**: 
  - "My computer is running slowly, please create a ticket"
  - "How do I fix printer connection issues?"

### HR Agent  
- **Purpose**: HR policies, leave requests, recruitment information
- **Tools**: `policy_document_search`, `leave_request_tool`
- **Example queries**:
  - "What's the company policy on remote work?"
  - "I need to request 3 days of annual leave"

### Search Agent
- **Purpose**: Internet search using Google search
- **Tools**: `google_search`
- **Example queries**:
  - "Search for latest AI technology trends"
  - "Find information about Python programming"

### Personal Assistant Agent
- **Purpose**: Calendar and weather assistance
- **Tools**: `check_calendar`, `check_weather`
- **Example queries**:
  - "What's on my calendar today?"
  - "What's the weather like in New York?"

### General Utility Agent
- **Purpose**: Versatile agent for various tasks
- **Tools**: `google_search`, `check_calendar`, `check_weather`
- **Example queries**:
  - "Check weather and my schedule for today"
  - "Search for meeting room booking system"

## 🛠️ Available Tools

### Jira Tools (`jira_tool.py`)
- `jira_ticket_creator`: Creates new Jira tickets
- `it_knowledge_base_search`: Searches IT knowledge base

### Search Tools (`search_tool.py`)
- `internet_search`: Performs internet searches (legacy)
- `policy_document_search`: Searches company policies
- `leave_request_tool`: Submits leave requests

### Utility Tools (`utility_tools.py`)
- `google_search`: Google web search with real API support
- `check_calendar`: Calendar event checking
- `check_weather`: Weather information and forecasts

## ⚙️ Configuration

### Adding New Agents

Edit `agents.json` to add new agents:

```json
{
  "agent_name": "New_Agent",
  "description": "Description of what this agent does...",
  "tools": ["tool1", "tool2"],
  "llm_config": {
    "model_name": "gemini-2.0-flash",
    "temperature": 0.5
  }
}
```

### Adding New Tools

1. Create a new Python file in the `toolkit/` directory
2. Define tools using the `@tool` decorator:

```python
from langchain.tools import tool

@tool
def my_new_tool(param: str) -> str:
    """
    Description of what this tool does.
    Use this tool when...
    """
    # Implementation here
    return "Tool result"
```

3. Register the tool in `agent_manager.py`:

```python
tools_registry["my_new_tool"] = my_module.my_new_tool
```

## 🔄 Dynamic Configuration

The system automatically reloads when `agents.json` is modified:

1. Edit `agents.json` while the system is running
2. Save the file
3. The system automatically detects changes and reloads
4. New configuration takes effect immediately

## 💬 Interactive Commands

While running, the system supports these commands:

- `help` - Show available commands
- `info` - Display current system configuration
- `reload` - Manually reload agent configuration
- `quit`/`exit`/`q` - Exit the application

## 🔧 Development

### Adding Custom LLM Providers

Extend the system to support other LLM providers by modifying the agent creation logic in `agent_manager.py`.

### Error Handling

The system includes comprehensive error handling:
- Graceful degradation when tools fail
- Automatic fallback to mock responses for some tools
- Detailed error logging and user feedback

### Monitoring and Logging

All agent interactions are logged to the console with detailed information about:
- Request routing decisions
- Tool usage
- Error conditions
- System reloads

## 🚨 Troubleshooting

### Common Issues

1. **"ModuleNotFoundError: No module named 'watchdog'"**
   - Activate the virtual environment: `source venv/bin/activate`

2. **"GOOGLE_API_KEY not found"**
   - Set your Google API key: `export GOOGLE_API_KEY=your_key_here`

3. **System starts but agents don't work**
   - Ensure both virtual environment is active AND API key is set
   - Use the `run.sh` script for automated setup

4. **Agent not responding correctly**
   - Check agent descriptions in `agents.json`
   - Verify tool implementations
   - Review console logs for errors

### Debug Mode

For more detailed logging, the system runs in verbose mode by default. Check console output for:
- Agent loading status
- Request routing decisions  
- Tool execution results
- Error messages

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your changes
4. Test thoroughly
5. Submit a pull request

## 📧 Support

For questions or issues, please create an issue in the project repository. 