# Frontend Chatbot - Technical Specification

This document outlines the technical architecture of the `chatbot-ui` Next.js application.

## 1. Overview

The `chatbot-ui` is a standalone Next.js application that provides a comprehensive user interface for interacting with various Large Language Models (LLMs). It includes its own backend for frontend (BFF) to handle API requests, a database for persistence, and a rich set of UI components for a modern chat experience.

## 2. Tech Stack

- **Framework:** [Next.js](https://nextjs.org/) (App Router)
- **Language:** [TypeScript](https://www.typescriptlang.org/)
- **UI Components:** [React](https://react.dev/), [Shadcn UI](https://ui.shadcn.com/), [Tailwind CSS](https://tailwindcss.com/)
- **State Management:** [React Context API](https://react.dev/learn/passing-data-deeply-with-context) (`ChatbotUIContext`)
- **Database:** [Supabase](https://supabase.com/) (PostgreSQL)
- **API Communication:** `fetch` API, [Vercel AI SDK](https://sdk.vercel.ai/docs) for stream handling.

## 3. Project Structure

The codebase is organized into the following key directories:

- `app/`: Contains the pages and API routes (BFF) of the application, following the Next.js App Router convention.
- `components/`: Reusable React components, with chat-specific components in `components/chat/`.
- `context/`: Holds the main React context (`ChatbotUIContext`) for global state management.
- `db/`: Contains functions for interacting with the Supabase database. Each file corresponds to a database table.
- `lib/`: Utility functions, hooks, and helper scripts.
- `supabase/`: Supabase configuration, migrations, and database types.
- `types/`: TypeScript type definitions used throughout the application.

## 4. Architecture and Data Flow

### 4.1. Frontend Architecture

The frontend is built around a central `ChatUI` component (`components/chat/chat-ui.tsx`) which acts as the main container for the chat interface.

- **State Management:** The `ChatbotUIContext` (`context/context.tsx`) is the single source of truth for the application's state. It provides the rest of the application with access to the current chat messages, user settings, selected model, and more.
- **Core Logic:** The `useChatHandler` custom hook (`components/chat/chat-hooks/use-chat-handler.tsx`) encapsulates the primary business logic for the chat. It handles sending messages, regenerating responses, creating new chats, and managing the chat lifecycle.
- **Component Breakdown:**
  - `ChatInput`: Manages user input, file attachments, and the send button.
  - `ChatMessages`: Renders the list of messages in the current conversation.
  - `Sidebar`: The main navigation component for accessing different chats, assistants, and other resources.

### 4.2. Backend for Frontend (BFF)

The Next.js application includes its own backend within the `app/api/` directory. These API routes are responsible for:

1.  Receiving requests from the frontend UI.
2.  Authenticating the user and checking for API keys.
3.  Proxying the request to the appropriate third-party LLM service (e.g., OpenAI, Anthropic, Google).
4.  Streaming the response from the LLM service back to the UI.

This BFF layer allows the frontend to remain decoupled from the specifics of each LLM provider's API and keeps sensitive API keys off the client-side.

### 4.3. Data Flow: Sending a Message

1.  The user types a message in the `ChatInput` component and clicks send.
2.  The `useChatHandler` hook's `handleSendMessage` function is invoked.
3.  The hook creates temporary messages to update the UI optimistically.
4.  It constructs the final message payload, including the prompt, chat history, and any other context.
5.  If files are attached, it first calls the `/api/retrieval/retrieve` endpoint to get relevant text chunks from the files.
6.  The hook then makes a `fetch` request to the appropriate BFF API route (e.g., `/api/chat/openai`).
7.  The BFF route receives the request, validates it, and then calls the external LLM's API.
8.  The BFF streams the response back to the frontend.
9.  The `useChatHandler` hook processes the stream, updating the assistant's message in the UI in real-time.
10. Once the stream is complete, the hook saves the final user and assistant messages to the Supabase database via functions in the `db/` directory.

## 5. Database Schema

The application uses a Supabase (PostgreSQL) database to store all its data. The schema is defined by the migration files in `supabase/migrations/`. Key tables include:

- `workspaces`
- `chats`
- `messages`
- `users`
- `assistants`
- `files`
- `tools`
- `presets`
- `prompts`

## 6. Discrepancy with Backend Architecture Document

It is important to note that the `chatbot-ui` application, in its current state, **does not** directly communicate with the `AgentPlatform.API` for its core chat functionality. The `backend_architecture.md` document describes a system where a central API handles chat requests. However, the `chatbot-ui` handles chat by calling LLM providers directly through its own BFF.

The `AgentPlatform.API` may be intended for other purposes like agent creation and management, but it is not the endpoint that the `chatbot-ui` uses to send and receive messages. The documentation should be updated to reflect this decoupled architecture. 