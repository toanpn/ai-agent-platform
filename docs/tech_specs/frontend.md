# Technical Specification: Angular Chatbot

This document outlines the technical architecture and development plan for the new Angular-based chatbot application. The application will serve as a lightweight, modern frontend for the `AgentPlatform.API`.

## 1. Guiding Principles

- **Thin Client Architecture:** The frontend will be a "thin client," meaning it will not contain complex business logic. All major operations (chat processing, agent management, document handling) will be delegated to the `AgentPlatform.API`.
- **Backend-Driven:** The application will be a pure consumer of the `AgentPlatform.API`. It will not connect to any third-party LLM services directly.
- **Component-Based:** The UI will be built using Angular, leveraging a modular, component-based architecture.
- **Simplified UX:** Following the business specifications, the UI will be streamlined. Features like Workspaces, direct LLM model selection, and client-side presets/prompts are explicitly excluded to maintain simplicity.
- **Internationalization:** The application supports multiple languages with Vietnamese as the default language, providing a localized user experience.

## 2. Technology Stack

-   **Framework:** Angular 20
-   **Language:** TypeScript
-   **UI Components:**
    -   **Hashbrown:** The primary component library for UI elements (buttons, inputs, cards, etc.).
    -   **Angular Material:** For more complex components like tables or dialogs if not available in Hashbrown.
-   **Styling:** SCSS with Angular Material Design system for consistent theming and component styling.
-   **State Management:** Angular Services with RxJS `BehaviorSubject` for reactive state management.
-   **API Communication:** Angular's `HttpClient` module.
-   **Internationalization:** ngx-translate library for multi-language support.
-   **Testing:** Jasmine and Karma for unit testing.
-   **Code Quality:** ESLint with TypeScript support and Prettier for code formatting.

## 3. Proposed Project Structure

The project will be organized into feature modules to ensure a clean and scalable architecture.

```
/frontend
├── angular.json
├── package.json
├── tsconfig.json
├── tsconfig.app.json
├── tsconfig.spec.json
├── .eslintrc.json
├── .prettierrc
├── public/
├── src/
│   ├── main.ts
│   ├── styles.scss
│   ├── index.html
│   ├── assets/
│   │   └── i18n/
│   │       ├── en.json
│   │       └── vi.json
│   ├── app/
│   │   ├── app.config.ts
│   │   ├── app.routes.ts
│   │   ├── app.ts (component)
│   │   ├── app.html
│   │   ├── app.scss
│   │   │
│   │   ├── core/
│   │   │   ├── guards/
│   │   │   │   └── auth.guard.ts
│   │   │   ├── interceptors/
│   │   │   │   └── auth.interceptor.ts
│   │   │   └── services/
│   │   │       ├── api.service.ts
│   │   │       ├── auth.service.ts
│   │   │       ├── chat.service.ts
│   │   │       ├── agent.service.ts
│   │   │       ├── hashbrown.service.ts
│   │   │       ├── notification.service.ts
│   │   │       ├── storage.service.ts
│   │   │       └── translation.service.ts
│   │   │
│   │   ├── features/
│   │   │   ├── auth/
│   │   │   │   └── login/
│   │   │   │       ├── login.component.ts
│   │   │   │       ├── login.component.html
│   │   │   │       └── login.component.scss
│   │   │   ├── chat/
│   │   │   │   ├── chat-page/
│   │   │   │   │   ├── chat-page.component.ts
│   │   │   │   │   ├── chat-page.component.html
│   │   │   │   │   └── chat-page.component.scss
│   │   │   │   ├── chat-state.service.ts
│   │   │   │   └── components/
│   │   │   │       ├── chat-input/
│   │   │   │       ├── chat-message/
│   │   │   │       ├── chat-messages/
│   │   │   │       └── chat-sidebar/
│   │   │   └── agent-management/
│   │   │       ├── agent-list/
│   │   │       ├── agent-form/
│   │   │       └── agent-detail/
│   │   │
│   │   └── shared/
│   │       ├── components/
│   │       │   └── language-selector/
│   │       │       └── language-selector.component.ts
│   │       ├── models/
│   │       └── pipes/
│   │
│   └── environments/
│       ├── environment.ts
│       └── environment.prod.ts
```

## 4. State Management Strategy

A reactive state management approach using **Angular Services and RxJS** will be employed.

-   **Singleton Services:** Services provided in `root` (e.g., `AuthService`, `ChatService`, `TranslationService`) will hold the application's state.
-   **`BehaviorSubject`:** Each service will use `BehaviorSubject` to store and manage its part of the state (e.g., `currentUser$`, `activeConversation$`, `messages$`, `currentLanguage$`).
-   **Observables:** Components will subscribe to the public `Observable` streams exposed by these services to receive state updates.
-   **Immutability:** State updates will be handled immutably to ensure predictable state transitions.

This approach avoids the boilerplate of more complex libraries like NgRx while providing a robust, scalable, and reactive solution suitable for this application's needs.

