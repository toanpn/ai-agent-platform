# Angular Chatbot - Technical Specification

This document outlines the technical architecture of the `chatbot-ui-ng` Angular application.

## 1. Overview

The `chatbot-ui-ng` is a standalone Angular application that provides a user interface for interacting with the Agent Platform API. It is built with a modern component-based architecture, includes services for API communication, and implements key features for chat and agent management.

## 2. Tech Stack

- **Framework:** [Angular](https://angular.dev/)
- **Language:** [TypeScript](https://www.typescriptlang.org/)
- **UI:** [Tailwind CSS](https://tailwindcss.com/)
- **AI/Chat Components:** [Hashbrown AI](https://hashbrown.dev/)
- **API Communication:** Angular `HttpClient`
- **Routing:** Angular Router
- **Forms:** Angular Reactive Forms

## 3. Project Structure

The codebase for `chatbot-ui-ng` is organized into the following key directories:

- `src/app/`: The root application folder.
  - `agents/`: Contains components related to agent management (`agent-list`, `agent-form`, `agent-detail`).
  - `auth/`: Contains components for authentication (`login`).
  - `chat/`: Contains components for the main chat interface (`chat-view`, `chat-sidebar`, `chat-message`, `chat-input`).
  - `guards/`: Contains route guards, such as `auth-guard`.
  - `interceptors/`: Contains HTTP interceptors, such as the `auth-interceptor`.
  - `services/`: Contains injectable services for handling API calls (`auth.service`, `chat.service`, `agent.service`).
  - `types/`: Contains TypeScript interface definitions for data models (`auth.d.ts`, `chat.d.ts`, `agent.d.ts`).
- `src/environments/`: Contains environment-specific configuration, such as API URLs.

## 4. Architecture and Features

### 4.1. Authentication

- **Login Flow:** The `LoginComponent` captures user credentials and uses the `AuthService` to call the `/api/auth/login` endpoint.
- **Token Handling:** Upon successful login, a JWT is stored in `localStorage`.
- **Request Interception:** The `AuthInterceptor` automatically attaches the JWT as a `Bearer` token to the `Authorization` header of all outgoing HTTP requests.
- **Route Protection:** The `AuthGuard` prevents unauthenticated users from accessing protected routes (e.g., `/chat`, `/agents`).

### 4.2. Chat Interface

- **Chat View:** The `ChatViewComponent` is the main container for the chat interface. It fetches chat history and orchestrates communication between the message list and the input area.
- **Services:** The `ChatService` handles all communication with the `/api/chat` backend endpoints, including sending messages and fetching history.
- **Components:**
  - `ChatSidebarComponent`: Displays navigation and conversation history.
  - `ChatMessageComponent`: Renders individual messages.
  - `ChatInputComponent`: Manages user input for sending new messages.

### 4.3. Agent Management

- **Agent List:** The `AgentListComponent` displays a table of all available agents, fetched via the `AgentService`. It includes loading and error states.
- **Agent Form:** The `AgentFormComponent` is used for both creating and editing agents. It uses Angular's Reactive Forms for data entry and validation.
- **Agent Detail:** The `AgentDetailComponent` displays the complete information for a single agent and includes a confirmation dialog before deletion.
- **Routing:** The module features routes for `/agents`, `/agents/new`, `/agents/:id`, and `/agents/:id/edit`.

### 4.4. Configuration

- **Proxy:** A `proxy.conf.json` file is used during development to proxy requests from `/api` to the backend server (e.g., `http://localhost:5000`), avoiding CORS issues.
- **Environment Variables:** The base URL for the backend API is stored in the `src/environments` folder, allowing for different URLs for development and production builds. 