<!-- 🅰️ Angular | 🟦 TypeScript | ⚙️ .NET 8 | 🐍 Python | 🗄️ SQL Server | 🐳 Docker | 🤖 Google ADK -->
<p align="center">
  🅰️ <b>Angular</b> &nbsp;|&nbsp; 🟦 <b>TypeScript</b> &nbsp;|&nbsp; ⚙️ <b>.NET 8</b> &nbsp;|&nbsp; 🐍 <b>Python</b> &nbsp;|&nbsp; 🗄️ <b>SQL Server</b> &nbsp;|&nbsp; 🐳 <b>Docker</b> &nbsp;|&nbsp; 🤖 <b>Google ADK</b>
</p>

# 🤖 AI Agent Platform

A comprehensive platform for creating, managing, and interacting with specialized AI agents. Built with modern web technologies and a microservices architecture with intelligent agent routing and JSON-based configuration.

## 🏗️ Architecture Overview

This platform consists of multiple specialized AI agents that can handle different domains (HR, IT, General Support, Search, Personal Assistant) through a central routing system with automatic JSON synchronization.

### Layered Architecture & Workflow

The platform is organized into four main layers, each with a distinct responsibility and technology stack:

#### 1. Frontend (Presentation Layer)
- **Technology:** Angular 20+, TypeScript, Angular Material, SCSS
- **Responsibilities:**
  - User interface and experience
  - Real-time chat and agent management
  - Authentication and authorization (JWT)
  - API communication via HTTP/WebSocket

#### 2. Backend API (Application Layer)
- **Technology:** .NET 8, Entity Framework Core, Serilog
- **Responsibilities:**
  - REST API for frontend and agent core
  - Business logic and orchestration
  - Authentication, authorization, and rate limiting
  - Agent and user management
  - Synchronization with Agent Core (agents.json)

#### 3. Agent Core (AI/Agent Layer)
- **Technology:** Python 3, Flask, LangChain, Google ADK
- **Responsibilities:**
  - AI agent runtime and orchestration
  - Tool integration (Jira, Google Search, etc.)
  - LLM configuration and prompt enhancement
  - File processing and RAG (Retrieval-Augmented Generation)

#### 4. Database (Persistence Layer)
- **Technology:** SQL Server
- **Responsibilities:**
  - Persistent storage for users, agents, chat history, and configuration
  - Automatic migrations and data integrity

#### Workflow Diagram

```mermaid
graph TD
  A[User (Browser)] -->|HTTP/WebSocket| B[Frontend (Angular)]
  B -->|REST API| C[Backend API (.NET 8)]
  C <--> |Sync/REST| D[Agent Core (Python Flask)]
  C -->|SQL| E[Database (SQL Server)]
  D -->|File/Tool APIs| F[External Tools/APIs]
```

- **User** interacts with the **Frontend** via browser.
- **Frontend** communicates with the **Backend API** for all business operations.
- **Backend API** manages data, authentication, and synchronizes agent configuration with the **Agent Core**.
- **Agent Core** executes AI logic, tool integrations, and interacts with external APIs.
- **Database** stores all persistent data.

### Services Overview

| Service         | Port | Technology                | Description                                 |
|----------------|------|---------------------------|---------------------------------------------|
| Frontend       | 4200 | Angular 20+ + TypeScript  | Modern web interface                        |
| Backend API    | 5000 | .NET 8                    | REST API and business logic                 |
| Database       | 1433 | SQL Server                | Data persistence                            |
| Agent Core     | 8000 | Python Flask              | AI agent runtime with LangChain             |

### 🎯 Key Features

- **Multi-Agent System**: Specialized agents for different departments with tool integration
- **Intelligent Routing**: Automatic message routing to appropriate agents
- **Agent-Database Sync**: Bidirectional synchronization between database and `agents.json`
- **Tool Integration**: Each agent can have multiple tools (Jira, Google Search, Calendar, etc.)
- **LLM Configuration**: Configurable model and temperature per agent
- **Real-time Chat**: WebSocket-based real-time messaging
- **File Management**: Upload and process documents for agent knowledge
- **User Management**: Secure authentication and user profiles
- **Modern UI**: Clean, responsive interface built with Angular Material

