# Frontend-Backend Integration Technical Specification

## 1. Overview

This document provides a detailed technical specification for the integration between the `frontend` (Angular) application and the `AgentPlatform.API` backend. It outlines the API endpoints, data models, and communication flows required to connect the two systems. This specification is based on the analysis of `backend_architecture.md`, `angular_chatbot_tech_spec.md`, and the backend source code.

## 2. Target Audience

This document is intended for frontend and backend developers who are responsible for implementing the integration between the `frontend` Angular application and the `AgentPlatform.API`.

## 3. Core Architectural Principles

- **Client-Server Model**: The `frontend` Angular application acts as the client, making HTTP requests to the `AgentPlatform.API` server.
- **Stateless Authentication**: Authentication is handled via JSON Web Tokens (JWT), which are sent with each API request.
- **RESTful API**: The `AgentPlatform.API` exposes a set of RESTful endpoints for resource management.

## 4. Authentication Flow

1.  **User Login**: The user enters their credentials into the `LoginComponent` on the frontend.
2.  **API Request**: The frontend sends a `POST` request to `/api/auth/login` with the user's email and password in the request body.
3.  **Token Issuance**: Upon successful authentication, the backend returns a JWT to the frontend.
4.  **Token Storage**: The frontend stores the JWT in `localStorage`.
5.  **Authenticated Requests**: For all subsequent requests to protected endpoints, the frontend includes the JWT in the `Authorization` header as a `Bearer` token.

## 5. API Endpoint Specification

### 5.1. Authentication

-   **Endpoint**: `POST /api/auth/login`
-   **Description**: Authenticates a user and returns a JWT.
-   **Request Body**:
    ```json
    {
      "email": "user@example.com",
      "password": "your-password"
    }
    ```
-   **Success Response (200 OK)**:
    ```json
    {
      "token": "your-jwt-token",
      "userId": "user-id"
    }
    ```
-   **Error Response (401 Unauthorized)**:
    ```json
    {
      "message": "Invalid email or password"
    }
    ```

-   **Endpoint**: `POST /api/auth/register`
-   **Description**: Registers a new user.
-   **Request Body**:
    ```json
    {
      "email": "user@example.com",
      "password": "your-password",
      "name": "User Name"
    }
    ```
-   **Success Response (201 Created)**:
    ```json
    {
      "token": "your-jwt-token",
      "userId": "user-id"
    }
    ```

### 5.2. Chat

-   **Endpoint**: `POST /api/chat`
-   **Description**: Sends a message to a chat conversation.
-   **Request Body**:
    ```json
    {
      "message": "Hello, agent!",
      "conversationId": "existing-conversation-id", // Optional
      "agentIds": ["agent-id-1"],
      "metadata": {
        "fileId": "uploaded-file-id" // Optional
      }
    }
    ```
-   **Success Response (200 OK)**:
    ```json
    {
      "messageId": "new-message-id",
      "response": "This is the agent's response."
    }
    ```

-   **Endpoint**: `GET /api/chat/conversations`
-   **Description**: Retrieves a paginated list of the user's conversations.

-   **Endpoint**: `GET /api/chat/conversations/{conversationId}`
-   **Description**: Retrieves the details and messages of a specific conversation.

-   **Endpoint**: `DELETE /api/chat/conversations/{conversationId}`
-   **Description**: Deletes a conversation.

### 5.3. Agents

-   **Endpoint**: `GET /api/agents`
-   **Description**: Retrieves a list of available agents.

-   **Endpoint**: `GET /api/agents/{agentId}`
-   **Description**: Retrieves the details of a specific agent.

-   **Endpoint**: `POST /api/agents`
-   **Description**: Creates a new agent.

-   **Endpoint**: `PUT /api/agents/{agentId}`
-   **Description**: Updates an existing agent.

-   **Endpoint**: `DELETE /api/agents/{agentId}`
-   **Description**: Deletes an agent.

### 5.4. Files

-   **Endpoint**: `POST /api/files`
-   **Description**: Uploads a file for use by agents. The request should be `multipart/form-data`.

-   **Endpoint**: `GET /api/files`
-   **Description**: Retrieves a list of uploaded files.

-   **Endpoint**: `GET /api/files/{fileId}`
-   **Description**: Retrieves the details of a specific file.

-   **Endpoint**: `DELETE /api/files/{fileId}`
-   **Description**: Deletes a file.

## 6. Frontend Implementation Guide

This section provides guidance on where and how the API calls should be implemented within the `frontend` Angular application, based on its existing architecture.

### 6.1. Authentication (`/api/auth`)

-   **Service**: `AuthService` (`src/app/services/auth.service.ts`)
-   **Components**:
    -   `LoginComponent` (`src/app/auth/login/login.component.ts`)
