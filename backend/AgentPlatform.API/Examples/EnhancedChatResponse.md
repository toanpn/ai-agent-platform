# Enhanced Chat API Response Format

The Chat API has been updated to provide comprehensive information about agent execution, available agents, and tools used during processing.

## Response Structure

```json
{
  "response": "The actual response from the agent system",
  "agentName": "MasterAgent",
  "sessionId": 123,
  "timestamp": "2024-01-15T10:30:00.000Z",
  "success": true,
  "error": null,
  
  "agentsUsed": [
    "General_Utility_Agent",
    "Weather_Agent"
  ],
  
  "toolsUsed": [
    "check_weather",
    "google_search"
  ],
  
  "availableAgents": {
    "totalAgents": 5,
    "agents": [
      {
        "name": "IT_Support_Agent",
        "description": "Handles technical support requests, troubleshooting software and hardware issues"
      },
      {
        "name": "HR_Agent", 
        "description": "Handles HR policies, leave procedures, and recruitment information"
      },
      {
        "name": "Search_Agent",
        "description": "Performs general information searches on the Internet"
      },
      {
        "name": "General_Utility_Agent",
        "description": "Handles various utility tasks including web searches, calendar checks, and weather information"
      },
      {
        "name": "ADK Assistant",
        "description": "Advanced AI assistant with multi-tool capabilities and workflow orchestration"
      }
    ]
  },
  
  "availableTools": [
    {
      "name": "check_weather",
      "description": "Get current weather information for a specified location"
    },
    {
      "name": "google_search", 
      "description": "Search Google for general information and current topics"
    },
    {
      "name": "jira_ticket_creator",
      "description": "Create and manage Jira tickets for issue tracking"
    },
    {
      "name": "policy_document_search",
      "description": "Search through company policy documents and procedures"
    },
    {
      "name": "leave_request_tool",
      "description": "Submit and manage employee leave requests"
    },
    {
      "name": "check_calendar",
      "description": "Check calendar availability and appointments"
    }
  ],
  
  "executionDetails": {
    "totalSteps": 2,
    "executionSteps": [
      {
        "toolName": "General_Utility_Agent",
        "toolInput": "What's the weather like in London today?",
        "observation": "I'll check the current weather in London for you using the weather tool..."
      },
      {
        "toolName": "check_weather",
        "toolInput": "London",
        "observation": "Current weather in London: 15°C, partly cloudy with light rain expected..."
      }
    ]
  },
  
  "metadata": {
    "timestamp": "2024-01-15T10:30:00.000Z",
    "userId": "user123",
    "error": null,
    "processingTimeMs": 1250
  }
}
```

## Enhanced Fields Explanation

### `agentsUsed`
Array of agent names that were actually invoked during the request processing. This shows which specific agents handled the user's request.

### `toolsUsed` 
Array of tool names that were executed during processing. This provides insight into which specific tools were called to fulfill the request.

### `availableAgents`
Complete list of all agents available in the system with their descriptions. This helps clients understand what capabilities are available.

### `availableTools`
Complete list of all tools available in the system with their descriptions. This provides transparency about the system's capabilities.

### `executionDetails`
Detailed step-by-step execution trace showing:
- `totalSteps`: Number of execution steps performed
- `executionSteps`: Array of execution steps with:
  - `toolName`: Name of the tool/agent that was called
  - `toolInput`: Input provided to the tool/agent
  - `observation`: Response or output from the tool/agent

### `metadata`
Additional metadata about the request processing including timing information and error details.

## Benefits

1. **Transparency**: Users can see exactly which agents and tools were used
2. **Debugging**: Detailed execution steps help troubleshoot issues
3. **Discovery**: Available agents and tools help users understand system capabilities
4. **Monitoring**: Execution details enable performance monitoring and optimization
5. **Analytics**: Rich metadata supports usage analytics and improvement insights

## Backward Compatibility

The enhanced response maintains backward compatibility by preserving all original fields (`response`, `agentName`, `sessionId`, `timestamp`). Existing clients will continue to work while new clients can leverage the enhanced information. 