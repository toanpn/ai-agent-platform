# **AgentPlatform.Core - Google ADK Runtime**

🚀 **Production-Ready AI Agent Platform with Google ADK**

A modern, scalable AI agent runtime service built with [Google ADK (Agent Development Kit)](https://google.github.io/adk-docs/). This service processes chat interactions with AI agents by loading configurations from a shared database and executing AI-powered conversations with integrated tools.

## 🌟 **Key Features**

- ✅ **Google ADK Integration** - Production-ready agent framework v1.0.0
- ✅ **Multi-Agent Workflows** - Sequential, Parallel, and Loop orchestration
- ✅ **Database Integration** - Shared SQL Server with AgentPlatform.API
- ✅ **Tool Ecosystem** - Jira, Calendar, Confluence + ADK built-in tools
- ✅ **Deployment Ready** - Docker, Cloud Run, Vertex AI support

## 🏗️ **Architecture**

```
┌─────────────────────────────────────────────┐
│            AgentPlatform.Core               │
│         (Google ADK Runtime)                │
├─────────────────────────────────────────────┤
│  FastAPI Web Layer                         │
│  ├── Chat API (/api/v1/chat/)               │
│  ├── Multi-Agent (/agents/{id}/multi-agent) │
│  └── Tool Management                       │
├─────────────────────────────────────────────┤
│  Google ADK Agents                         │
│  ├── LlmAgent (Individual agents)          │
│  ├── SequentialAgent (Workflows)           │
│  ├── ParallelAgent (Concurrent)            │
│  └── LoopAgent (Iterative)                 │
├─────────────────────────────────────────────┤
│  Tools & Integrations                      │
│  ├── ADK Built-in (Search, HTTP, File)     │
│  ├── Custom Tools (Jira, Calendar, etc.)   │
│  └── Google Cloud Tools                    │
├─────────────────────────────────────────────┤
│  Data Layer                                │
│  ├── SQL Server (Shared with .NET API)     │
│  ├── Agent Configurations                  │
│  └── Chat Sessions & History               │
└─────────────────────────────────────────────┘
```

## 📋 **Prerequisites**

- **Python 3.10+** (required for Google ADK)
- **Google API Key** for Gemini
- **SQL Server** (shared with AgentPlatform.API)
- **Docker** (optional)

## 🚀 **Quick Start**

### **1. Setup Environment**
```bash
# Navigate to project
cd backend/AgentPlatform.Core

# Run ADK setup
python setup_adk.py
```

### **2. Configure Credentials**
Edit `.env` file:
```bash
GOOGLE_API_KEY=your_google_api_key
DATABASE_URL=mssql+pyodbc://sa:password@localhost:1433/agentplatform?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes
```

### **3. Start Application**
```bash
# Development
python -m uvicorn agent_platform_core.main:app --reload

# Docker
docker-compose up --build
```

### **4. Test Integration**
Visit: `http://localhost:8000/docs`

## 🛠️ **Project Structure**

```
AgentPlatform.Core/
├── src/agent_platform_core/
│   ├── agents/
│   │   ├── adk_agents.py          # ADK agent factory & runtime
│   │   └── __init__.py            # Clean exports
│   ├── tools/
│   │   ├── adk_tools.py           # ADK tools adapter
│   │   ├── registry.py            # Tool registry
│   │   ├── jira.py                # Jira integration
│   │   ├── google_calendar.py     # Calendar integration
│   │   └── confluence.py          # Confluence integration
│   ├── api/endpoints/
│   │   ├── chat.py                # ADK-powered chat API
│   │   └── agents.py              # Agent management
│   ├── database/                  # SQL Server integration
│   ├── models/                    # Pydantic models
│   └── main.py                    # FastAPI application
├── adk_config.py                  # ADK configuration
├── setup_adk.py                   # Setup script
├── requirements.txt               # Dependencies
├── Dockerfile                     # Container config
├── docker-compose.yml             # Local development
└── README_ADK.md                  # Detailed ADK guide
```

## 🌐 **API Endpoints**

### **Core Chat API**
- `POST /api/v1/chat/` - Chat with ADK agents
- `GET /api/v1/chat/sessions/{id}/history` - Chat history

### **Multi-Agent Workflows**
- `POST /api/v1/chat/agents/{id}/multi-agent` - Multi-agent orchestration

### **Agent Management**
- `GET /api/v1/agents/{id}` - Get agent configuration
- `GET /api/v1/chat/agents/{id}/tools` - Get agent tools

## 🚢 **Deployment Options**

### **Local Development**
```bash
docker-compose up --build
```

### **Cloud Deployment**
```bash
# Vertex AI Agent Engine
gcloud ai agents deploy --config=adk_config.py

# Cloud Run
gcloud run deploy agent-platform-core --source .
```

## 📊 **Monitoring**

- **Health**: `GET /health`
- **Database**: `GET /health/db`
- **Logs**: Comprehensive ADK logging

## 📚 **Documentation**

- **ADK Integration Guide**: `README_ADK.md`
- **Google ADK Docs**: https://google.github.io/adk-docs/
- **API Reference**: `http://localhost:8000/docs`

## 🔧 **Configuration**

Key configuration in `adk_config.py`:
- ADK Runtime settings
- Multi-agent workflows
- Tool configurations
- Deployment options

---

**🎉 Powered by Google ADK for production-ready AI agents!** 