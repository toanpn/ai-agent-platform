# 🤖 AI Agent Platform - Backend

A multi-agent platform with department-specific AI agents that can handle HR, IT support, and general queries through a central router.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  AgentPlatform  │    │  AgentRuntime   │    │  ADKAgentCore   │
│      .API       │───▶│   (.NET 7)      │───▶│   (Python)      │
│   (.NET 7)      │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                                              │
         ▼                                              ▼
┌─────────────────┐                          ┌─────────────────┐
│   PostgreSQL    │                          │   Router Agent  │
│    Database     │                          │   HR Bot        │
│                 │                          │   IT Bot        │
└─────────────────┘                          └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- .NET 7 SDK (for local development)
- Python 3.11+ (for local development)

### 🐳 Docker Setup (Recommended)

1. **Clone and navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Start all services:**
   ```bash
   docker-compose up -d
   ```

3. **Verify services are running:**
   ```bash
   docker-compose ps
   ```

### 🌐 Service Endpoints

| Service | URL | Description |
|---------|-----|-------------|
| API | http://localhost:5000 | Main REST API |
| Runtime | http://localhost:5001 | Agent runtime service |
| ADK Core | http://localhost:8000 | Python agent core |
| Database | localhost:5432 | PostgreSQL database |
| Swagger UI | http://localhost:5000/swagger | API documentation |

## 📋 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user

### Chat
- `POST /api/chat/message` - Send message to agents
- `GET /api/chat/history` - Get chat history
- `GET /api/chat/sessions/{id}` - Get specific chat session
- `DELETE /api/chat/sessions/{id}` - Delete chat session

### Agents
- `GET /api/agent` - List user's agents
- `POST /api/agent` - Create new agent
- `GET /api/agent/{id}` - Get agent details
- `PUT /api/agent/{id}` - Update agent
- `DELETE /api/agent/{id}` - Delete agent
- `POST /api/agent/{id}/functions` - Add function to agent

### Files
- `POST /api/file/upload/{agentId}` - Upload file to agent
- `GET /api/file/{id}/download` - Download file
- `DELETE /api/file/{id}` - Delete file
- `POST /api/file/{id}/index` - Index file for RAG

## 🤖 Available Agents

### 1. Router Agent (Main)
- **Purpose**: Analyzes user messages and routes to appropriate department
- **Triggers**: Default for all unspecified requests
- **Capabilities**: 
  - Intent detection
  - Department routing
  - General assistance

### 2. HR Bot
- **Department**: Human Resources
- **Expertise**:
  - PTO/vacation requests
  - Benefits information
  - Payroll questions
  - Company policies
  - Employee handbook

### 3. IT Bot
- **Department**: Information Technology  
- **Expertise**:
  - Password resets
  - Email/Outlook issues
  - Hardware troubleshooting
  - Software installation
  - Network connectivity

## 💬 Example Chat Flow

```
User: "I need to reset my password"
↓
Router Agent: Analyzes message → Routes to IT
↓
IT Bot: Provides password reset instructions
```

```
User: "How many vacation days do I have?"
↓
Router Agent: Analyzes message → Routes to HR
↓
HR Bot: Provides PTO information and next steps
```

## 🛠️ Development Setup

### Local API Development

1. **Setup database:**
   ```bash
   docker-compose up postgres -d
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

The system uses PostgreSQL with Entity Framework Core. Database schema is automatically created on first run.

**Default Connection:**
```
Host: localhost
Database: agentplatform
Username: postgres
Password: postgres
Port: 5432
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
└── scripts/                   # Database scripts
```

## 🔐 Security Features

- JWT authentication
- Rate limiting
- CORS configuration
- Input validation
- Error handling middleware
- Secure file upload

## 📈 Monitoring & Logging

- Structured logging with Serilog
- Health check endpoints
- Request/response logging
- Error tracking

## 🚀 Deployment

### Production Deployment

1. **Update configuration:**
   - Change JWT keys
   - Update database connections
   - Configure production URLs

2. **Deploy with Docker:**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

### Scaling Considerations

- API can be horizontally scaled
- Database connection pooling configured
- Stateless agent processing
- File storage can be moved to cloud storage

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## 📝 API Testing

### Sample Requests

**Register User:**
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@company.com",
    "password": "SecurePass123",
    "firstName": "John",
    "lastName": "Doe",
    "department": "Engineering"
  }'
```

**Send Chat Message:**
```bash
curl -X POST http://localhost:5000/api/chat/message \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "message": "I need help with my password"
  }'
```

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Ensure PostgreSQL container is running
   - Check connection string configuration

2. **Agent Not Responding**
   - Verify Python agent core is running
   - Check runtime service connectivity

3. **Authentication Errors**
   - Verify JWT configuration
   - Check token expiration

### Logs Location

- API Logs: `./logs/`
- Container Logs: `docker-compose logs [service-name]`

## 📞 Support

For technical support or questions:
- Create an issue in the repository
- Check existing documentation
- Review API documentation at `/swagger`

---

**Built with ❤️ using .NET 7, FastAPI, and PostgreSQL** 