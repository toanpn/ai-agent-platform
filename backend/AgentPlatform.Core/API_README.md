# AgentPlatform.Core API Server

This document describes how to run the AgentPlatform.Core as an API server to integrate with the AgentPlatform.API (.NET application).

## Overview

The AgentPlatform.Core now exposes a Flask-based REST API that allows the .NET API to communicate with the agent system. The API server wraps the existing `AgentSystemManager` functionality and provides HTTP endpoints.

## Setup

### 1. Install Dependencies

```bash
# Make sure you're in the AgentPlatform.Core directory
cd backend/AgentPlatform.Core

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

Make sure you have a `.env` file with your Google API key:

```env
GOOGLE_API_KEY=your_google_api_key_here
PORT=8000
FLASK_ENV=development
```

### 3. Agent Configuration

Ensure your `agents.json` file is configured with the agents you want to use.

## Running the API Server

### Option 1: Using the startup script (Recommended)

```bash
python start_api.py
```

### Option 2: Direct execution

```bash
python api_server.py
```

The server will start on `http://localhost:8000` by default.

## API Endpoints

### Health Check
- **GET** `/health`
- Returns server health status

### Chat Endpoint
- **POST** `/api/chat`
- Main endpoint for processing user messages
- **Request Body:**
  ```json
  {
    "message": "Your message here",
    "userId": "user123",
    "sessionId": "session123",
    "agentName": "optional_agent_name"
  }
  ```
- **Response:**
  ```json
  {
    "success": true,
    "response": "Agent response here",
    "agentName": "MasterAgent",
    "sessionId": "session123",
    "metadata": {
      "timestamp": "2024-01-01T12:00:00Z",
      "userId": "user123"
    }
  }
  ```

### Agent Information
- **GET** `/api/agents`
- Returns information about loaded agents

### Reload Configuration
- **POST** `/api/reload`
- Reloads the agent configuration from `agents.json`

## Integration with AgentPlatform.API

The .NET API is already configured to communicate with this Flask server:

1. The `AgentRuntimeClient` in the .NET API sends requests to `http://localhost:5001/api/chat`
2. The configuration is in `appsettings.json` under `AgentRuntime.BaseUrl`
3. The communication uses the shared models defined in `AgentPlatform.Shared.Models`

## Running Both Services

1. **Start the Python API server:**
   ```bash
   cd backend/AgentPlatform.Core
   python start_api.py
   ```

2. **Start the .NET API (in another terminal):**
   ```bash
   cd backend/AgentPlatform.API
   dotnet run
   ```

The .NET API will automatically connect to the Python API server and route chat requests through it.

## Troubleshooting

### Common Issues

1. **Port 8000 already in use:**
   - Change the `PORT` environment variable
   - Update `appsettings.json` in the .NET API accordingly

2. **Google API Key not found:**
   - Make sure the `.env` file exists and contains `GOOGLE_API_KEY`
   - Check that the environment variable is properly loaded

3. **Agents not loading:**
   - Verify `agents.json` exists and is valid JSON
   - Check the agent configuration format

4. **Connection refused from .NET API:**
   - Ensure the Python API server is running
   - Check that the `AgentRuntime.BaseUrl` in `appsettings.json` matches the Python server URL

## Logs

The API server provides detailed logging:
- INFO level logs for successful operations
- ERROR level logs for failures
- Request/response logging for debugging

## Development

For development, set `FLASK_ENV=development` in your `.env` file to enable:
- Auto-reload on code changes
- Debug mode
- Detailed error messages 