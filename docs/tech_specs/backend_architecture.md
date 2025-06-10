# AI Agent Platform - Backend Architecture (MVP)

## Overview

This document outlines the backend architecture for the MVP version of the AI Agent Platform using Google ADK, with a focus on clarity and minimal service separation.

## Services Breakdown

### 1. AgentPlatform.API

**Role:**

* Acts as the main entry point for frontend requests
* Handles authentication, request validation, and logging
* Routes messages to AgentRuntime
* Stores conversation history, files, and user-agent metadata

**Endpoints:**

#### Chat API
* `POST /api/chat`: Send a message to the agent system
  * Request: `{ message: string, conversationId?: string, agentIds: string[], metadata?: object }`
  * Response: `{ messageId: string, response: string, actions?: Action[], metadata?: object }`

* `GET /api/chat/conversations`: Get user's conversation history
  * Query params: `limit`, `offset`, `sortBy`
  * Response: `{ conversations: Conversation[], total: number }`

* `GET /api/chat/conversations/{conversationId}`: Get a specific conversation
  * Response: `{ id: string, messages: Message[], metadata: object, agents: string[] }`

* `DELETE /api/chat/conversations/{conversationId}`: Delete a conversation
  * Response: `{ success: boolean }`

#### Agent API
* `GET /api/agents`: Retrieve list of available agents
  * Query params: `category`, `limit`, `offset`
  * Response: `{ agents: Agent[], total: number }`

* `GET /api/agents/{agentId}`: Get agent details
  * Response: `{ id: string, name: string, description: string, capabilities: string[], metadata: object }`

* `POST /api/agents`: Create a new agent
  * Request: `{ name: string, description: string, capabilities: string[], config: object }`
  * Response: `{ id: string, name: string, success: boolean }`

* `PUT /api/agents/{agentId}`: Update an agent
  * Request: `{ name?: string, description?: string, capabilities?: string[], config?: object }`
  * Response: `{ success: boolean }`

* `DELETE /api/agents/{agentId}`: Delete an agent
  * Response: `{ success: boolean }`

#### File API
* `POST /api/files`: Upload documents for agent use
  * Request: `multipart/form-data` with file and metadata
  * Response: `{ fileId: string, filename: string, url: string, metadata: object }`

* `GET /api/files`: Get list of uploaded files
  * Query params: `limit`, `offset`, `type`
  * Response: `{ files: File[], total: number }`

* `GET /api/files/{fileId}`: Get file details
  * Response: `{ id: string, filename: string, url: string, metadata: object }`

* `DELETE /api/files/{fileId}`: Delete a file
  * Response: `{ success: boolean }`

#### User API
* `POST /api/users/register`: Register a new user
  * Request: `{ email: string, password: string, name: string }`
  * Response: `{ userId: string, success: boolean }`

* `POST /api/users/login`: Login a user
  * Request: `{ email: string, password: string }`
  * Response: `{ token: string, userId: string }`

* `GET /api/users/me`: Get current user profile
  * Response: `{ id: string, email: string, name: string, preferences: object }`

* `PUT /api/users/me`: Update user profile
  * Request: `{ name?: string, preferences?: object }`
  * Response: `{ success: boolean }`

**Implementation Details:**

* Built with ASP.NET Core 7+
* JWT authentication
* Rate limiting middleware
* Logging with Serilog
* API versioning
* Swagger documentation
* Input validation using FluentValidation

---

### 2. AgentRuntime

**Role:**

* Acts as a middleware between AgentPlatform.API and Google ADK
* Encapsulates all logic related to communicating with ADK
* Manages Agent Master logic and delegates to child agents as needed

**Core Components:**

* **MessageProcessor**: Handles incoming messages, adds context, and prepares for ADK
* **AgentSelector**: Determines which agents to involve based on message content
* **ContextManager**: Manages conversation context, history, and agent memory
* **ADKClient**: Client library for communicating with Google ADK
* **ResponseFormatter**: Processes and formats responses from ADK

**Implementation Details:**

* Built with .NET 7+
* Dependency injection pattern
* Async processing queue for handling multiple requests
* Circuit breaker pattern for ADK communication
* In-memory caching for frequently accessed data
* Extensible plugin architecture for custom processors

---

### 3. Google ADK

**Role:**

* Hosts and executes the multi-agent logic
* Handles reasoning, memory, and individual agent behaviors

**Integration Points:**

