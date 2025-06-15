# 🤖 AI Agent Platform

A comprehensive platform for creating, managing, and interacting with specialized AI agents. Built with modern web technologies and a microservices architecture.

## 🏗️ Architecture Overview

This platform consists of multiple specialized AI agents that can handle different domains (HR, IT, General Support) through a central routing system.

### Services Overview

| Service | Port | Technology | Description |
|---------|------|------------|-------------|
| Frontend | 3000 | Next.js + React | Modern web interface |
| Backend API | 5000 | .NET 8 | REST API and business logic |
| Database | 1433 | SQL Server | Data persistence |
| Agent Core | 8000 | Python FastAPI | AI agent runtime |

### 🎯 Key Features

- **Multi-Agent System**: Specialized agents for different departments
- **Intelligent Routing**: Automatic message routing to appropriate agents
- **Real-time Chat**: WebSocket-based real-time messaging
- **File Management**: Upload and process documents for agent knowledge
- **User Management**: Secure authentication and user profiles
- **Modern UI**: Clean, responsive interface built with React/Next.js

## 🚀 Quick Start

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- [Node.js 18+](https://nodejs.org/) (for frontend development)
- [.NET 8 SDK](https://dotnet.microsoft.com/download/dotnet/8.0) (for backend development)

### Running with Docker

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd ai-agent-platform
   ```

2. **Start the backend services:**
   ```bash
   cd backend
   docker-compose up -d
   ```

3. **Start the frontend:**
   ```bash
   cd chatbot-ui
   npm install
   npm run dev
   ```

4. **Access the applications:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000
   - API Documentation: http://localhost:5000/swagger

## 🛠️ Technology Stack

### Frontend
- **Framework**: Next.js 14 with React 18
- **Styling**: Tailwind CSS
- **UI Components**: Radix UI
- **State Management**: Zustand
- **Database**: Supabase (PostgreSQL)
- **Authentication**: Supabase Auth

### Backend
- **API**: .NET 8 Web API
- **Database**: SQL Server with Entity Framework Core
- **Authentication**: JWT Bearer tokens
- **Logging**: Serilog
- **Rate Limiting**: AspNetCoreRateLimit
- **Agent Runtime**: Python FastAPI

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Database**: SQL Server
- **File Storage**: Local file system (configurable)

## 🤖 Available Agents

### 🎯 Router Agent (Main)
- **Purpose**: Analyzes incoming messages and routes to appropriate specialized agents
- **Capabilities**: Intent detection, department routing, general assistance

### 👥 HR Agent
- **Department**: Human Resources
- **Expertise**: PTO requests, benefits, payroll, company policies, employee handbook

### 🖥️ IT Agent  
- **Department**: Information Technology
- **Expertise**: Password resets, email issues, hardware troubleshooting, software installation

## 📁 Project Structure

```
ai-agent-platform/
├── backend/                    # .NET 8 Backend
│   ├── AgentPlatform.API/     # Main REST API
│   ├── ADKAgentCore/          # Python Agent Runtime
│   ├── shared/                # Shared models
│   └── docker-compose.yml    # Backend services
├── chatbot-ui/                # Next.js Frontend
│   ├── components/            # React components
│   ├── app/                   # Next.js app directory
│   ├── lib/                   # Utilities and helpers
│   └── supabase/             # Database migrations
└── docs/                      # Documentation
```

## 🔧 Development

### Backend Development

```bash
cd backend
docker-compose up -d sqlserver  # Start database
cd AgentPlatform.API
dotnet run                      # Start API
```

### Frontend Development

```bash
cd chatbot-ui
npm install
npm run dev
```

### Agent Development

```bash
cd backend/ADKAgentCore
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

## 🌟 Features

### For End Users
- **Multi-Agent Chat**: Seamless conversation with specialized AI agents
- **Department Routing**: Automatic routing to HR, IT, or general support
- **File Upload**: Share documents for agent analysis
- **Chat History**: Access previous conversations
- **Responsive Design**: Works on desktop and mobile

### For Administrators
- **Agent Management**: Create and configure custom agents
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

## 📈 Monitoring & Logging

- Structured logging with Serilog
- Request/response logging
- Error tracking and reporting
- Health check endpoints
- Docker container logging

## 🚀 Deployment

### Production Deployment

1. **Configure environment variables**
2. **Set up SSL certificates**
3. **Configure production database**
4. **Deploy with Docker Compose**

### Environment Variables

```env
# Backend
ConnectionStrings__DefaultConnection=<sql-server-connection>
Jwt__Key=<secure-jwt-key>
ASPNETCORE_ENVIRONMENT=Production

# Frontend
NEXT_PUBLIC_API_URL=<backend-api-url>
NEXT_PUBLIC_SUPABASE_URL=<supabase-url>
NEXT_PUBLIC_SUPABASE_ANON_KEY=<supabase-key>
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📧 Email: support@agentplatform.com
- 📖 Documentation: [docs/](./docs/)
- 🐛 Issues: [GitHub Issues](../../issues)

---

**Built with ❤️ using Next.js, .NET 8, and SQL Server**
