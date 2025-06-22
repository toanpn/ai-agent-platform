# 🤖 AI Agent Platform

A comprehensive platform for creating, managing, and interacting with specialized AI agents. Built with modern web technologies and a microservices architecture with intelligent agent routing and JSON-based configuration.

## 🏗️ Architecture Overview

This platform consists of multiple specialized AI agents that can handle different domains (HR, IT, General Support, Search, Personal Assistant) through a central routing system with automatic JSON synchronization.

### Services Overview

| Service | Port | Technology | Description |
|---------|------|------------|-------------|
| Frontend | 4200 | Angular + TypeScript | Modern web interface |
| Backend API | 5000 | .NET 8 | REST API and business logic |
| Database | 1433 | SQL Server | Data persistence |
| Agent Core | 8000 | Python Flask | AI agent runtime with LangChain |

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
   # Get your API key from: https://console.cloud.google.com/apis/credentials
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
- **Agent Runtime**: Python FastAPI with Google ADK integration

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
├── backend/                   # .NET 8 Backend
│   ├── AgentPlatform.API/     # Main REST API
│   │   ├── Models/            # Entity models with Tools & LLM config
│   │   ├── DTOs/              # Data transfer objects
│   │   ├── Services/          # Business logic with JSON sync
│   │   ├── Controllers/       # API endpoints
│   │   ├── Data/              # Database context & seeding
│   │   ├── Migrations/        # EF Core migrations
│   │   └── Dockerfile         # Backend container
│   ├── AgentPlatform.Core/    # Python Agent Runtime
│   │   ├── core/              # Agent management modules
│   │   ├── toolkit/           # Agent tools (Jira, Search, etc.)
│   │   ├── agents.json        # Agent definitions (auto-synced)
│   │   ├── requirements.txt   # Python dependencies
│   │   ├── main.py            # CLI entry point
│   │   ├── start_api.py       # API server entry point
│   │   ├── api_server.py      # Flask API server
│   │   ├── Dockerfile         # Agent Core container
│   │   └── .dockerignore      # Docker build optimization
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
│   ├── .dockerignore          # Docker build optimization
│   └── docker-compose.yml     # Frontend service
└── docs/                      # Documentation
```

## 🔧 Development

### Backend Development

```bash
cd backend
docker-compose up -d sqlserver  # Start database
cd AgentPlatform.API
dotnet ef database update      # Apply migrations
dotnet run                     # Start API
```

### Frontend Development

```bash
cd frontend
npm install
ng serve
```

### Agent Development

```bash
cd backend/ADKAgentCore
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

## 🔄 Agent Configuration & Synchronization

### Agent Schema
Each agent has the following configuration:
```json
{
  "agent_name": "IT_Support_Agent",
  "description": "Handles technical support requests...",
  "tools": ["jira_ticket_creator", "it_knowledge_base_search"],
  "llm_config": {
    "model_name": "gemini-2.0-flash",
    "temperature": 0.0
  }
}
```

### Database Schema
```sql
-- Agent table includes:
- Tools (pipe-separated: "tool1|tool2|tool3")
- LlmModelName (string)
- LlmTemperature (double)
```

### Automatic Synchronization
- **Database → JSON**: Changes via API automatically update `agents.json`
- **Consistency**: Database and JSON file stay synchronized
- **Manual Sync**: `POST /api/agent/sync-json` endpoint available

## 🌟 API Endpoints

### Agent Management
- `GET /api/agent` - List all agents
- `GET /api/agent/{id}` - Get specific agent
- `POST /api/agent` - Create new agent
- `PUT /api/agent/{id}` - Update agent
- `DELETE /api/agent/{id}` - Delete agent (soft delete)
- `POST /api/agent/{id}/functions` - Add function to agent
- `POST /api/agent/sync-json` - Manual JSON synchronization

### Request/Response Examples

#### Create Agent
```json
POST /api/agent
{
  "name": "Custom_Agent",
  "department": "Sales",
  "description": "Sales support agent",
  "tools": ["crm_search", "lead_tracker"],
  "llmConfig": {
    "modelName": "gemini-2.0-flash",
    "temperature": 0.3
  }
}
```

#### Response
```json
{
  "id": 7,
  "name": "Custom_Agent",
  "department": "Sales",
  "tools": ["crm_search", "lead_tracker"],
  "llmConfig": {
    "modelName": "gemini-2.0-flash",
    "temperature": 0.3
  },
  "isActive": true,
  "createdAt": "2024-12-21T10:30:00Z"
}
```

## 🌟 Features

### For End Users
- **Multi-Agent Chat**: Seamless conversation with specialized AI agents
- **Smart Routing**: Automatic routing based on agent capabilities
- **Tool Integration**: Agents can use external tools (Jira, Google, Calendar)
- **File Upload**: Share documents for agent analysis
- **Chat History**: Access previous conversations
- **Responsive Design**: Works on desktop and mobile

### For Administrators
- **Agent Management**: Create and configure custom agents with tools
- **JSON Synchronization**: Automatic sync between database and configuration files
- **LLM Configuration**: Set model and temperature per agent
- **Tool Assignment**: Assign specific tools to each agent
- **User Management**: User registration and authentication
- **Analytics**: Monitor agent performance and usage
- **File Management**: Organize and manage agent knowledge files

## 🔐 Security

- JWT-based authentication
- Rate limiting on API endpoints
- Input validation and sanitization
- Secure file upload handling
- CORS configuration
- Environment-based configuration
- Soft delete for data retention

## 📈 Monitoring & Logging

- Structured logging with Serilog
- Request/response logging
- Agent operation tracking
- JSON sync error handling
- Error tracking and reporting
- Health check endpoints
- Docker container logging

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

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📧 Email: support@agentplatform.com
- 📖 Documentation: [docs/](./docs/)
- 🐛 Issues: [GitHub Issues](../../issues)

---

**Built with ❤️ using Angular, .NET 8, SQL Server, and Google ADK**
