"""
Pydantic models for API requests/responses and data structures.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


class AgentFunction(BaseModel):
    """
    Represents a function/tool available to an agent.
    """
    id: Optional[int] = Field(None, description="Function ID")
    agent_id: Optional[int] = Field(None, description="Agent ID this function belongs to")
    name: str = Field(..., description="Function name")
    description: Optional[str] = Field(None, description="Function description")
    schema: Optional[str] = Field(None, description="JSON schema for function parameters")
    endpoint_url: Optional[str] = Field(None, description="HTTP endpoint URL for the function")
    http_method: str = Field("POST", description="HTTP method")
    headers: Optional[str] = Field(None, description="JSON string for HTTP headers")
    is_active: bool = Field(True, description="Whether the function is active")
    created_at: Optional[datetime] = Field(None, description="When the function was created")
    updated_at: Optional[datetime] = Field(None, description="When the function was last updated")


class AgentFile(BaseModel):
    """
    Represents a file associated with an agent.
    """
    id: Optional[int] = Field(None, description="File ID")
    agent_id: Optional[int] = Field(None, description="Agent ID this file belongs to")
    file_name: str = Field(..., description="Original file name")
    file_path: str = Field(..., description="Path to the stored file")
    file_size: int = Field(..., description="File size in bytes")
    content_type: str = Field(..., description="MIME type of the file")
    uploaded_at: Optional[datetime] = Field(None, description="When the file was uploaded")


class AgentConfig(BaseModel):
    """
    Configuration for an AI agent (matching .NET API structure).
    """
    id: Optional[int] = Field(None, description="Agent ID (auto-generated)")
    name: str = Field(..., description="Human-readable name for the agent")
    department: str = Field(..., description="Department the agent belongs to")
    description: Optional[str] = Field(None, description="Description of the agent's purpose")
    instructions: Optional[str] = Field(None, description="Instructions for the agent")
    is_active: bool = Field(True, description="Whether the agent is active")
    is_main_router: bool = Field(False, description="Whether this is a main router agent")
    created_by_id: int = Field(..., description="User ID of the agent creator")
    created_at: Optional[datetime] = Field(None, description="When the agent was created")
    updated_at: Optional[datetime] = Field(None, description="When the agent was last updated")
    
    # Navigation properties
    files: List[AgentFile] = Field(default_factory=list, description="Files associated with the agent")
    functions: List[AgentFunction] = Field(default_factory=list, description="Functions available to the agent")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class User(BaseModel):
    """
    User model (matching .NET API structure).
    """
    id: Optional[int] = Field(None, description="User ID")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email address")
    full_name: Optional[str] = Field(None, description="Full name")
    department: Optional[str] = Field(None, description="Department")
    is_active: bool = Field(True, description="Whether the user is active")
    created_at: Optional[datetime] = Field(None, description="When the user was created")
    updated_at: Optional[datetime] = Field(None, description="When the user was last updated")


class ChatSession(BaseModel):
    """
    Chat session model (matching .NET API structure).
    """
    id: Optional[int] = Field(None, description="Session ID")
    user_id: int = Field(..., description="User ID")
    agent_id: int = Field(..., description="Agent ID")
    session_name: Optional[str] = Field(None, description="Session name")
    created_at: Optional[datetime] = Field(None, description="When the session was created")
    updated_at: Optional[datetime] = Field(None, description="When the session was last updated")


class ChatMessage(BaseModel):
    """
    Chat message model (matching .NET API structure).
    """
    id: Optional[int] = Field(None, description="Message ID")
    session_id: int = Field(..., description="Session ID")
    role: str = Field(..., description="Message role (user/assistant)")
    content: str = Field(..., description="Message content")
    timestamp: Optional[datetime] = Field(None, description="Message timestamp")


class ChatRequest(BaseModel):
    """
    Request model for chat interactions with an agent.
    """
    agent_id: int = Field(..., description="ID of the agent to use for the chat")
    session_id: Optional[int] = Field(None, description="Session ID for conversation continuity")
    user_message: str = Field(..., description="The user's message to the agent")
    chat_history: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Previous chat history for context"
    )


class ChatResponse(BaseModel):
    """
    Response model for chat interactions.
    """
    response: str = Field(..., description="The agent's response to the user")
    sources: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Sources or references used in generating the response"
    )
    session_id: int = Field(..., description="Session ID for conversation continuity")


class CreateAgentRequest(BaseModel):
    """
    Request model for creating a new agent.
    """
    name: str = Field(..., description="Human-readable name for the agent")
    department: str = Field(..., description="Department the agent belongs to")
    description: Optional[str] = Field(None, description="Description of the agent's purpose")
    instructions: Optional[str] = Field(None, description="Instructions for the agent")
    is_active: bool = Field(True, description="Whether the agent is active")
    is_main_router: bool = Field(False, description="Whether this is a main router agent")
    functions: List[AgentFunction] = Field(default_factory=list, description="Functions to associate with the agent")


class UpdateAgentRequest(BaseModel):
    """
    Request model for updating an existing agent.
    """
    name: Optional[str] = Field(None, description="Human-readable name for the agent")
    department: Optional[str] = Field(None, description="Department the agent belongs to")
    description: Optional[str] = Field(None, description="Description of the agent's purpose")
    instructions: Optional[str] = Field(None, description="Instructions for the agent")
    is_active: Optional[bool] = Field(None, description="Whether the agent is active")
    is_main_router: Optional[bool] = Field(None, description="Whether this is a main router agent")
    functions: Optional[List[AgentFunction]] = Field(None, description="Functions to associate with the agent")


class AgentListResponse(BaseModel):
    """
    Response model for listing agents.
    """
    agents: List[AgentConfig] = Field(..., description="List of agent configurations")
    total: int = Field(..., description="Total number of agents")


class ErrorResponse(BaseModel):
    """
    Standard error response model.
    """
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional error details")
    code: Optional[str] = Field(None, description="Error code") 