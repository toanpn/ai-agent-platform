# Chat System API Specification

## Overview

This document provides detailed API specifications for the Chat System endpoints in the AI Agent Platform. All endpoints require JWT authentication and operate under the `/api/chat` base path.

## Authentication

All chat endpoints require a valid JWT token in the Authorization header:

```http
Authorization: Bearer <jwt_token>
```

The JWT token must contain a valid `NameIdentifier` claim representing the user ID.

## Base URL

```
{base_url}/api/chat
```

## Endpoints

### 1. Send Message

Send a message to the agent system and receive an enhanced response with execution details.

#### Request

```http
POST /api/chat/message
Content-Type: application/json
Authorization: Bearer <jwt_token>
```

#### Request Body

```json
{
  "message": "string", // Required: The user's message
  "sessionId": "integer", // Optional: Existing session ID to continue conversation
  "agentName": "string" // Optional: Specific agent to route the message to
}
```

#### Response

```json
{
  "response": "string", // The main response from the agent
  "agentName": "string", // Name of the agent that processed the request
  "sessionId": "integer", // Session ID for this conversation
  "timestamp": "2024-01-01T12:00:00Z", // ISO 8601 timestamp
  "success": true, // Boolean indicating success
  "error": "string", // Error message if success is false
  "masterAgentThinking": "string", // Master agent's reasoning (when execution steps exist)
  
  // Enhanced response fields
  "agentsUsed": ["agent1", "agent2"], // List of agents involved
  "toolsUsed": ["tool1", "tool2"], // List of tools executed
  "executionDetails": {
    "totalSteps": 3,
    "executionSteps": [
      {
        "toolName": "string", // Name of the tool/agent executed
        "toolInput": "string", // Input parameters sent to the tool
        "observation": "string" // Output/response from the tool
      }
    ]
  },
  "metadata": {} // Additional metadata as key-value pairs
}
```

#### Status Codes

- `200 OK`: Message processed successfully
- `400 Bad Request`: Invalid request body or missing required fields
- `401 Unauthorized`: Invalid or missing JWT token
- `500 Internal Server Error`: Error processing the message

#### Example

**Request:**
```http
POST /api/chat/message
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

{
  "message": "What's the weather like today?",
  "sessionId": 123
}
```

**Response:**
```json
{
  "response": "Today's weather in your location shows sunny skies with a temperature of 72°F (22°C).",
  "agentName": "WeatherAgent",
  "sessionId": 123,
  "timestamp": "2024-01-15T14:30:00Z",
  "success": true,
  "error": null,
  "masterAgentThinking": "The user is asking about weather. I need to use the WeatherAgent to get current conditions.",
  "agentsUsed": ["MasterAgent", "WeatherAgent"],
  "toolsUsed": ["weather_lookup"],
  "executionDetails": {
    "totalSteps": 1,
    "executionSteps": [
      {
        "toolName": "WeatherAgent",
        "toolInput": "location: user_location, query: current_weather",
        "observation": "Today's weather in your location shows sunny skies with a temperature of 72°F (22°C)."
      }
    ]
  },
  "metadata": {
    "location": "San Francisco, CA",
    "temperature_unit": "fahrenheit"
  }
}
```

### 2. Get Chat History

Retrieve paginated chat history for the authenticated user.

#### Request

```http
GET /api/chat/history?page={page}&pageSize={pageSize}
Authorization: Bearer <jwt_token>
```

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| page | integer | 1 | Page number (1-based) |
| pageSize | integer | 10 | Number of sessions per page |

#### Response

```json
{
  "sessions": [
    {
      "id": 123,
      "title": "Weather Discussion", // Nullable
      "isActive": true,
      "createdAt": "2024-01-15T10:00:00Z",
      "messages": [
        {
          "id": 456,
          "content": "What's the weather like?",
          "role": "user",
          "agentName": null,
          "createdAt": "2024-01-15T10:00:00Z"
        },
        {
          "id": 457,
          "content": "Today's weather is sunny with 72°F.",
          "role": "assistant",
          "agentName": "WeatherAgent",
          "createdAt": "2024-01-15T10:00:30Z"
        }
      ]
    }
  ],
  "totalCount": 25, // Total number of sessions for pagination
  "page": 1,
  "pageSize": 10
}
```

#### Status Codes

- `200 OK`: History retrieved successfully
- `401 Unauthorized`: Invalid or missing JWT token
- `500 Internal Server Error`: Error retrieving history

