# Project Improvements & Missing Features

This document outlines missing features from the backend API and potential improvements for the Angular frontend (`chatbot-ui-ng`).

## Backend: Missing Features (To-Do)

Based on the existing controllers and business specifications, here are some key features that appear to be missing from the `AgentPlatform.API`:

1.  **Workspace Management:** The business specifications identify the "Workspace" as the primary organizational unit. However, there are no controllers or endpoints for creating, reading, updating, deleting, or managing user membership for workspaces. This is a critical missing piece for multi-tenant functionality.

2.  **Agent File Management:** While agents can have files associated with them, there are no endpoints on the `AgentController` to add, remove, or manage these files after an agent has been created. The existing `FileController` seems to handle general file uploads but is not integrated with the agent-specific logic.

3.  **Agent Function Management:** The `AgentController` has an endpoint to *add* a function to an agent, but it lacks corresponding endpoints to **update** or **delete** a function from an agent.

4.  **User Profile Management:** The `AuthController` handles registration and login, but there are no endpoints for users to manage their own profiles (e.g., change their name, password, or department).

5.  **API Key Management:** The specifications mention that users should be able to manage their API keys for different AI providers, but there is no controller to handle this functionality.

6.  **Explicit Logout Endpoint:** While logout can be handled on the client-side by deleting the token, a dedicated `/api/auth/logout` endpoint would be a good practice for invalidating tokens on the server side, which enhances security.

---

## Frontend Improvements

### Completed

The following improvements have been implemented in the `chatbot-ui-ng` project:

*   **Security - Route Guards:** An `AuthGuard` has been implemented to prevent unauthenticated users from accessing protected routes.
*   **Code Quality - Environment Variables:** The API URL has been moved from hardcoded strings in services to Angular's environment configuration files.
*   **UI/UX - Loading & Error States:** The Agent List now displays loading spinners and user-friendly error messages.
*   **UI/UX - Confirmation Dialogs:** A confirmation dialog has been added to the delete agent functionality to prevent accidental deletions.
*   **UI/UX - Empty State Displays:** The Agent List now shows a user-friendly message when no agents are available.
*   **Code Quality - Stronger Typing:** The `message` property in the `ChatMessageComponent` has been updated from `any` to a specific `ChatMessage` interface.

### To-Do / Potential Future Enhancements

*   **Secure Token Storage:** Storing the JWT in `localStorage` is functional but vulnerable to XSS attacks. A more secure long-term solution would be for the backend to set an `httpOnly` cookie.
*   **Centralized State Management:** The application could benefit from a centralized state management solution like NgRx or a signal-based store to manage application-wide state more effectively.
*   **Advanced User-Friendly Error Handling:** API errors are currently logged to the console in many places. A global, user-facing notification system, such as toast messages, should be implemented. 