## 5. Component Breakdown & Architecture

The application will be broken down into the following key components, aligning with the UI specification.

-   **`LoginComponent`**:
    -   **Responsibility:** Handles user login via a form with localized text and validation messages.
    -   **Interaction:** Calls `AuthService.login()` on form submission. Navigates to the chat view on success.
-   **`ChatSidebarComponent`**:
    -   **Responsibility:** Displays user info, a "New Chat" button, and the list of past conversations with localized labels.
    -   **Interaction:** Subscribes to `ChatService.conversations$` to display history. Calls `ChatService.loadChat(id)` when a conversation is selected or `ChatService.startNewChat()` when the button is clicked.
-   **`ChatViewComponent`**:
    -   **Responsibility:** The main container that orchestrates the chat interface with language selector in the toolbar.
    -   **Interaction:** Subscribes to `ChatService.activeConversation$` and `ChatService.messages$` to display the current chat. Hosts the `ChatMessage` and `ChatInput` components.
-   **`ChatMessageComponent`**:
    -   **Responsibility:** Renders a single message, with distinct styling for user vs. assistant messages and localized sender labels.
    -   **Interaction:** Receives message data via an `@Input()`.
-   **`ChatInputComponent`**:
    -   **Responsibility:** Manages the text input, file attachment button, and send button with localized placeholders and labels.
    -   **Interaction:** Emits a `(sendMessage)` event with the message text and optional `File` object.
-   **`ChatMessagesComponent`**:
    -   **Responsibility:** Displays the list of messages with localized loading indicators.
    -   **Interaction:** Receives messages array and loading state via `@Input()`.
-   **`LanguageSelectorComponent`**:
    -   **Responsibility:** Provides a dropdown for language selection (EN/VI) in the application toolbar.
    -   **Interaction:** Uses `TranslationService` to switch languages and persists the selection.
-   **Agent Management Components** (`AgentListComponent`, `AgentFormComponent`, `AgentDetailComponent`):
    -   **Responsibility:** Handle the CRUD (Create, Read, Update, Delete) operations for Agents with fully localized interface.
    -   **Interaction:** Will use a dedicated `AgentService` to interact with the `/api/agents` endpoints.

## 6. Internationalization (i18n) Strategy

The application implements comprehensive internationalization using the ngx-translate library:

-   **Supported Languages:** Vietnamese (default) and English
-   **Translation Files:** JSON-based translation files located in `src/assets/i18n/`
-   **Language Persistence:** Selected language is stored in localStorage and restored on application restart
-   **Dynamic Switching:** Language can be changed at runtime without page reload
-   **Translation Keys:** Organized by feature (AUTH, CHAT, AGENTS, COMMON, etc.) for maintainability
-   **Service Integration:** `TranslationService` manages language switching and provides reactive language state
-   **Component Integration:** All UI text, validation messages, and error messages are translatable

### Translation Structure
```
{
  "COMMON": { /* Common UI elements */ },
  "AUTH": { /* Authentication related text */ },
  "CHAT": { /* Chat interface text */ },
  "AGENTS": { /* Agent management text */ },
  "FILES": { /* File management text */ },
  "NAVIGATION": { /* Navigation elements */ },
  "VALIDATION": { /* Form validation messages */ },
  "ERRORS": { /* Error messages */ }
}
```

## 7. API Integration and Data Flow

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

## 8. Key Feature Implementation Strategy

-   **Conversation Handling & Message Threading:** Managed by the `ChatService`, which tracks the `activeConversationId` and fetches message history for that ID from the `/api/chat/conversations/{id}` endpoint.
-   **User Authentication:**
    -   JWT-based authentication flow.
    -   Token stored securely in `localStorage` via a `StorageService`.
    -   `AuthGuard` will protect all feature routes (e.g., `/chat`, `/agents`).
-   **Internationalization:**
    -   Vietnamese as the default language with English support.
    -   Language selector in the application toolbar.
    -   All UI text, validation messages, and error messages are translatable.
    -   Language preference persisted across sessions.
-   **Responsive Design:** Angular Flex Layout and Angular Material's responsive utilities will be used to ensure the layout adapts correctly to different screen sizes across desktop and mobile devices.
-   **Integration of Technologies:**
    -   **Angular:** Standalone components will be used for better encapsulation and modern Angular patterns.
    -   **Hashbrown/Angular Material:** HashbrownAI components serve as the primary UI library, with Angular Material providing additional complex components like dialogs and tables.
    -   **SCSS:** Used for component-specific styling with Angular Material's theming system for consistent design patterns.
    -   **TypeScript:** Strict mode enabled for enhanced type safety and code quality.
    -   **ngx-translate:** Provides robust internationalization capabilities with reactive language switching.

This specification provides a comprehensive blueprint for the development team. It aligns with the business requirements for a simplified, backend-driven application while leveraging a modern and scalable Angular architecture with full internationalization support.