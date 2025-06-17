Hashbrown# Simple Chatbot - Business Specification

## 1. Project Overview

This document outlines the business requirements for a simplified chatbot interface. The primary goal is to provide a clean, intuitive, and lightweight user experience. This application will act as a "thin client," with all complex logic, such as agent routing, document processing, and multi-LLM management, handled by the `AgentPlatform.API` backend.

The target technology stack is **Angular** for the framework, **Hashbrown** for the UI component library, and **Tailwind CSS** for styling.

## 2. Core Principles

- **Simplicity:** The UI should be minimal and focused on the core chat experience. Avoid feature bloat.
- **Backend-Driven:** All data and functionality will be driven by the `AgentPlatform.API`. The UI will not contain complex business logic or connect to third-party services directly.
- **Responsiveness:** The interface must be fully responsive and functional on both desktop and mobile devices.

## 3. Key Features & User Stories

### 3.1. User Authentication
- As a user, I want to be able to create an account so I can use the platform.
- As a user, I want to be able to log in to my account to access my conversations.
- As a user, I want my session to be remembered so I don't have to log in every time.
- As a user, I want to be able to view and update my basic profile information (e.g., name).

### 3.2. Chat Interface
- As a user, I want a single, clear chat window to send and receive messages.
- As a user, I want to see my conversation history so I can review past interactions.
- As a user, I want to be able to start a new conversation.
- As a user, I want to be able to upload files (e.g., PDF, TXT) with my message so the agent can use them for context.

### 3.3. Agent Interaction
- As a user, I want to have a seamless conversation without needing to know which specific "agent" (e.g., HR, IT) is handling my request. The backend will manage the routing.
- As a user, I might want to see a list of available agents and their capabilities, but my primary interaction should be through the main chat window.

## 4. Removed Features (Compared to `chatbot-ui`)

To achieve simplicity, the following features from the existing `chatbot-ui` will be **excluded**:

- **Workspaces:** The concept of multiple workspaces will be removed from the UI. All activity will occur within a single, default workspace for the user.
- **Direct Model Selection:** Users will not select an LLM (e.g., GPT-4). This is determined by the backend.
- **Client-Side Assistants/Presets/Prompts:** Management of assistants, presets, and reusable prompts will be removed. This functionality is owned by the backend.
- **User-Managed API Keys:** Users will not provide their own API keys for different services. The platform's backend will manage all API keys.
- **BFF for LLMs:** The UI will not have its own Backend-for-Frontend that calls LLM providers. All communication goes to `AgentPlatform.API`. 