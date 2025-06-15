# **Technical Implementation Plan: AgentPlatform.Core**

## 1. Overview & Goal

**Goal:** Build a flexible and scalable **AI runtime service** (AI Core). This service processes chat interactions with AI agents by loading their configurations from a shared database and executing AI-powered conversations with the selected tools.

**Core Concept:** The service operates based on the **Function Tool** model. Functional tools are pre-defined in code. The service loads agent configurations (which include tool selections and authentication) from the database and "assembles" (instantiates) a dynamic agent at runtime to fulfill chat requests.

**Database Integration:** The Python service connects to the same SQL Server database as the AgentPlatform.API (.NET Core) for unified data management.

**Architecture:** 
- **AgentPlatform.API (.NET)**: Primary management layer for agent creation, user management, file uploads
- **AgentPlatform.Core (Python)**: AI runtime layer for chat processing, tool execution, agent discovery

## 2. Technology Stack

- **Language:** Python 3.10+
- **Web Framework:** FastAPI
- **Data Validation:** Pydantic
- **AI/LLM Framework:** Google Generative AI SDK 
- **Database:** SQL Server (shared with .NET API)
- **Database Driver:** pyodbc + ODBC Driver 18 for SQL Server
- **Deployment:** Docker

## 3. Project Structure

The project follows the standard structure of a modern Python application to ensure modularity and maintainability.

```
agent-platform-core/
│
├── .env.example                # Template file for environment variables
├── .gitignore
├── docker-compose.yml          # SQL Server integration
├── Dockerfile                  # With ODBC drivers
├── requirements.txt            # SQL Server drivers
├── README.md
│
└── src/
    └── agent_platform_core/
        │
        ├── __init__.py
        ├── main.py                 # FastAPI application entry point
        │
        ├── api/
        │   ├── __init__.py
        │   └── endpoints/
        │       ├── __init__.py
        │       ├── agents.py       # API endpoints for CRUD agent config
        │       └── chat.py         # API endpoint for /chat
        │
        ├── agents/
        │   ├── __init__.py
        │   ├── orchestrator.py   # Master Agent logic (tool selection)
        │   └── runtime.py        # Dynamic agent "assembly" and execution logic
        │
        ├── database/
        │   ├── __init__.py
        │   ├── connection.py     # SQL Server connection management
        │   └── repositories/
        │       ├── __init__.py
        │       └── agent_repository.py  # Agent CRUD operations
        │
        ├── models/
        │   ├── __init__.py
        │   └── schemas.py        # Pydantic models (matching .NET API)
        │
        └── tools/
            ├── __init__.py
            ├── registry.py       # Central registration repository (Tool Registry)
            │
            ├── common/           # Common utility functions for tools
            │   └── http_client.py
            │
            ├── jira.py           # Tool functions related to Jira
            ├── google_calendar.py# Tool functions related to Google Calendar
            └── confluence.py     # Tool functions related to Confluence (RAG)
```

## 4. Database Schema (Shared with .NET API)

The Python service uses the same SQL Server database tables as the .NET API:

### Core Tables:
- **Agents**: Main agent configurations (Id, Name, Department, Description, Instructions, IsActive, IsMainRouter, CreatedById, CreatedAt, UpdatedAt)
- **AgentFunctions**: Functions/tools available to agents (Id, AgentId, Name, Description, Schema, EndpointUrl, HttpMethod, Headers, IsActive, CreatedAt, UpdatedAt)
- **AgentFiles**: Files associated with agents (Id, AgentId, FileName, FilePath, FileSize, ContentType, UploadedAt)
- **Users**: User management (Id, Username, Email, FullName, Department, IsActive, CreatedAt, UpdatedAt)
- **ChatSessions**: Chat session management (Id, UserId, AgentId, SessionName, CreatedAt, UpdatedAt)
- **ChatMessages**: Individual chat messages (Id, SessionId, Role, Content, Timestamp)

## 5. Core Data Models (Pydantic)

Define main data structures in `src/agent_platform_core/models/schemas.py` to match the .NET API models.

## 6. Implementation Plan (Task Checklist)

### Phase 1: Project Setup & Core Foundation ✅ **COMPLETED**
- [x] Set up project directory structure as above.
- [x] Install required libraries (`fastapi`, `uvicorn`, `pydantic`, `python-dotenv`, `google-generativeai`, SQL Server drivers).
- [x] Initialize basic FastAPI application in `main.py`.
- [x] Configure centralized logging for the entire application.
- [x] Define Pydantic models in `models/schemas.py`.

**Implementation Notes:**
- ✅ Complete project structure created with all required directories and `__init__.py` files
- ✅ `requirements.txt` with SQL Server dependencies (pyodbc, aioodbc)
- ✅ `main.py` with FastAPI app, logging configuration, CORS, error handling, and health checks
- ✅ Comprehensive Pydantic models in `schemas.py` matching .NET API structure
- ✅ API endpoints structure with placeholder implementations for agents and chat
- ✅ Docker configuration (`Dockerfile` and `docker-compose.yml`) with SQL Server
- ✅ Complete `README.md` with setup and usage instructions
- ✅ `.gitignore` file for Python projects

