from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
from datetime import datetime
import logging

# Import agents
from agents.main_router_agent import MainRouterAgent
from agents.hr_bot import HRBot
from agents.it_bot import ITBot

app = FastAPI(title="Agent Platform ADK Core", version="1.0.0")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MessageHistory(BaseModel):
    role: str
    content: str
    agent_name: Optional[str] = None
    timestamp: datetime

class ChatRequest(BaseModel):
    message: str
    user_id: str
    session_id: Optional[str] = None
    agent_name: Optional[str] = None
    history: List[MessageHistory] = []
    context: Dict[str, Any] = {}

class ChatResponse(BaseModel):
    response: str
    agent_name: str
    session_id: Optional[str] = None
    success: bool = True
    error: Optional[str] = None
    metadata: Dict[str, Any] = {}

# Initialize agents
router_agent = MainRouterAgent()
hr_agent = HRBot()
it_agent = ITBot()

# Agent registry
agents = {
    "router": router_agent,
    "hr": hr_agent,
    "it": it_agent
}

@app.get("/")
async def root():
    return {"message": "Agent Platform ADK Core is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        logger.info(f"Received chat request from user {request.user_id}")
        
        # If no specific agent is requested, use the router
        agent_name = request.agent_name or "router"
        
        if agent_name not in agents:
            # Default to router if agent not found
            agent_name = "router"
        
        agent = agents[agent_name]
        
        # Process the message
        response = await agent.process_message(
            message=request.message,
            history=request.history,
            context=request.context
        )
        
        return ChatResponse(
            response=response["content"],
            agent_name=response.get("agent_name", agent_name),
            session_id=request.session_id,
            success=True,
            metadata=response.get("metadata", {})
        )
        
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        return ChatResponse(
            response="I apologize, but I encountered an error processing your request. Please try again.",
            agent_name=agent_name if 'agent_name' in locals() else "unknown",
            session_id=request.session_id,
            success=False,
            error=str(e)
        )

@app.post("/api/agents/{agent_id}/chat", response_model=ChatResponse)
async def chat_with_specific_agent(agent_id: str, request: ChatRequest):
    try:
        if agent_id not in agents:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
        
        agent = agents[agent_id]
        
        response = await agent.process_message(
            message=request.message,
            history=request.history,
            context=request.context
        )
        
        return ChatResponse(
            response=response["content"],
            agent_name=response.get("agent_name", agent_id),
            session_id=request.session_id,
            success=True,
            metadata=response.get("metadata", {})
        )
        
    except Exception as e:
        logger.error(f"Error processing chat request with agent {agent_id}: {str(e)}")
        return ChatResponse(
            response="I apologize, but I encountered an error processing your request. Please try again.",
            agent_name=agent_id,
            session_id=request.session_id,
            success=False,
            error=str(e)
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 