-   **Implementation Details**:
    -   The `LoginComponent` will inject the `AuthService` and call its `login()` or `register()` methods.
    -   The `AuthService` will be responsible for making the HTTP `POST` requests to `/api/auth/login` and `/api/auth/register`.
    -   Upon receiving a successful response, the `AuthService` will store the JWT in `localStorage` and update the application's authentication state.
    -   The `AuthInterceptor` (`src/app/interceptors/auth-interceptor.ts`) will automatically attach the stored token to all subsequent API requests.

### 6.2. Chat (`/api/chat`)

-   **Service**: `ChatService` (`src/app/services/chat.service.ts`)
-   **Components**:
    -   `ChatViewComponent` (`src/app/chat/chat-view/chat-view.component.ts`)
    -   `ChatInputComponent` (`src/app/chat/chat-input/chat-input.component.ts`)
    -   `ChatSidebarComponent` (`src/app/chat/chat-sidebar/chat-sidebar.component.ts`)
-   **Implementation Details**:
    -   When a user sends a message from the `ChatInputComponent`, it will notify the parent `ChatViewComponent`.
    -   The `ChatViewComponent` will call the `sendMessage()` method in the `ChatService`.
    -   The `ChatService` will handle the `POST /api/chat` request.
    -   The `ChatSidebarComponent` will call `loadConversations()` in the `ChatService` (which calls `GET /api/chat/conversations`) to display the user's chat history.
    -   When a user clicks on a conversation in the sidebar, the `ChatService`'s `loadChat()` method will be called to fetch the message history using `GET /api/chat/conversations/{conversationId}`.

### 6.3. Agents (`/api/agents`)

-   **Service**: `AgentService` (`src/app/services/agent.service.ts`)
-   **Components**:
    -   `AgentListComponent` (`src/app/agents/agent-list/agent-list.component.ts`)
    -   `AgentFormComponent` (`src/app/agents/agent-form/agent-form.component.ts`)
    -   `AgentDetailComponent` (`src/app/agents/agent-detail/agent-detail.component.ts`)
-   **Implementation Details**:
    -   The `AgentListComponent` will use the `AgentService` to fetch the list of all agents (`GET /api/agents`).
    -   The `AgentFormComponent` will use the `AgentService` to create (`POST /api/agents`) or update (`PUT /api/agents/{agentId}`) an agent.
    -   The `AgentDetailComponent` will use the `AgentService` to fetch details for a single agent (`GET /api/agents/{agentId}`) and to delete an agent (`DELETE /api/agents/{agentId}`).

### 6.4. Files (`/api/files`)

-   **Service**: `FileService` (A new service, `src/app/services/file.service.ts`, should be created for this purpose).
-   **Components**:
    -   `ChatInputComponent` or a dedicated file management component.
-   **Implementation Details**:
    -   When a user attaches a file in the `ChatInputComponent`, the component will call a method in the `FileService`.
    -   The `FileService` will handle the `multipart/form-data` `POST /api/files` request to upload the file.
    -   The `fileId` returned from the upload will then be passed to the `ChatService`'s `sendMessage` method to be included in the chat message metadata.
    -   A dedicated file management component could use the `FileService` to list (`GET /api/files`) and delete (`DELETE /api/files/{fileId}`) files.

## 7. Data Models

### `User`
```typescript
interface User {
  id: string;
  email: string;
  name: string;
}
```

### `Conversation`
```typescript
interface Conversation {
  id: string;
  messages: Message[];
  metadata: object;
  agents: string[];
}
```

### `Message`
```typescript
interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}
```

### `Agent`
```typescript
interface Agent {
  id: string;
  name: string;
  description: string;
  capabilities: string[];
}
```

### `File`
```typescript
interface File {
  id: string;
  filename: string;
  url: string;
  metadata: object;
}
```

## 8. Error Handling

The frontend should be prepared to handle standard HTTP error codes from the API:
-   `400 Bad Request`: The request was malformed (e.g., missing required fields).
-   `401 Unauthorized`: The user is not authenticated, or the JWT is invalid/expired.
-   `403 Forbidden`: The user is not authorized to perform the requested action.
-   `404 Not Found`: The requested resource could not be found.
-   `500 Internal Server Error`: An unexpected error occurred on the backend.

The frontend should display appropriate user-friendly messages for each error case.

## 9. Future Considerations

-   **User Profile Management**: The endpoints `GET /api/users/me` and `PUT /api/users/me` are documented but not yet implemented. This specification should be updated once these features are available.
-   **Real-time Communication**: For a more responsive chat experience, the integration could be enhanced to use WebSockets or Server-Sent Events (SSE) for real-time message delivery. 