# Chat System Technical Specification

## Overview

The Chat System is a core feature of the AI Agent Platform that enables users to interact with AI agents through a conversational interface. The system manages chat sessions, message history, and integrates with the Python-based Agent Runtime to provide intelligent responses with execution details.

## Architecture Components

### 1. Data Models

#### ChatSession
```csharp
public class ChatSession
{
    public int Id { get; set; }
    public int UserId { get; set; }
    public User User { get; set; }
    public string? Title { get; set; }
    public bool IsActive { get; set; } = true;
    public DateTime CreatedAt { get; set; }
    public DateTime? UpdatedAt { get; set; }
    public ICollection<ChatMessage> Messages { get; set; }
}
```

**Purpose**: Represents a conversation session between a user and the agent system.

**Key Features**:
- One-to-many relationship with ChatMessage
- Belongs to a specific User
- Supports session title and active/inactive status
- Automatic timestamping

#### ChatMessage
```csharp
public class ChatMessage
{
    public int Id { get; set; }
    public int ChatSessionId { get; set; }
    public ChatSession ChatSession { get; set; }
    public string Content { get; set; }
    public string Role { get; set; } // "user", "assistant", "system"
    public string? AgentName { get; set; }
    public string? Metadata { get; set; } // JSON for additional data
    public DateTime CreatedAt { get; set; }
}
```

**Purpose**: Represents individual messages within a chat session.

**Key Features**:
- Support for different message roles (user, assistant, system)
- Agent name tracking for multi-agent conversations
- JSON metadata storage for extensibility
- Automatic timestamping

### 2. Data Transfer Objects (DTOs)

#### SendMessageRequestDto
```csharp
public class SendMessageRequestDto
{
    [Required]
    public string Message { get; set; }
    public int? SessionId { get; set; }
    public string? AgentName { get; set; }
}
```

#### ChatResponseDto
```csharp
public class ChatResponseDto
{
    public string Response { get; set; }
    public string AgentName { get; set; }
    public int SessionId { get; set; }
    public DateTime Timestamp { get; set; }
    public bool Success { get; set; }
    public string? Error { get; set; }
    public string? MasterAgentThinking { get; set; }
    
    // Enhanced response fields
    public List<string> AgentsUsed { get; set; }
    public List<string> ToolsUsed { get; set; }
    public ExecutionDetailsDto ExecutionDetails { get; set; }
    public Dictionary<string, object> Metadata { get; set; }
}
```

**Enhanced Features**:
- **Master Agent Thinking**: Captures the master agent's reasoning when execution steps are available
- **Agents Used**: List of all agents involved in processing the request
- **Tools Used**: List of all tools executed during processing
- **Execution Details**: Detailed breakdown of execution steps with tool inputs and observations

### 3. API Endpoints

#### POST /api/chat/message
**Purpose**: Send a message to the agent system and receive an enhanced response.

**Request Body**: `SendMessageRequestDto`
**Response**: `ChatResponseDto`

**Process Flow**:
1. Validate user authentication
2. Get or create chat session
3. Save user message to database
4. Prepare message history for runtime
5. Send request to Agent Runtime via HTTP client
6. Process runtime response with enhanced logic:
   - If execution steps exist, use best observation as main response
   - Treat master agent response as "thinking" when steps are available
   - Use actual agent name from execution steps
7. Save agent response to database
8. Return enhanced response with execution details

#### GET /api/chat/history
**Purpose**: Retrieve paginated chat history for the authenticated user.

**Query Parameters**:
- `page` (default: 1)
- `pageSize` (default: 10)

**Response**: `ChatHistoryDto`

#### GET /api/chat/sessions/{sessionId}
**Purpose**: Retrieve a specific chat session with all messages.

**Response**: `ChatSessionDto`

#### DELETE /api/chat/sessions/{sessionId}
**Purpose**: Delete a specific chat session and all associated messages.

**Response**: 204 No Content (success) or 404 Not Found

### 4. Agent Runtime Integration

#### AgentRuntimeClient
The system communicates with a Python-based Agent Runtime service via HTTP.

**Configuration**:
```json
{
  "AgentRuntime": {
    "BaseUrl": "http://localhost:5001"
  }
}
```

**Request Format** (`AgentRuntimeRequest`):
```csharp
public class AgentRuntimeRequest
{
    public string Message { get; set; }
    public string UserId { get; set; }
    public string? SessionId { get; set; }
    public string? AgentName { get; set; }
    public List<MessageHistory> History { get; set; }
    public Dictionary<string, object> Context { get; set; }
}
```

**Response Processing**:
The client handles mapping between Python backend response format and C# models, including:
- JSON property name mapping (snake_case to PascalCase)
- Large content handling with increased buffer sizes
- Unicode character encoding
- Comprehensive error handling and logging

### 5. Database Schema

