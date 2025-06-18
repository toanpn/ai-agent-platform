# Technical Specification: Angular Chatbot

This document outlines the technical architecture and development plan for the new Angular-based chatbot application. The application will serve as a lightweight, modern frontend for the `AgentPlatform.API`.

## 1. Guiding Principles

- **Thin Client Architecture:** The frontend will be a "thin client," meaning it will not contain complex business logic. All major operations (chat processing, agent management, document handling) will be delegated to the `AgentPlatform.API`.
- **Backend-Driven:** The application will be a pure consumer of the `AgentPlatform.API`. It will not connect to any third-party LLM services directly.
- **Component-Based:** The UI will be built using Angular, leveraging a modular, component-based architecture.
- **Simplified UX:** Following the business specifications, the UI will be streamlined. Features like Workspaces, direct LLM model selection, and client-side presets/prompts are explicitly excluded to maintain simplicity.

## 2. Technology Stack

-   **Framework:** Angular 20
-   **Language:** TypeScript
-   **UI Components:**
    -   **Hashbrown:** The primary component library for UI elements (buttons, inputs, cards, etc.).
    -   **Angular Material:** For more complex components like tables or dialogs if not available in Hashbrown.
-   **Styling:** Tailwind CSS for utility-first styling, with SCSS for component-level style organization.
-   **State Management:** Angular Services with RxJS `BehaviorSubject` for reactive state management.
-   **API Communication:** Angular's `HttpClient` module.

## 3. Proposed Project Structure

The project will be organized into feature modules to ensure a clean and scalable architecture.

```
/chatbot
├── angular.json
├── package.json
├── tailwind.config.js
├── tsconfig.json
├── src/
│   ├── main.ts
│   ├── styles.scss
│   ├── index.html
│   ├── app/
│   │   ├── app.config.ts
│   │   ├── app.routes.ts
│   │   ├── app.component.ts
│   │   │
│   │   ├── core/
│   │   │   ├── guards/
│   │   │   │   └── auth.guard.ts
│   │   │   ├── interceptors/
│   │   │   │   └── auth.interceptor.ts
│   │   │   └── services/
│   │   │       ├── api.service.ts
│   │   │       ├── auth.service.ts
│   │   │       └── storage.service.ts
│   │   │
│   │   ├── features/
│   │   │   ├── auth/
│   │   │   │   └── login/
│   │   │   │       └── login.component.ts
│   │   │   ├── chat/
│   │   │   │   ├── components/
│   │   │   │   │   ├── chat-input/
│   │   │   │   │   ├── chat-message/
│   │   │   │   │   └── chat-sidebar/
│   │   │   │   └── chat-view/
│   │   │   │       └── chat-view.component.ts
│   │   │   └── agent-management/
│   │   │       ├── agent-list/
│   │   │       ├── agent-form/
│   │   │       └── agent-detail/
│   │   │
│   │   └── shared/
│   │       ├── components/  (e.g., loading spinner, confirm dialog)
│   │       ├── models/       (TypeScript interfaces for API objects)
│   │       └── pipes/
│   │
│   └── environments/
│       ├── environment.ts
│       └── environment.prod.ts
```

## 4. State Management Strategy

A reactive state management approach using **Angular Services and RxJS** will be employed.

-   **Singleton Services:** Services provided in `root` (e.g., `AuthService`, `ChatService`) will hold the application's state.
-   **`BehaviorSubject`:** Each service will use `BehaviorSubject` to store and manage its part of the state (e.g., `currentUser$`, `activeConversation$`, `messages$`).
-   **Observables:** Components will subscribe to the public `Observable` streams exposed by these services to receive state updates.
-   **Immutability:** State updates will be handled immutably to ensure predictable state transitions.

This approach avoids the boilerplate of more complex libraries like NgRx while providing a robust, scalable, and reactive solution suitable for this application's needs.

## 5. Component Breakdown & Architecture

The application will be broken down into the following key components, aligning with the UI specification.

-   **`LoginComponent`**:
    -   **Responsibility:** Handles user login via a form.
    -   **Interaction:** Calls `AuthService.login()` on form submission. Navigates to the chat view on success.