* **REST API**: Primary integration method for the AgentRuntime
  * `POST /v1/agents/{agentId}/chat`: Send message to a specific agent
  * `POST /v1/agents/master/chat`: Send message to master agent for delegation
  * `GET /v1/agents/{agentId}/capabilities`: Get agent capabilities
  * `GET /v1/agents/{agentId}/memory`: Retrieve agent memory (if supported)

* **Streaming**: Support for real-time response streaming
  * WebSocket endpoint for continuous communication
  * SSE (Server-Sent Events) for one-way streaming

**Implementation Details:**

* Google ADK configuration
* Custom prompts and agent definitions
* Memory and context management
* Integration with external knowledge bases

---

## Optional Supporting Components

### Database (PostgreSQL / MongoDB)

* Store conversation history, uploaded documents, and agent metadata
* Schema includes:
  * Users: user profiles and authentication
  * Conversations: chat history and metadata
  * Messages: individual messages within conversations
  * Agents: agent definitions and configurations
  * Files: uploaded document metadata and references

### Caching Layer (Redis)

* Session caching
* Frequently accessed agent information
* Rate limiting counters

### File Storage (AWS S3 / Azure Blob Storage)

* Document storage for agent knowledge base
* User uploaded files
* Conversation attachments

---

## Request Flow Diagram

```plaintext
[User / UI]
    |
    v
[AgentPlatform.API]
    - Xác thực request
    - Ghi log, lưu lịch sử
    - Gửi message → AgentRuntime
    |
    v
[AgentRuntime]
    - Xử lý context
    - Gửi message → Google ADK Agent Master
         |
         +---> Master gọi agent con (VD: hr-bot, it-bot)
         |
    - Nhận phản hồi từ ADK
    |
    v
[AgentPlatform.API]
    - Trả kết quả về UI
```

---

## Services Diagram

```plaintext
             +--------------------------+
             |     Frontend UI         |
             |  (Chat Interface)       |
             +-----------+-------------+
                         |
                         v
             +--------------------------+
             | AgentPlatform.API        |
             | - REST API (chat, agent)|
             | - Session, log, files   |
             | - Auth & rate limit     |
             +-----------+-------------+
                         |
                         v
             +--------------------------+
             | AgentRuntime             |
             | - Giao tiếp với Google ADK|
             | - Logic Agent Master     |
             | - Gọi các Agent con      |
             +-----------+-------------+
                         |
                         v
             +--------------------------+
             | Google ADK               |
             | - Multi-Agent runtime    |
             | - Code logic mỗi agent   |
             +--------------------------+
```

---

## Sample Chat Request Flow

### Example Request

```http
POST /api/chat
{
  "message": "Tôi muốn xin nghỉ phép",
  "conversationId": "conv-12345",
  "agentIds": ["hr-bot"],
  "metadata": {
    "userId": "user-789",
    "locale": "vi-VN"
  }
}
```

### Example Response

```http
200 OK
{
  "messageId": "msg-6789",
  "response": "Tôi có thể giúp bạn xin nghỉ phép. Bạn muốn nghỉ vào ngày nào và bao nhiêu ngày?",
  "actions": [
    {
      "type": "datePicker",
      "id": "leave-date",
      "label": "Chọn ngày nghỉ"
    },
    {
      "type": "numericInput",
      "id": "leave-duration",
      "label": "Số ngày nghỉ"
    }
  ],
  "metadata": {
    "agentId": "hr-bot",
    "confidence": 0.95
  }
}
```

### Sequence:

1. `AgentPlatform.API` receives and logs the request
2. API calls `AgentRuntime` with message + agent info
3. Runtime invokes Google ADK Master agent
4. ADK delegates to `hr-bot`, processes the request
5. Response flows back: ADK → Runtime → API → UI

---

## Deployment Architecture

### Development Environment
* Local Docker containers
* Mock ADK service
* SQLite for database

### Staging Environment
* Azure App Service
* Managed PostgreSQL
* Azure Blob Storage
* Integration with ADK staging instance

### Production Environment
* Azure Kubernetes Service (AKS)
* Azure Database for PostgreSQL
* Azure Redis Cache
* Azure Blob Storage
* Azure API Management
* Azure Application Insights
* Production ADK instance

---

## Summary

This architecture provides a scalable foundation, balancing simplicity for MVP delivery with the ability to evolve into a multi-service platform. The detailed API design and implementation specifications ensure clear integration points and development guidelines.
