# 🧠 AI Agent Platform for Departments using Google ADK

## 1. Project Overview

This project aims to build an internal AI Agent Platform that enables each department within an organization to independently create, configure, and maintain their own AI Agents using Google's Agent Development Kit (ADK). The system includes a central orchestrator agent that receives user messages and dynamically routes queries to the appropriate department agent based on the intent or context.

---

## 2. Goals & Objectives

- Provide a centralized yet flexible AI assistant infrastructure.
- Allow departments (HR, IT, Admin, Communications, etc.) to:
  - Create and configure their own AI agents.
  - Upload internal documents to their agent for retrieval-augmented generation (RAG).
  - Define custom functions/APIs the agent can call.
- Improve internal knowledge accessibility for employees.
- Minimize repeated manual Q&A tasks handled by support teams.
- Enable multi-agent communication and orchestration through a main router agent.

---

## 3. Key Features

### 3.1. Agent Orchestration
- A **Main Agent Router** receives all user queries.
- Determines the most appropriate department agent to handle the query.
- Uses keyword intent matching, routing rules, or LLM intent classification.

### 3.2. Department Agent Management
- UI for departments to:
  - Register a new agent.
  - Set agent name, and initial instructions (prompt).
  - Upload documents (PDFs, Markdown, or links to internal wikis).
  - Define accessible internal APIs or functions.
  - Test their agent in preview mode before going live.

### 3.3. Document Ingestion and Search
- Uploaded documents are indexed using a vector database.
- Used by agents to retrieve internal knowledge during conversations.

### 3.4. Custom Tooling & Function Calling
- Agents can define tools or API calls with:
  - Function schema (name, parameters, description).
  - Backend endpoint to be invoked at runtime.
- Support for tools such as:
  - Fetch leave policy (HR)
  - Create helpdesk ticket (IT)
  - Book meeting room (Admin)

### 3.5. User Chat Interface
- A unified web-based chat interface for employees.
- Messages go to the Main Agent first.
- The Main Agent then routes or delegates tasks to other agents.
- Users do not need to know which department handles which task.

---
## 4. Technical Architecture

```plaintext
+---------------------------+
|        Chat UI            |
+---------------------------+
           |
           v
+---------------------------+
|  Main Router Agent (ADK)  |
+---------------------------+
           |
   +---------------+---------------+---------------+
   |               |               |               |
   v               v               v               v
[HR Agent]     [IT Agent]     [Admin Agent]   [Comms Agent]
   |               |               |               |
Docs + APIs   Docs + APIs   Docs + Forms   Docs + Announcements