### 3. Get Chat Session

Retrieve a specific chat session with all messages.

#### Request

```http
GET /api/chat/sessions/{sessionId}
Authorization: Bearer <jwt_token>
```

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| sessionId | integer | The ID of the chat session |

#### Response

```json
{
  "id": 123,
  "title": "Weather Discussion",
  "isActive": true,
  "createdAt": "2024-01-15T10:00:00Z",
  "messages": [
    {
      "id": 456,
      "content": "What's the weather like?",
      "role": "user",
      "agentName": null,
      "createdAt": "2024-01-15T10:00:00Z"
    },
    {
      "id": 457,
      "content": "Today's weather is sunny with 72°F.",
      "role": "assistant",
      "agentName": "WeatherAgent",
      "createdAt": "2024-01-15T10:00:30Z"
    }
  ]
}
```

#### Status Codes

- `200 OK`: Session retrieved successfully
- `401 Unauthorized`: Invalid or missing JWT token
- `404 Not Found`: Session not found or user doesn't have access
- `500 Internal Server Error`: Error retrieving session

### 4. Delete Chat Session

Delete a specific chat session and all associated messages.

#### Request

```http
DELETE /api/chat/sessions/{sessionId}
Authorization: Bearer <jwt_token>
```

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| sessionId | integer | The ID of the chat session to delete |

#### Response

No response body.

#### Status Codes

- `204 No Content`: Session deleted successfully
- `401 Unauthorized`: Invalid or missing JWT token
- `404 Not Found`: Session not found or user doesn't have access
- `500 Internal Server Error`: Error deleting session

## Message Roles

The system supports three message roles:

| Role | Description |
|------|-------------|
| `user` | Messages sent by the user |
| `assistant` | Messages sent by AI agents |
| `system` | System-generated messages (future use) |

## Enhanced Response Processing

### Master Agent Thinking

When the agent system executes multiple steps to process a request, the response includes:

- **response**: The final answer from the best execution step
- **masterAgentThinking**: The master agent's reasoning process
- **agentName**: The name of the agent that provided the final answer
- **executionDetails**: Detailed breakdown of all execution steps

### Execution Steps

Each execution step contains:

- **toolName**: Name of the tool or agent executed
- **toolInput**: Input parameters or query sent to the tool
- **observation**: Output or response from the tool

The system automatically selects the execution step with the most comprehensive observation as the main response.

## Error Handling

### Client Errors (4xx)

```json
{
  "type": "https://tools.ietf.org/html/rfc7231#section-6.5.1",
  "title": "Bad Request",
  "status": 400,
  "detail": "The Message field is required.",
  "instance": "/api/chat/message"
}
```

### Server Errors (5xx)

```json
{
  "response": "I apologize, but I'm having trouble processing your request right now. Please try again later.",
  "agentName": "",
  "sessionId": 0,
  "timestamp": "2024-01-15T14:30:00Z",
  "success": false,
  "error": "Runtime service timeout",
  "masterAgentThinking": null,
  "agentsUsed": [],
  "toolsUsed": [],
  "executionDetails": {
    "totalSteps": 0,
    "executionSteps": []
  },
  "metadata": {}
}
```

## Rate Limiting

Currently, no rate limiting is implemented. Future implementations may include:

- Per-user message limits
- Session creation limits
- Concurrent request limits

## Pagination

History endpoints use cursor-based pagination:

- **page**: 1-based page number
- **pageSize**: Number of items per page (default: 10, max: 100)
- **totalCount**: Total number of items for calculating page count

## Data Retention

- Chat sessions are preserved indefinitely unless explicitly deleted
- Deleted sessions and their messages are permanently removed
- No soft delete functionality is currently implemented

## Integration Notes

### Agent Runtime Communication

The API communicates with a Python-based Agent Runtime service:

- **Endpoint**: Configured via `AgentRuntime:BaseUrl` setting
- **Protocol**: HTTP/HTTPS with JSON payloads
- **Timeout**: Configurable (default: 5 minutes)
- **Retry Policy**: Basic retry for transient failures

### Database Transactions

- Message sending uses database transactions for consistency
- Failed runtime requests don't save user messages
- Successful responses save both user and agent messages atomically

## WebSocket Support (Future)

Future versions may include WebSocket endpoints for real-time features:

- Live message streaming
- Typing indicators
- Real-time session updates
- Agent status notifications 