"""
API endpoint for chat interactions with agents using Google ADK.
"""

import logging
import os
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from ...models.schemas import ChatRequest, ChatResponse, ErrorResponse
from ...database.connection import get_db_session
from ...database.repositories.agent_repository import AgentRepository
from ...agents.adk_agents import ADKAgentRuntime

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize ADK agent runtime
_adk_agent_runtime = None


def get_adk_agent_runtime() -> ADKAgentRuntime:
    """
    Get or create ADK agent runtime instance.
    
    Returns:
        ADKAgentRuntime: ADK agent runtime instance
    """
    global _adk_agent_runtime
    if _adk_agent_runtime is None:
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            raise HTTPException(
                status_code=500,
                detail="Google API key not configured"
            )
        _adk_agent_runtime = ADKAgentRuntime(google_api_key)
    return _adk_agent_runtime


# TODO: Implement proper authentication and authorization
async def get_current_user_id() -> int:
    """
    Placeholder for user authentication.
    
    Returns:
        int: Current user ID
    """
    # For now, return a placeholder user ID (as integer to match database)
    # In production, this should extract user ID from JWT token or session
    return 1


def get_agent_repository(db: Session = Depends(get_db_session)) -> AgentRepository:
    """
    Get agent repository instance.
    
    Args:
        db: Database session
        
    Returns:
        AgentRepository: Agent repository instance
    """
    return AgentRepository(db)


@router.post("/", response_model=ChatResponse)
async def chat_with_agent(
    request: ChatRequest,
    current_user_id: int = Depends(get_current_user_id),
    agent_repo: AgentRepository = Depends(get_agent_repository),
    adk_runtime: ADKAgentRuntime = Depends(get_adk_agent_runtime)
):
    """
    Chat with an agent using Google ADK Agent Runtime system.
    
    Args:
        request: Chat request containing agent ID, session ID, and user message
        current_user_id: ID of the current user
        agent_repo: Agent repository instance
        adk_runtime: ADK agent runtime instance
        
    Returns:
        ChatResponse: Agent's response to the user message
    """
    logger.info(
        f"ADK Chat request from user {current_user_id} to agent {request.agent_id} "
        f"in session {request.session_id}"
    )
    
    try:
        # Retrieve agent configuration from database
        agent_config = agent_repo.get_agent_by_id(request.agent_id)
        
        if not agent_config:
            raise HTTPException(
                status_code=404,
                detail=f"Agent with ID '{request.agent_id}' not found"
            )
        
        if not agent_config.is_active:
            raise HTTPException(
                status_code=400,
                detail=f"Agent '{request.agent_id}' is not active"
            )
        
        # Get tool credentials (in production, these would come from secure storage)
        credentials = _get_tool_credentials()
        
        # Process the chat request using ADK Agent Runtime
        response = await adk_runtime.process_chat(
            agent_config=agent_config,
            chat_request=request,
            credentials=credentials
        )
        
        # TODO: Store chat message in database (ChatSessions and ChatMessages tables)
        # This would involve:
        # 1. Creating or finding the chat session
        # 2. Storing the user message
        # 3. Storing the agent response
        
        logger.info(f"ADK Chat response generated for session {response.session_id}")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing ADK chat request: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your request"
        )


@router.get("/sessions/{session_id}/history")
async def get_chat_history(
    session_id: int,
    current_user_id: int = Depends(get_current_user_id),
    limit: int = 50
):
    """
    Get chat history for a session.
    
    Args:
        session_id: Session ID
        current_user_id: ID of the current user
        limit: Maximum number of messages to return
        
    Returns:
        dict: Chat history
    """
    logger.info(f"Retrieving chat history for session {session_id}")
    
    # TODO: Implement chat history retrieval from database using ChatSessions and ChatMessages tables
    # For now, return a placeholder response
    
    return {
        "session_id": session_id,
        "messages": [
            {
                "role": "user",
                "content": "Hello, how are you?",
                "timestamp": "2024-01-01T10:00:00Z"
            },
            {
                "role": "assistant",
                "content": "Hello! I'm doing well, thank you for asking. How can I help you today?",
                "timestamp": "2024-01-01T10:00:01Z"
            }
        ],
        "total": 2
    }


@router.get("/agents/{agent_id}/tools")
async def get_agent_tools(
    agent_id: int,
    current_user_id: int = Depends(get_current_user_id),
    agent_repo: AgentRepository = Depends(get_agent_repository),
    adk_runtime: ADKAgentRuntime = Depends(get_adk_agent_runtime)
):
    """
    Get available tools for an agent.
    
    Args:
        agent_id: Agent ID
        current_user_id: ID of the current user
        agent_repo: Agent repository instance
        adk_runtime: ADK agent runtime instance
        
    Returns:
        dict: Available tools for the agent
    """
    logger.info(f"Getting tools for agent {agent_id}")
    
    try:
        # Get agent configuration
        agent_config = agent_repo.get_agent_by_id(agent_id)
        
        if not agent_config:
            raise HTTPException(
                status_code=404,
                detail=f"Agent with ID '{agent_id}' not found"
            )
        
        # Get available tools information
        tools_info = []
        for function in agent_config.functions:
            tools_info.append({
                "id": function.id,
                "name": function.name,
                "description": function.description,
                "schema": function.schema,
                "is_active": function.is_active
            })
        
        return {
            "agent_id": agent_id,
            "agent_name": agent_config.name,
            "tools": tools_info,
            "total_tools": len(tools_info),
            "runtime": "Google ADK"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent tools: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while retrieving agent tools"
        )


