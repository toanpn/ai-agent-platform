# Frontend Chatbot - Business Specification

This document outlines the business logic and user-facing features of the chatbot UI.

## 1. Core Concepts

- **Workspace:** The primary organizational unit. All chats, files, and other resources are scoped to a workspace. A user can be a member of multiple workspaces.
- **Chat:** A single conversation between a user and an AI model or assistant. Each chat has its own context and message history.
- **Message:** A single turn in a conversation, either from the user or the AI.
- **Model:** A specific Large Language Model (LLM) that can be used for a chat (e.g., GPT-4, Claude 3).
- **Assistant:** A pre-configured AI agent with a specific purpose. An assistant has a name, a set of instructions (prompt), a designated model, and can be equipped with files and tools.
- **Preset:** A user-defined configuration for a chat, including a prompt, model, and other settings, that can be reused.
- **Prompt:** A piece of text that can be quickly inserted into the chat input.
- **Tool:** A custom function that an assistant can call to perform an action or retrieve information from an external system.
- **File:** A document that can be uploaded and associated with a chat or an assistant. The AI can use retrieval-augmented generation (RAG) to find information in these files to answer questions.

## 2. User Stories & Features

### 2.1. Chatting

- As a user, I want to start a new chat so that I can have a conversation with the AI.
- As a user, I want to see my past conversations so that I can review them or continue them later.
- As a user, I want to be able to edit my previous messages so that I can correct mistakes or refine my questions.
- As a user, I want to be able to regenerate the AI's response so that I can get a different answer.
- As a user, I want to be able to stop the AI while it is generating a response.
- As a user, I want to be able to clear all messages in a chat and start over.
- As a user, I want to be able to search my chat history.

### 2.2. Model & Assistant Selection

- As a user, I want to be able to choose which AI model to chat with.
- As a user, I want to be able to select from a list of pre-configured assistants to perform specific tasks.
- As a user, I want to be able to see the details of an assistant, including its instructions and capabilities.

### 2.3. File & Data Integration

- As a user, I want to be able to upload files to a chat so that the AI can use the information in those files.
- As a user, I want to see which files are currently active in my chat session.
- As a user, I want the AI to be able to search through the attached files to find answers to my questions (Retrieval).

### 2.4. Personalization & Configuration

- As a user, I want to be able to create and save my own presets for chat configurations.
- As a user, I want to create and save my own custom prompts for quick access.
- As a user, I want to be able to configure chat settings like temperature and context length.
- As a user, I want to manage my API keys for different AI providers in my profile settings.
- As a user, I want to be able to switch between different workspaces.

## 3. User Interface Overview

- **Sidebar:** The main navigation area on the left, allowing users to switch between chats, assistants, presets, files, etc. It also contains the workspace switcher.
- **Chat View:** The central part of the screen where the conversation takes place.
  - **Message List:** Displays the history of messages in the current chat.
  - **Chat Input:** The text area at the bottom where the user types their message. It includes buttons for attaching files and using prompts.
  - **Chat Settings:** A panel to configure the model and other parameters for the current chat.
- **Profile/Settings:** A section for managing user-specific information like API keys and profile details. 