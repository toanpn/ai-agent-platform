# Simple Chatbot - UI Specification

This document provides a high-level, text-based wireframe and description of the user interface for the simple Angular chatbot.

## 1. Layout

The UI will consist of a main, two-column layout, which is active after the user has logged in.

- **Left Column (Sidebar):** A fixed-width column that displays the user's conversation history.
- **Right Column (Chat Panel):** The main area where the active conversation is displayed and where the user interacts with the chatbot.

---

## 2. Screens & Components

### 2.1. Login Screen

A single, centered card on a plain background.

```
+-------------------------------------------+
|                                           |
|              [Company Logo]               |
|                                           |
|  +-------------------------------------+  |
|  | Email                               |  |
|  +-------------------------------------+  |
|                                           |
|  +-------------------------------------+  |
|  | Password                            |  |
|  +-------------------------------------+  |
|                                           |
|  +-------------------------------------+  |
|  |             Login                   |  |
|  +-------------------------------------+  |
|                                           |
|         Don't have an account?          |
|                 Sign Up                 |
|                                           |
+-------------------------------------------+
```
- **Components:** `LoginComponent`. Uses Hashbrown inputs and buttons.

### 2.2. Chat View (Main Screen)

This is the primary interface for the application.

```
+--------------------------------------------------------------------------+
| Sidebar (25%)              | Chat Panel (75%)                            |
+----------------------------+---------------------------------------------+
|                            |                                             |
|  [User Avatar/Name]        |  +---------------------------------------+  |
|  +-----------------------+ |  | Assistant: Hi! How can I help you?    |  |
|  |    + New Chat         | |  +---------------------------------------+  |
|  +-----------------------+ |                                             |
|                            |  +---------------------------------------+  |
|  [Conversation History]    |  | User: I need to know the policy...    |  |
|  - Chat Title 1 (Active)   |  +---------------------------------------+  |
|  - Chat Title 2            |                                             |
|  - Chat Title 3            |                                             |
|  ...                       |                                             |
|                            |                                             |
|                            |                                             |
|                            |                                             |
|                            |                                             |
|                            |                                             |
|                            |                                             |
|                            |                                             |
|  [Logout Button]           |  +---------------------------------------+  |
|                            |  | [Attach File] [Text Input Area......] |  |
+----------------------------+---------------------------------------------+
```

#### 2.2.1. Sidebar

- **User Info:** Displays the current user's name or avatar at the top.
- **New Chat Button:** Clears the chat panel to start a new conversation.
- **Conversation List:** A scrollable list of past chats. Clicking on a chat loads it into the Chat Panel. The active chat is highlighted.
- **Logout:** A button at the bottom to log the user out.
- **Components:** `ChatSidebarComponent`.

#### 2.2.2. Chat Panel

- **Message Area:** A scrollable view that displays the messages of the active conversation. User messages are aligned to the right, and assistant messages are aligned to the left.
- **Input Area:** A fixed area at the bottom.
  - **File Attachment:** A button (e.g., a paperclip icon) to open a file dialog.
  - **Text Input:** A multi-line text input field for the user's message.
  - **Send Button:** A button to send the message.
- **Components:** `ChatViewComponent`, `ChatMessageComponent`, `ChatInputComponent`.

---

## 3. Agent Management Views

### 3.1. Agent List View

A view displaying a table of agents with a button to create new ones.

```
+--------------------------------------------------------------------------+
| Top Bar                                                                  |
+--------------------------------------------------------------------------+
| Agents                                               [Create Agent]      |
+--------------------------------------------------------------------------+
|                                                                          |
|  +--------------------------------------------------------------------+  |
|  | Name     | Department      | Description                 | Actions |  |
|  +----------+-----------------+-----------------------------+---------+  |
|  | Agent 1  | Sales           | Handles sales inquiries.    | [View]  |  |
|  | Agent 2  | Support         | Assists with support...     | [Edit]  |  |
|  +--------------------------------------------------------------------+  |
|                                                                          |
+--------------------------------------------------------------------------+
```
- **Components:** `AgentListComponent`.

### 3.2. Agent Form / Detail View

A form for creating or editing an agent's details. The same layout is used to display agent details in a read-only fashion.

```
+--------------------------------------------------------------------------+
| Top Bar                                                                  |
+--------------------------------------------------------------------------+
| Create Agent / Edit Agent / Agent Details              [Save] [Delete]   |
+--------------------------------------------------------------------------+
|                                                                          |
|  Name                                                                    |
|  +--------------------------------------------------------------------+  |
|  | [Agent Name Input]                                                 |  |
|  +--------------------------------------------------------------------+  |
|                                                                          |
|  Department                                                              |
|  +--------------------------------------------------------------------+  |
|  | [Department Input]                                                 |  |
|  +--------------------------------------------------------------------+  |
|                                                                          |
|  Description                                                             |
|  +--------------------------------------------------------------------+  |
|  | [Description Text Area]                                            |  |
|  +--------------------------------------------------------------------+  |
|                                                                          |
+--------------------------------------------------------------------------+
```
- **Components:** `AgentFormComponent`, `AgentDetailComponent`.

## 4. Component Sourcing

- All interactive elements like **Buttons**, **Input Fields**, and **Cards** will be implemented using the **Hashbrown** component library.
- Layout and positioning will be handled using **Tailwind CSS** utility classes. 