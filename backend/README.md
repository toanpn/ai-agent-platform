# 🤖 AI Agent Platform - Backend

A comprehensive backend system for managing AI agents with secure user authentication, real-time chat capabilities, and flexible agent management.

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │   Agent Core    │
│   (React/Next)  │◄──►│  (.NET 8 API)  │◄──►│   (Python)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   SQL Server    │
                       │                 │
                       └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Router Agent  │
                       │   (Main Bot)    │
                       └─────────────────┘
                              │
                   ┌──────────┼──────────┐
                   ▼          ▼          ▼
            ┌──────────┐ ┌──────────┐ ┌──────────┐
            │ HR Bot   │ │ IT Bot   │ │ ... Bot  │
            └──────────┘ └──────────┘ └──────────┘
```

## 🌟 Features

### Core Features
- **User Management**: Registration, authentication, profile management
- **Agent Management**: Create, configure, and manage AI agents
- **Chat System**: Real-time messaging with agents
- **File Management**: Upload and manage agent knowledge files
- **Function Integration**: Define custom functions for agents
- **Department-based Access**: Role-based agent access control

### Technical Features
- **JWT Authentication**: Secure token-based authentication
- **Rate Limiting**: API rate limiting for security
- **File Upload**: Secure file handling with validation
- **Logging**: Comprehensive logging with Serilog
- **Docker Support**: Containerized deployment
- **Auto-migration**: Database schema management

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| API Framework | .NET 8 Web API | REST API endpoints |
| Database | SQL Server | Data persistence |
| ORM | Entity Framework Core | Database operations |
| Authentication | JWT Bearer | Secure authentication |
| Validation | FluentValidation | Input validation |
| Logging | Serilog | Application logging |
| Rate Limiting | AspNetCoreRateLimit | API protection |
| Agent Runtime | Python FastAPI | AI agent execution |

## 📋 Prerequisites

- [.NET 8 SDK](https://dotnet.microsoft.com/download/dotnet/8.0)
- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- [Python 3.11+](https://www.python.org/downloads/) (for agent development)

## 🚀 Quick Start

### Using Docker (Recommended)

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd ai-agent-platform/backend
   ```

2. **Start all services:**
   ```bash
   docker-compose up -d
   ```

3. **Access the application:**
   - API: http://localhost:5000
   - Swagger UI: http://localhost:5000/swagger
   - Agent Core: http://localhost:8000

### Services Overview

| Service | URL | Description |
|---------|-----|-------------|
| API | http://localhost:5000 | Main REST API |
| Database | localhost:1433 | SQL Server database |
| Agent Core | http://localhost:8000 | Python agent runtime |
| Swagger | http://localhost:5000/swagger | API documentation |

## 🤖 Agents Overview

The system includes several specialized agents:

### 🎯 Main Router Agent
**Purpose**: Central coordinator that routes user queries to appropriate specialized agents
- Analyzes user intent
- Routes to HR, IT, or other domain-specific agents
- Provides general assistance when no specific agent is needed

### 👥 HR Bot
**Purpose**: Human Resources support and information
- Employee handbook queries
- PTO policies and requests
- Benefits information
- Company policies

### 🖥️ IT Bot
**Purpose**: Technical support and IT assistance
- Password reset procedures
- Software installation guides
- Network troubleshooting
- Equipment requests

### ➕ Extensible Architecture
- Easy to add new specialized agents
- Each agent can have custom knowledge files
- Configurable routing logic

**Example Interaction:**
```
User: "How do I request time off?"
↓
Main Router: Analyzes query → Routes to HR Bot
↓
HR Bot: Provides PTO information and next steps
```

## 🛠️ Development Setup

### Local API Development

1. **Setup database:**
   ```bash
   docker-compose up sqlserver -d
   ```

2. **Run API locally:**
   ```bash
   cd AgentPlatform.API
   dotnet restore
   dotnet run
   ```

### Local Python Agent Development

1. **Setup Python environment:**
   ```bash
   cd ADKAgentCore
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   pip install -r requirements.txt
   ```

2. **Run agent core:**
   ```bash
   python main.py
   ```

## 🔧 Configuration

### Environment Variables