@router.post("/agents/{agent_id}/validate-credentials")
async def validate_agent_credentials(
    agent_id: int,
    credentials: dict,
    current_user_id: int = Depends(get_current_user_id),
    agent_repo: AgentRepository = Depends(get_agent_repository),
    adk_runtime: ADKAgentRuntime = Depends(get_adk_agent_runtime)
):
    """
    Validate credentials for an agent's tools.
    
    Args:
        agent_id: Agent ID
        credentials: Credentials to validate
        current_user_id: ID of the current user
        agent_repo: Agent repository instance
        adk_runtime: ADK agent runtime instance
        
    Returns:
        dict: Validation results
    """
    logger.info(f"Validating credentials for agent {agent_id}")
    
    try:
        # Get agent configuration
        agent_config = agent_repo.get_agent_by_id(agent_id)
        
        if not agent_config:
            raise HTTPException(
                status_code=404,
                detail=f"Agent with ID '{agent_id}' not found"
            )
        
        # For now, return a simple validation result
        # In production, this would test each tool's credentials
        validation_results = {}
        
        for function in agent_config.functions:
            # Simple validation logic - check if required keys exist
            validation_results[function.name] = {
                "valid": True,  # Placeholder
                "message": "Credentials appear valid"
            }
        
        return {
            "agent_id": agent_id,
            "validation_results": validation_results,
            "overall_valid": all(result["valid"] for result in validation_results.values()),
            "runtime": "Google ADK"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating credentials: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while validating credentials"
        )


@router.post("/agents/{agent_id}/multi-agent")
async def create_multi_agent_chat(
    agent_id: int,
    request: ChatRequest,
    orchestration_type: str = "sequential",
    current_user_id: int = Depends(get_current_user_id),
    agent_repo: AgentRepository = Depends(get_agent_repository),
    adk_runtime: ADKAgentRuntime = Depends(get_adk_agent_runtime)
):
    """
    Create a multi-agent chat session with ADK workflow agents.
    
    Args:
        agent_id: Primary agent ID
        request: Chat request
        orchestration_type: "sequential", "parallel", or "loop"
        current_user_id: ID of the current user
        agent_repo: Agent repository instance
        adk_runtime: ADK agent runtime instance
        
    Returns:
        ChatResponse: Multi-agent response
    """
    logger.info(f"Creating multi-agent chat with orchestration: {orchestration_type}")
    
    try:
        # Get related agents (for now, just use the requested agent)
        # In production, this could discover related agents by department or function
        agent_config = agent_repo.get_agent_by_id(agent_id)
        
        if not agent_config:
            raise HTTPException(
                status_code=404,
                detail=f"Agent with ID '{agent_id}' not found"
            )
        
        # For now, create a single-agent workflow
        # This can be extended to include multiple agents
        credentials = _get_tool_credentials()
        
        # Create multi-agent system
        multi_agent = adk_runtime.factory.create_multi_agent_system(
            agent_configs=[agent_config],
            orchestration_type=orchestration_type,
            credentials=credentials
        )
        
        # Process request with multi-agent system
        result = await multi_agent.run(
            input_data=request.user_message,
            context={
                "session_id": request.session_id,
                "chat_history": request.chat_history or []
            }
        )
        
        # Convert result to ChatResponse
        response = ChatResponse(
            response=result.output,
            sources=[{
                "type": "multi_agent_result",
                "orchestration": orchestration_type,
                "agents_used": [agent_config.name],
                "title": f"Multi-Agent {orchestration_type.title()} Result"
            }],
            session_id=request.session_id or 1
        )
        
        logger.info(f"Multi-agent chat completed with {orchestration_type} orchestration")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in multi-agent chat: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing multi-agent request"
        )


def _get_tool_credentials() -> dict:
    """
    Get tool credentials from environment variables.
    In production, this should use a secure credential store.
    
    Returns:
        dict: Tool credentials
    """
    return {
        # Jira credentials
        "jira_url": os.getenv("JIRA_URL", "https://your-domain.atlassian.net"),
        "jira_username": os.getenv("JIRA_USERNAME"),
        "jira_api_token": os.getenv("JIRA_API_TOKEN"),
        
        # Google Calendar credentials
        "google_calendar_credentials_file": os.getenv("GOOGLE_CALENDAR_CREDENTIALS_FILE"),
        "google_calendar_token_file": os.getenv("GOOGLE_CALENDAR_TOKEN_FILE"),
        
        # Confluence credentials
        "confluence_url": os.getenv("CONFLUENCE_URL", "https://your-domain.atlassian.net/wiki"),
        "confluence_username": os.getenv("CONFLUENCE_USERNAME"),
        "confluence_api_token": os.getenv("CONFLUENCE_API_TOKEN"),
    } 