## 🚀 Quick Start

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- [Node.js 18+](https://nodejs.org/) (for frontend development)
- [Angular CLI](https://angular.io/cli) (for Angular development)
- [.NET 8 SDK](https://dotnet.microsoft.com/download/dotnet/8.0) (for backend development)

### Running with Docker

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd ai-agent-platform
   ```

2. **Configure environment variables:**
   ```bash
   # Copy the environment template
   cp env.template .env
   # Edit .env and set your Google API key (required for AgentPlatform.Core)
   # Get your API key from: https://aistudio.google.com/apikey
   ```

3. **Start all services (Full Stack):**
   ```bash
   docker-compose up -d
   ```

4. **Or start individual services:**
   ```bash
   # Backend only (includes database and agent core)
   cd backend && docker-compose up -d
   # Frontend only
   cd frontend && docker-compose up -d
   ```

5. **Access the applications:**
   - Frontend: http://localhost:4200
   - Backend API: http://localhost:5000
   - Agent Core API: http://localhost:8000
   - API Documentation: http://localhost:5000/swagger

## 🛠️ Technology Stack

### Frontend
- **Framework**: Angular 20+ with TypeScript
- **Styling**: SCSS with Angular Material Design
- **UI Components**: Angular Material 20.0.3
- **State Management**: RxJS 7.8.0 (built-in with Angular)
- **HTTP Client**: Angular HttpClient with custom interceptors
- **Authentication**: JWT Bearer tokens with custom interceptor
- **AI Integration**: HashbrownAI packages for AI functionality

### Backend
- **API**: .NET 8 Web API with Entity Framework Core
- **Database**: SQL Server with automatic migrations
- **Authentication**: JWT Bearer tokens
- **Agent Configuration**: JSON-based with database synchronization
- **Logging**: Serilog
- **Rate Limiting**: AspNetCoreRateLimit
- **Agent Runtime**: Python Flask with Google ADK integration

### Frontend Development Tools
- **Build System**: Angular CLI with esbuild
- **Testing**: Jasmine & Karma
- **Linting**: ESLint with TypeScript support
- **Formatting**: Prettier
- **Type Checking**: TypeScript with strict mode

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Database**: SQL Server
- **File Storage**: Local file system (configurable)
- **Configuration**: Environment-based with JSON sync

## 🤖 Available Agents

### 🎯 General Utility Agent (Main Router)
- **Department**: General
- **Tools**: `google_search`, `check_calendar`, `check_weather`
- **LLM Config**: Gemini 2.0 Flash (temp: 0.4)
- **Purpose**: Versatile fallback agent for various utility tasks

### 🛠️ IT Support Agent
- **Department**: IT
- **Tools**: `jira_ticket_creator`, `it_knowledge_base_search`
- **LLM Config**: Gemini 2.0 Flash (temp: 0.0)
- **Expertise**: Technical support, troubleshooting, Jira ticket management

### 👥 HR Agent
- **Department**: HR
- **Tools**: `policy_document_search`, `leave_request_tool`
- **LLM Config**: Gemini 2.0 Flash (temp: 0.7)
- **Expertise**: HR policies, leave procedures, recruitment information

### 🔍 Search Agent
- **Department**: General
- **Tools**: `google_search`
- **LLM Config**: Gemini 2.0 Flash (temp: 0.5)
- **Purpose**: Internet search for current information, news, guides

### 📅 Personal Assistant Agent
- **Department**: General
- **Tools**: `check_calendar`, `check_weather`
- **LLM Config**: Gemini 2.0 Flash (temp: 0.3)
- **Purpose**: Calendar management, weather updates, daily planning

### 🚀 ADK Assistant (Advanced)
- **Department**: AI Research
- **Tools**: `adk_search`, `adk_http_request`, `adk_workflow`
- **LLM Config**: Gemini 2.0 Flash (temp: 0.2)
- **Purpose**: Advanced AI operations with Google ADK integration

## 📁 Project Structure

```
ai-agent-platform/
├── docker-compose.yml         # Full stack Docker setup
├── env.template               # Environment variables template
├── backend/                   # Backend services
│   ├── AgentPlatform.API/     # .NET 8 REST API
│   │   ├── Models/            # Entity models with Tools & LLM config
│   │   ├── DTOs/              # Data transfer objects
│   │   ├── Services/          # Business logic with JSON sync
│   │   ├── Controllers/       # API endpoints
│   │   ├── Data/              # Database context & seeding
│   │   ├── Migrations/        # EF Core migrations
│   │   └── Dockerfile         # Backend container
│   ├── AgentPlatform.Core/    # Python Agent Runtime (Flask)
│   │   ├── core/              # Agent management modules
│   │   ├── toolkit/           # Agent tools (Jira, Search, etc.)
│   │   ├── agents.json        # Agent definitions (auto-synced)
│   │   ├── requirements.txt   # Python dependencies
│   │   ├── main.py            # CLI entry point
│   │   ├── start_api.py       # API server entry point
│   │   ├── api_server.py      # Flask API server
│   │   └── Dockerfile         # Agent Core container
│   ├── shared/                # Shared models
│   └── docker-compose.yml     # Backend services
├── frontend/                  # Angular Frontend
│   ├── src/app/               # Angular application
│   │   ├── features/          # Feature modules (auth, chat, agent-management)
│   │   ├── core/              # Core services, guards, interceptors
│   │   └── shared/            # Shared components, models, pipes
│   ├── angular.json           # Angular CLI configuration
│   ├── package.json           # NPM dependencies
│   ├── tsconfig.json          # TypeScript configuration
│   ├── Dockerfile             # Frontend container
│   └── docker-compose.yml     # Frontend service
└── docs/                      # Documentation
```

## 🔧 Development

### Backend Development

```bash
cd backend
# Start database (SQL Server)
docker-compose up -d sqlserver
cd AgentPlatform.API
# Apply migrations
# Option 1: Using EF Core CLI
dotnet ef database update
# Option 2: Using provided migration script
# (edit scripts/migrations.sql as needed, then run)
# psql or Azure Data Studio, or use scripts/migration-scripts.ps1 for PowerShell
# Start API
dotnet run
```

### Frontend Development

```bash
cd frontend
npm install
ng serve
```

### Agent Core Development

```bash
cd backend/AgentPlatform.Core
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

## 🚀 Deployment

### Production Deployment

1. **Configure environment variables**
2. **Set up SSL certificates**
3. **Configure production database**
4. **Apply database migrations**
5. **Deploy with Docker Compose**

### Environment Variables

```env
# Backend
ConnectionStrings__DefaultConnection=<sql-server-connection>
Jwt__Key=<secure-jwt-key>
ASPNETCORE_ENVIRONMENT=Production
```

### Database Migrations

```bash
# Apply migrations in production
cd backend/AgentPlatform.API
dotnet ef database update --configuration Release
# Or use scripts/migration-scripts.ps1 for PowerShell
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow the existing agent schema when adding new agents
- Ensure database changes include proper migrations
- Test JSON synchronization after agent modifications
- Update documentation for new tools or agents
