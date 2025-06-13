# AI Agent Platform

This repository contains a multi-agent platform with both frontend chatbot UI and backend services for handling AI agent interactions.

## Project Structure

```
ai-agent-platform/
├── chatbot-ui/               # Next.js frontend application
├── supabase/                 # Supabase configuration files
└── backend/                  # Backend services (.NET 7 + Python)
    ├── AgentPlatform.API/    # Main REST API (.NET 7)
    ├── shared/               # Shared models and utilities
    ├── ADKAgentCore/         # Python agent core (FastAPI)
    ├── scripts/              # Database setup scripts
    ├── ai-agent-platform.sln # Visual Studio solution file
    └── docker-compose.yml    # Docker orchestration
```

## Backend Setup

### Prerequisites

- Docker & Docker Compose
- .NET 7 SDK (for local development)
- Python 3.11+ (for local development)

### 🐳 Quick Start with Docker

1. **Navigate to backend directory:**
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

### 🌐 Backend Service Endpoints

| Service | URL | Description |
|---------|-----|-------------|
| API | http://localhost:5000 | Main REST API |
| ADK Core | http://localhost:8000 | Python agent core |
| Database | localhost:5432 | PostgreSQL database |
| Swagger UI | http://localhost:5000/swagger | API documentation |

### 🛠️ Local Development

**Build the solution:**
```bash
cd backend
dotnet build ai-agent-platform.sln
```

**Run API locally:**
```bash
cd backend/AgentPlatform.API
dotnet run
```

**Run Python Agent Core:**
```bash
cd backend/ADKAgentCore
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
python main.py
```

## Frontend Setup

### Prerequisites

- Node.js (v18 or later recommended)
- npm or yarn
- Supabase CLI

### Local Development Setup

#### 1. Set Up Supabase Locally

Install the Supabase CLI:

**MacOS/Linux**
```bash
brew install supabase/tap/supabase
```

**Windows**
```bash
scoop bucket add supabase https://github.com/supabase/scoop-bucket.git
scoop install supabase
```

Start Supabase:
```bash
supabase start
```

#### 2. Configure Environment Variables

```bash
cd chatbot-ui
cp .env.local.example .env.local
```

Get the required values by running:
```bash
supabase status
```

Fill in the values in your `.env.local` file:
- Use `API URL` from `supabase status` for `NEXT_PUBLIC_SUPABASE_URL`
- Use `anon key` for `NEXT_PUBLIC_SUPABASE_ANON_KEY`
- Use `service_role_key` for appropriate variables

#### 3. Configure SQL Setup

In the migration file `supabase/migrations/20240108234540_setup.sql`, update:
- `project_url` (line 53): Should be `http://supabase_kong_chatbotui:8000` by default
- `service_role_key` (line 54): Use the value from `supabase status`

#### 4. Install Dependencies and Run

```bash
cd chatbot-ui
npm install
npm run chat
```

Your local instance should now be running at [http://localhost:3000](http://localhost:3000).

## Available AI Agents

### 1. Router Agent (Main)
- **Purpose**: Analyzes user messages and routes to appropriate department
- **Capabilities**: Intent detection, department routing, general assistance

### 2. HR Bot
- **Department**: Human Resources
- **Expertise**: PTO/vacation requests, benefits information, payroll questions, company policies

### 3. IT Bot
- **Department**: Information Technology  
- **Expertise**: Password resets, email/Outlook issues, hardware troubleshooting, software installation

## Production Deployment

### Backend Deployment

1. **Update configuration:**
   - Change JWT keys
   - Update database connections
   - Configure production URLs

2. **Deploy with Docker:**
   ```bash
   cd backend
   docker-compose -f docker-compose.prod.yml up -d
   ```

### Frontend Deployment

#### 1. Create a Supabase Project

Go to [Supabase](https://supabase.com/) and create a new project.

#### 2. Configure Authentication

In the Supabase dashboard:
- Go to Authentication → Providers
- Enable Email provider
- Configure other settings as needed

#### 3. Connect to Hosted Database

Get your project values from the Supabase dashboard:
- Project URL
- Project ID
- Anon key
- Service role key

Link your project:
```bash
supabase login
supabase link --project-ref <project-id>
```

Apply migrations:
```bash
supabase db push
```

#### 4. Deploy Frontend

The chatbot-ui is a Next.js application that can be deployed to platforms like Vercel:

```bash
cd chatbot-ui
npm run build
```

Follow the deployment instructions for your chosen hosting platform (Vercel, Netlify, etc.).

## Features

### Backend Features
- Multi-agent architecture with department-specific bots
- JWT authentication and authorization
- PostgreSQL database with Entity Framework Core
- RESTful API with OpenAPI/Swagger documentation
- Docker containerization
- Rate limiting and security middleware
- Structured logging with Serilog

### Frontend Features
- Modern chat interface
- Integration with various AI models
- User authentication
- Conversation history storage
- Customizable UI

## API Testing

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

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the terms of the MIT license.