```sql
-- ChatSessions Table
CREATE TABLE ChatSessions (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    UserId INT NOT NULL,
    Title NVARCHAR(MAX),
    IsActive BIT NOT NULL DEFAULT 1,
    CreatedAt DATETIME2 NOT NULL DEFAULT GETDATE(),
    UpdatedAt DATETIME2,
    FOREIGN KEY (UserId) REFERENCES Users(Id)
);

-- ChatMessages Table
CREATE TABLE ChatMessages (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    ChatSessionId INT NOT NULL,
    Content NVARCHAR(MAX) NOT NULL,
    Role NVARCHAR(50) NOT NULL,
    AgentName NVARCHAR(MAX),
    Metadata NVARCHAR(MAX),
    CreatedAt DATETIME2 NOT NULL DEFAULT GETDATE(),
    FOREIGN KEY (ChatSessionId) REFERENCES ChatSessions(Id) ON DELETE CASCADE
);
```

**Indexes**:
- Primary keys on Id columns
- Foreign key indexes for performance
- Potential composite index on (UserId, CreatedAt) for history queries

## Advanced Features

### 1. Enhanced Response Processing

The system implements intelligent response processing logic:

```csharp
// If execution steps exist, use best observation as main response
if (runtimeResponse.ExecutionDetails?.ExecutionSteps?.Any() == true)
{
    var bestStep = runtimeResponse.ExecutionDetails.ExecutionSteps
        .Where(s => !string.IsNullOrEmpty(s.Observation))
        .OrderByDescending(s => s.Observation.Length)
        .FirstOrDefault();

    if (bestStep != null)
    {
        masterAgentThinking = runtimeResponse.Response; // Master thinking
        mainResponse = bestStep.Observation; // Best execution result
        agentName = bestStep.ToolName; // Actual executing agent
    }
}
```

### 2. Session Management

**Auto-Creation**: New sessions are automatically created when no sessionId is provided.

**History Tracking**: All messages within a session are sent to the runtime for context.

**Lifecycle Management**: Sessions can be marked as inactive but are preserved for history.

### 3. Error Handling

**Runtime Service Errors**:
- Connection timeouts with configurable thresholds
- HTTP errors with proper status code handling
- JSON parsing errors with fallback responses
- Service unavailability with graceful degradation

**Database Errors**:
- Transaction rollback on failures
- Constraint violation handling
- Connection pool management

## Security Considerations

### 1. Authentication & Authorization
- All endpoints require JWT authentication
- User isolation through userId validation
- Session ownership verification

### 2. Input Validation
- Required field validation on DTOs
- SQL injection prevention through Entity Framework
- Content length limitations

### 3. Data Protection
- Sensitive data is not logged
- Message content is stored securely
- User data isolation

## Performance Considerations

### 1. Database Optimization
- Efficient pagination with OFFSET/FETCH
- Optimized foreign key relationships
- Indexed queries for common operations

### 2. HTTP Client Configuration
- Connection pooling for runtime client
- Timeout configurations
- Retry policies for transient failures

### 3. Memory Management
- Large content handling with streaming
- Efficient JSON serialization settings
- Proper disposal of resources

## Monitoring & Logging

### 1. Structured Logging
```csharp
_logger.LogInformation("Sending request to runtime service at {BaseUrl}", _httpClient.BaseAddress);
_logger.LogInformation("Runtime service responded in {ElapsedMs}ms with status {StatusCode}", 
    stopwatch.ElapsedMilliseconds, response.StatusCode);
```

### 2. Performance Metrics
- Request/response times
- Success/failure rates
- Agent usage statistics
- Tool execution metrics

### 3. Error Tracking
- Exception logging with context
- Runtime service error correlation
- User impact assessment

## Future Enhancements

### 1. Real-time Features
- WebSocket support for live updates
- Message streaming for long responses
- Typing indicators

### 2. Advanced Analytics
- Conversation analytics
- Agent performance metrics
- User engagement tracking

### 3. Scalability Improvements
- Message storage optimization
- Caching strategies
- Horizontal scaling support

## Dependencies

### Core Dependencies
- Microsoft.EntityFrameworkCore
- AutoMapper
- Microsoft.AspNetCore.Authorization
- System.Text.Json

### External Services
- Agent Runtime Service (Python FastAPI)
- SQL Server Database
- JWT Authentication Service

## Configuration

### Required Environment Variables
```json
{
  "ConnectionStrings": {
    "DefaultConnection": "Server=...;Database=AgentPlatform;..."
  },
  "AgentRuntime": {
    "BaseUrl": "http://localhost:5001"
  },
  "Jwt": {
    "Key": "...",
    "Issuer": "...",
    "Audience": "..."
  }
}
```

### HTTP Client Configuration
```csharp
services.AddHttpClient<IAgentRuntimeClient, AgentRuntimeClient>(client =>
{
    client.Timeout = TimeSpan.FromMinutes(5);
    client.DefaultRequestHeaders.Add("Accept", "application/json");
});
``` 