**API Service:**
- `ConnectionStrings__DefaultConnection` - Database connection
- `Jwt__Key` - JWT signing key
- `AgentRuntime__BaseUrl` - Runtime service URL

**Runtime Service:**
- `ADKAgent__BaseUrl` - Python agent core URL

**Python Agent Core:**
- `PYTHONPATH` - Application path

### Database Configuration

The system uses SQL Server with Entity Framework Core. Database schema is automatically created on first run.

**Default Connection:**
```
Server: localhost,1433
Database: agentplatform
User Id: sa
Password: YourStrong@Passw0rd
```

## 📁 Project Structure

```
backend/
├── AgentPlatform.API/          # Main REST API
│   ├── Controllers/            # API endpoints
│   ├── Services/              # Business logic
│   ├── Models/                # Database entities
│   ├── DTOs/                  # Data transfer objects
│   └── Data/                  # Database context
├── AgentRuntime/              # Agent runtime service
├── ADKAgentCore/              # Python agent core
│   ├── agents/                # Agent implementations
│   │   ├── main_router_agent.py
│   │   ├── hr_bot.py
│   │   └── it_bot.py
│   └── main.py               # FastAPI application
├── shared/                    # Shared models
├── scripts/                   # Database scripts
└── docker-compose.yml        # Container orchestration
```

## 🔧 API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration

### Users
- `GET /api/users/profile` - Get user profile
- `PUT /api/users/profile` - Update profile

### Agents
- `GET /api/agents` - List all agents
- `POST /api/agents` - Create new agent
- `GET /api/agents/{id}` - Get agent details
- `PUT /api/agents/{id}` - Update agent
- `DELETE /api/agents/{id}` - Delete agent

### Chat
- `GET /api/chat/sessions` - Get chat sessions
- `POST /api/chat/sessions` - Create chat session
- `GET /api/chat/sessions/{id}/messages` - Get messages
- `POST /api/chat/sessions/{id}/messages` - Send message

### Files
- `POST /api/files/upload` - Upload file
- `GET /api/files/{id}` - Download file
- `DELETE /api/files/{id}` - Delete file

## 🗂️ Database Schema

### Core Tables
- **Users**: User accounts and authentication
- **Agents**: AI agent configurations
- **ChatSessions**: Chat conversation sessions
- **ChatMessages**: Individual chat messages
- **AgentFiles**: File attachments for agents
- **AgentFunctions**: Custom functions for agents

### Relationships
- Users can have multiple ChatSessions
- Agents can have multiple Files and Functions
- ChatSessions contain multiple ChatMessages

## 🐳 Docker Deployment

### Production Deployment

1. **Build and deploy:**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

2. **Environment variables:**
   ```env
   ASPNETCORE_ENVIRONMENT=Production
   ConnectionStrings__DefaultConnection=<production-connection>
   Jwt__Key=<secure-jwt-key>
   ```

## 🧪 Testing

### Unit Tests
```bash
dotnet test
```

### Integration Tests
```bash
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

## 🔍 Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Ensure SQL Server container is running
   - Verify connection string format
   - Check network connectivity

2. **JWT Authentication Failed**
   - Verify JWT key configuration
   - Check token expiration
   - Ensure correct issuer/audience

3. **Agent Core Unreachable**
   - Verify Python service is running
   - Check network configuration
   - Review agent core logs

### Logs and Monitoring

- **API Logs**: `./logs/log-{date}.txt`
- **Docker Logs**: `docker-compose logs [service]`
- **Database Logs**: SQL Server container logs

## 🚀 Production Considerations

### Security
- Use environment variables for secrets
- Enable HTTPS in production
- Configure proper CORS policies
- Set up proper authentication

### Performance
- Configure connection pooling
- Implement caching where appropriate
- Set up proper indexing
- Monitor resource usage

### Scalability
- Consider load balancing
- Database connection limits
- Agent runtime scaling
- File storage considerations

## 📈 Monitoring and Logging

The application uses **Serilog** for structured logging with:
- Console output for development
- File-based logging for production
- Configurable log levels
- Request/response logging

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests
5. Submit a pull request

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

**Built with ❤️ using .NET 8, FastAPI, and SQL Server** 