# Chat UX Specification

This document outlines the user experience for the chat page, focusing on the initial state for new conversations. This design is inspired by the UX from t3.chat.

## New Chat Screen

When a user starts a new chat, instead of an empty screen, they will be presented with a helpful welcome screen to guide them.

**Visibility**: This welcome screen will only be shown for conversations that have no messages. As soon as the user sends a message, it will be replaced by the chat message history.

The welcome screen will contain:

1.  **Welcome Message**: A prominent heading with a title like "How can I help you today?".
2.  **Category Buttons**: 4-6 buttons with icons and text suggesting broad categories of tasks relevant to our platform.
3.  **Suggested Prompts**: 4 clickable suggested prompts to help users get started quickly.

## Component Breakdown

*   **`ChatWelcomeComponent`**: A new standalone component will be created to encapsulate the entire welcome screen (`chat-welcome.component.ts`, `chat-welcome.component.html`, `chat-welcome.component.scss`).
*   **`ChatPageComponent`**:
    *   Will include logic to show/hide `ChatWelcomeComponent`.
    *   The `ChatWelcomeComponent` will be displayed if `chatState.messages().length === 0`.
    *   The existing suggested prompts will be moved into the `ChatWelcomeComponent`.

## User Interaction Flow

1.  **New Chat**: User starts a new chat.
2.  **Welcome Screen Appears**: Because there are no messages, the `ChatWelcomeComponent` is displayed. The `app-chat-messages` component will be hidden or empty.
3.  **User sends a message**: The user either clicks a suggested prompt or types their own message and sends it.
4.  **Chat View Appears**: The `ChatWelcomeComponent` is hidden, and the `app-chat-messages` component now displays the conversation. 