-   **`ChatSidebarComponent`**:
    -   **Responsibility:** Displays user info, a "New Chat" button, and the list of past conversations.
    -   **Interaction:** Subscribes to `ChatService.conversations$` to display history. Calls `ChatService.loadChat(id)` when a conversation is selected or `ChatService.startNewChat()` when the button is clicked.
-   **`ChatViewComponent`**:
    -   **Responsibility:** The main container that orchestrates the chat interface.
    -   **Interaction:** Subscribes to `ChatService.activeConversation$` and `ChatService.messages$` to display the current chat. Hosts the `ChatMessage` and `ChatInput` components.
-   **`ChatMessageComponent`**:
    -   **Responsibility:** Renders a single message, with distinct styling for user vs. assistant messages.
    -   **Interaction:** Receives message data via an `@Input()`.
-   **`ChatInputComponent`**:
    -   **Responsibility:** Manages the text input, file attachment button, and send button.
    -   **Interaction:** Emits a `(sendMessage)` event with the message text and optional `File` object.
-   **Agent Management Components** (`AgentListComponent`, `AgentFormComponent`, `AgentDetailComponent`):
    -   **Responsibility:** Handle the CRUD (Create, Read, Update, Delete) operations for Agents as detailed in the UI spec.
    -   **Interaction:** Will use a dedicated `AgentService` to interact with the `/api/agents` endpoints.

## 6. API Integration and Data Flow

All communication with the backend will be centralized through the `AgentPlatform.API`.

-   **`ApiService`**: A core wrapper around `HttpClient`. It will be responsible for setting base URLs and standard headers.
-   **`AuthInterceptor`**: An `HttpInterceptor` that automatically attaches the JWT Bearer token from `AuthService` to all outgoing requests to the API.
-   **`AuthService`**: Manages all authentication-related API calls (`/api/users/login`, `/api/users/me`).
-   **`ChatService`**: Handles all chat-related API calls (`/api/chat/...`, `/api/files`).

### Data Flow Example: Sending a Message

1.  **User Action:** User types "Hello" in `ChatInputComponent` and clicks "Send".
2.  **Component Event:** `ChatInputComponent` emits a `(sendMessage)` event with the string "Hello".
3.  **View Orchestration:** The parent `ChatViewComponent` catches the event and calls `ChatService.sendMessage("Hello")`.
4.  **Service Logic (`ChatService`):**
    a. An optimistic message object `{ text: "Hello", sender: "user" }` is added to the `messages$` stream to instantly update the UI.
    b. The service calls `ApiService.post('/api/chat', { message: "Hello", conversationId: ... })`.
5.  **API Interaction (`ApiService` & `AuthInterceptor`):** The request is sent with the `Authorization` header attached.
6.  **Response Handling:**
    a. The `ChatService` receives the final response from the API.
    b. It updates the `messages$` stream with the official response from the backend, replacing the optimistic message with the saved one and adding the assistant's reply.

## 7. Key Feature Implementation Strategy

-   **Conversation Handling & Message Threading:** Managed by the `ChatService`, which tracks the `activeConversationId` and fetches message history for that ID from the `/api/chat/conversations/{id}` endpoint.
-   **User Authentication:**
    -   JWT-based authentication flow.
    -   Token stored securely in `localStorage` via a `StorageService`.
    -   `AuthGuard` will protect all feature routes (e.g., `/chat`, `/agents`).
-   **Responsive Design:** Tailwind CSS's responsive breakpoint utilities (`sm:`, `md:`, `lg:`) will be used to ensure the layout adapts correctly to different screen sizes, matching the experience of the `chatbot-ui-ng` implementation.
-   **Integration of Technologies:**
    -   **Angular:** Standalone components will be used for better encapsulation.
    -   **Hashbrown/Angular Material:** Components will be imported into a `SharedModule` and reused throughout the application.
    -   **Tailwind CSS:** Integrated into the build process via PostCSS as is standard for Angular projects.
    -   **SCSS:** Will be used for component-specific styles that are more complex than utility classes can handle, scoped to each component.

This specification provides a comprehensive blueprint for the development team. It aligns with the business requirements for a simplified, backend-driven application while leveraging a modern and scalable Angular architecture.