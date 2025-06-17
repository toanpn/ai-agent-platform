# Simple Chatbot - Technical Specification

## 1. Overview

This document describes the technical architecture for the new, simplified chatbot UI built with Angular. It is designed to be a lightweight client for the `AgentPlatform.API`, as detailed in the `backend_architecture.md` document.

## 2. Tech Stack

- **Framework:** [Angular](https://angular.io/) (v17+)
- **UI Components:** [Hashbrown](https://www.figma.com/community/file/1138278244017369343) (Assumed Internal Component Library) & [Tailwind CSS](https://tailwindcss.com/)
- **State Management:** Angular Services with RxJS for reactive state.
- **Language:** [TypeScript](https://www.typescriptlang.org/)
- **API Communication:** Angular `HttpClient`.

## 3. Architecture

The application will follow a standard Angular architecture, organized into modules, components, and services.

- **Core Module:** Will provide singleton services like `AuthService` and `ApiService`.
- **Feature Modules:** The application will be split into logical feature modules, primarily `Auth` and `Chat`.
- **Reactive State:** State will be managed within services using RxJS `BehaviorSubject` to hold the current state and `Observable` shashbrown treams to broadcast changes to components.

## 4. Project Structure (Proposed)

```
src/
├── app/
│   ├── modules/
│   │   ├── auth/
│   │   │   ├── components/
│   │   │   │   ├── login/
│   │   │   │   └── register/
│   │   │   └── auth.module.ts
│   │   │
│   │   └── chat/
│   │       ├── components/
│   │       │   ├── chat-input/
│   │       │   ├── chat-message/
│   │       │   ├── chat-sidebar/
│   │       │   └── chat-view/
│   │       ├── services/
│   │       │   └── chat.service.ts
│   │       └── chat.module.ts
│   │
│   ├── core/
│   │   ├── services/
│   │   │   ├── api.service.ts
│   │   │   ├── auth.service.ts
│   │   │   └── storage.service.ts
│   │   ├── guards/
│   │   │   └── auth.guard.ts
│   │   └── core.module.ts
│   │
│   ├── shared/
│   │   └── shared.module.ts
│   │
│   ├── app.component.ts
│   ├── app.config.ts
│   └── app.routes.ts
│
└── assets/
└── environments/
```

## 5. Data Flow and Services

### 5.1. `ApiService`
A central service that wraps Angular's `HttpClient`. It will be responsible for making all HTTP requests to the `AgentPlatform.API`. It will handle adding the auth token to headers and processing base responses.

### 5.2. `AuthService`
- Manages user authentication state (e.g., JWT token, user profile).
- Exposes methods like `login()`, `register()`, `logout()`.
- `login()` will call `POST /api/users/login` via the `ApiService`.
- Stores the JWT in local storage (via a `StorageService`) and keeps user profile information in a `BehaviorSubject`.
- An `AuthGuard` will protect routes that require authentication.

### 5.3. `ChatService`
- Manages the state of chat conversations.
- Holds the current list of conversations and the active chat's messages in `BehaviorSubject`s.
- **`sendMessage(message: string, file?: File)`**:
  1. If a file is provided, it will first call `POST /api/files` to upload the file.
  2. It receives a `fileId` from the response.
  3. It then calls `POST /api/chat` with the message and the `fileId` included in the payload metadata.
  4. It optimistically updates the message list in the UI.
  5. It updates the message list with the final response from the API.
- **`loadConversations()`**: Calls `GET /api/chat/conversations` to populate the chat history sidebar.
- **`loadChat(conversationId: string)`**: Calls `GET /api/chat/conversations/{conversationId}` to load the messages for a specific chat.

## 6. Component Breakdown

- **`LoginComponent`**: A simple form to handle user login.
- **`ChatViewComponent`**: The main container for the chat interface. It will display the message list and the chat input.
- **`ChatSidebarComponent`**: Lists past conversations and allows the user to start a new chat.
- **`ChatInputComponent`**: Contains the text area for typing messages, a send button, and a file upload button. It emits an event with the message and file to the parent `ChatViewComponent`.
- **`ChatMessageComponent`**: Renders a single message, differentiating between user and assistant messages.

All low-level UI elements (buttons, inputs, cards) will be sourced from the **Hashbrown** component library, styled with **Tailwind CSS**. 