### Phase 1.5: Database Setup & Migration ✅ **COMPLETED**
- [x] **SQL Server Integration**: Connect to the same database as the .NET API
    - [x] Updated connection string for SQL Server with ODBC Driver 18
    - [x] Database connection management in `database/connection.py`
    - [x] Connection pooling and error handling
    - [x] Health check endpoints for database connectivity
- [x] Implement database connection management in `database/connection.py`.
- [x] Create `AgentRepository` class in `database/repositories/agent_repository.py` for CRUD operations.
- [x] **Database Schema Alignment**: Ensure Python models match .NET API database structure
    - [x] Updated Pydantic models to match .NET API (Agent, AgentFunction, AgentFile, User, ChatSession, ChatMessage)
    - [x] Raw SQL queries to work with existing database schema
    - [x] Proper data type mapping (integer IDs, datetime handling)

**Implementation Notes:**
- ✅ SQL Server connection with pyodbc and ODBC Driver 18
- ✅ Database URL: `mssql+pyodbc://sa:password@localhost:1433/agentplatform?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes`
- ✅ AgentRepository with full CRUD operations using raw SQL
- ✅ Proper error handling and transaction management
- ✅ Docker configuration updated for SQL Server container
- ✅ Health check endpoints for database monitoring

### Phase 2: Tool Implementation & Registration ✅ **COMPLETED**
- [x] Design and implement `Tool Registry` in `tools/registry.py`. *(Fully implemented with metadata, credential injection, and auto-registration)*
- [x] **(MVP Tools)** Implement basic tool functions:
    - [x] **Jira:** `create_jira_ticket`, `read_jira_ticket`, `search_jira_tickets`. *(Comprehensive Jira integration)*
    - [x] **Google Calendar:** `create_google_calendar_event`, `find_free_time`, `get_calendar_events`. *(Full calendar management)*
    - [x] **Confluence/RAG:** `search_confluence_documents`, `get_confluence_page`, `search_confluence_spaces`. *(Complete knowledge base integration)*
- [x] Register all created tool functions in `Tool Registry`. *(Auto-registration system implemented)*
- [x] Write detailed and clear `docstring` for each tool function. *(Comprehensive documentation with examples)*

**Implementation Notes:**
- ✅ Central `ToolRegistry` class with metadata management and credential injection
- ✅ `HTTPClient` utility for authenticated API calls with error handling
- ✅ **9 tool functions** across 3 categories: Jira (3), Calendar (3), Confluence (3)
- ✅ **Auto-registration system** that imports and registers tools on startup
- ✅ **Credential validation** and **parameter schema** support
- ✅ **Category-based organization** for easy tool discovery

### Phase 3: Agent Configuration & Management
- [x] Implement database-based agent management using `AgentRepository` in `database/repositories/agent_repository.py`.
- [x] Build Agent API Endpoints in `api/endpoints/agents.py`:
    - [x] `GET /agents/{agent_id}`: Get agent configuration for runtime use. *(Read-only runtime endpoint)*
    - [x] `GET /agents`: List available agents for runtime. *(Read-only runtime endpoint)*
    - [x] `GET /agents/department/{department}`: List agents by department for routing. *(New runtime endpoint)*
    - [x] **Architectural Decision**: Removed CRUD operations (POST, PUT, DELETE) from AgentPlatform.Core as these should be handled by AgentPlatform.API (.NET) *(Management layer separation)*

### Phase 4: Core Agent Logic ✅ **COMPLETED**
- [x] Implement logic for **Specialist Agent Runtime** in `agents/runtime.py`. This is the most complex part: *(✅ MIGRATED TO ADK)*
- [x] Implement logic for **Master Agent (Orchestrator)** in `agents/orchestrator.py` to select appropriate tools from the agent's tool list. *(✅ MIGRATED TO ADK)*
- [x] Implement main API Endpoint in `api/endpoints/chat.py`:
    - [x] `POST /chat`: Receive request, call `Agent Runtime` for processing and return results. *(Enhanced with database integration)*

**Implementation Notes:**
- ✅ **AgentOrchestrator**: AI-powered request analysis and tool selection using Gemini Pro
- ✅ **AgentRuntime**: Complete dynamic agent assembly with tool execution
- ✅ **Intelligent Analysis**: Context-aware tool selection with fallback mechanisms
- ✅ **Retry Logic**: Robust error handling with exponential backoff
- ✅ **Response Generation**: AI-powered response synthesis from tool results into conversational responses
- ✅ **Tool Execution**: Safe credential injection and parallel tool processing
- ✅ **Enhanced Chat API**: Integration with runtime system, tool validation, and credential management

**🎉 MIGRATION TO GOOGLE ADK COMPLETED:**
- ✅ **Legacy Custom Runtime** (`agents/runtime.py`) → **ADK Agent Runtime** (`agents/adk_agents.py`)
- ✅ **Legacy Custom Orchestrator** (`agents/orchestrator.py`) → **ADK Workflow Agents** (Sequential, Parallel, Loop)
- ✅ **Custom Tool System** → **ADK Tools with Adapter** (`tools/adk_tools.py`)
- ✅ **Manual Agent Assembly** → **ADK Agent Factory** with automated agent creation
- ✅ **Custom Error Handling** → **ADK Built-in Retry Logic** and error management

### Phase 5: Deployment & Finalization
- [x] Write `Dockerfile` and `docker-compose.yml`