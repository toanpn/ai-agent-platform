# Chat Session Summary - Technical Specification

## 1. Introduction

This document outlines the technical implementation details for the automatic chat session summarization feature. This feature will generate a concise summary for each chat session to be used as its title, improving user navigation and context awareness.

## 2. Architecture Overview

The implementation will span across the backend API (`AgentPlatform.API`) and the Python-based agent core (`AgentPlatform.Core`). The frontend will require minimal changes to display the updated session titles.

1.  **Client-Side (Angular)**: The chat interface sends messages to the backend as usual. The `ChatSidebarComponent` will display the session title provided by the backend.
2.  **Backend API (.NET)**: The `ChatController` receives the new message. The `ChatService` saves the message and checks if the session needs summarization (i.e., if the message count is a multiple of 5).
3.  **Summarization Service (Python)**: If summarization is needed, the .NET `ChatService` calls a new endpoint on the Python `AgentPlatform.Core` service, passing the recent conversation history.
4.  **Database**: The Python service returns a generated summary, which the .NET service saves to the `ChatSession` table in the database.
5.  **UI Update**: The updated session information, including the new title, is communicated back to the client.

## 3. Detailed Implementation

### 3.1. Python Backend (`AgentPlatform.Core`)

*   **New Endpoint:** A new endpoint `/v1/chat/summarize` will be created in `api_server.py`.
    *   **Method:** `POST`
    *   **Request Body:**
        ```json
        {
          "messages": [
            {"role": "user", "content": "Hello there"},
            {"role": "assistant", "content": "Hi! How can I help you?"}
          ]
        }
        ```
    *   **Response Body:**
        ```json
        {
          "summary": "Initial Greeting"
        }
        ```
*   **Summarization Logic:**
    *   A new function will be added, likely in `core/master_agent.py` or a new dedicated summarization module.
    *   This function will receive the list of messages.
    *   It will construct a specific prompt for the underlying language model.
        *   **Prompt Example:** `Based on the following conversation, create a short, descriptive title of 5 words or less. Do not use quotes. \n\n<conversation history>`
    *   It will invoke the LLM to get the summary and return it.

### 3.2. .NET Backend (`AgentPlatform.API`)

*   **`ChatSession` Model (`Models/ChatSession.cs`):**
    *   A new property `Title` will be added to the `ChatSession` model.
        ```csharp
        public string Title { get; set; }
        ```
    *   A migration will be needed to update the database schema.
*   **`ChatService` (`Services/ChatService.cs`):**
    *   The `AddMessageToSessionAsync` method will be updated.
    *   After saving a new message, it will get the count of messages in the current session.
    *   If `messageCount % 5 == 0`, it will trigger the summarization logic.
    *   It will call the new `/v1/chat/summarize` endpoint on the Python service. An `IAgentRuntimeClient` method will be added for this.
    *   Upon receiving the summary, it will update the `Title` of the `ChatSession` in the database.
*   **`AgentRuntimeClient` (`Services/AgentRuntimeClient.cs`):**
    *   A new method `GetSessionSummaryAsync` will be implemented to call the Python summarization endpoint.
*   **DTOs (`DTOs/ChatDTOs.cs`):**
    *   The `ChatSessionDto` will be updated to include the `Title` property, so it's sent to the frontend.

### 3.3. Frontend (Angular)

*   **`ChatSession` Model (`shared/models/`):**
    *   The `ChatSession` interface will be updated to include the optional `title` property.
*   **`chat-sidebar.component.html`:**
    *   The template will be modified to display `session.title` if it exists. If not, it will fall back to the default naming convention (e.g., "Session <index>").
        ```html
        <span>{{ session.title || 'Session ' + (i + 1) }}</span>
        ```
*   **`chat-state.service.ts`:**
    *   This service manages the state of chat sessions. When a message is sent, the service will eventually receive the updated session list from the backend (or the specific updated session) and the UI will update reactively. No major logic changes are anticipated here, as it should already be designed to handle updates to session data.

## 4. Database Changes

*   A new column `Title` of type `string` (e.g., `NVARCHAR(255)`) will be added to the `ChatSessions` table.
*   A new database migration will be created to apply this change. 