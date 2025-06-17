# Project Improvements & Missing Features

This document outlines missing features from the backend API and potential improvements for the Angular frontend (`chatbot-ui-ng`).

## Backend: Missing Features

Based on the existing controllers and business specifications, here are some key features that appear to be missing from the `AgentPlatform.API`:

1.  **Workspace Management:** The business specifications identify the "Workspace" as the primary organizational unit. However, there are no controllers or endpoints for creating, reading, updating, deleting, or managing user membership for workspaces. This is a critical missing piece for multi-tenant functionality.

2.  **Agent File Management:** While agents can have files associated with them, there are no endpoints on the `AgentController` to add, remove, or manage these files after an agent has been created. The existing `FileController` seems to handle general file uploads but is not integrated with the agent-specific logic.

3.  **Agent Function Management:** The `AgentController` has an endpoint to *add* a function to an agent, but it lacks corresponding endpoints to **update** or **delete** a function from an agent.

4.  **User Profile Management:** The `AuthController` handles registration and login, but there are no endpoints for users to manage their own profiles (e.g., change their name, password, or department).

5.  **API Key Management:** The specifications mention that users should be able to manage their API keys for different AI providers, but there is no controller to handle this functionality.

6.  **Explicit Logout Endpoint:** While logout can be handled on the client-side by deleting the token, a dedicated `/api/auth/logout` endpoint would be a good practice for invalidating tokens on the server side, which enhances security.

---

## Frontend: Potential Improvements

The `chatbot-ui-ng` project has a solid foundation, but the following areas can be improved for robustness, security, and user experience.

### 1. Security

*   **Route Guards:** The `/chat` and `/agents` routes are currently unprotected. An `AuthGuard` should be implemented to prevent unauthenticated users from accessing these routes.
*   **Secure Token Storage:** Storing the JWT in `localStorage` is functional but vulnerable to XSS attacks. A more secure long-term solution would be for the backend to set an `httpOnly` cookie.

### 2. State Management

*   **Centralized Store:** The application could benefit from a centralized state management solution. Using a signal-based store (given the use of Angular and Hashbrown) or a more robust library like NgRx would help manage application-wide state (like user info, chat sessions, etc.) more effectively than individual services.

### 3. UI/UX (User Experience)

*   **Loading Indicators:** The application lacks feedback while data is being fetched. Adding spinners or loading indicators would greatly improve the user experience.
*   **User-Friendly Error Handling:** API errors are currently logged to the console. A user-facing notification system, such as toast messages, should be implemented to inform users when actions fail.
*   **Confirmation Dialogs:** Destructive actions like deleting an agent are instantaneous. A confirmation dialog should be added to prevent accidental deletions.
*   **Empty State Displays:** The UI should gracefully handle cases where there is no data to display (e.g., an empty agent list).

### 4. Code Quality & Best Practices

*   **Environment Variables:** The API URL is currently hardcoded in services. It should be moved to Angular's environment configuration files (`environment.ts` and `environment.prod.ts`).
*   **Stronger Typing:** Some component properties (e.g., the `message` input in `ChatMessageComponent`) use `any` as a type, which defeats the purpose of TypeScript. These should be replaced with their specific interfaces. 