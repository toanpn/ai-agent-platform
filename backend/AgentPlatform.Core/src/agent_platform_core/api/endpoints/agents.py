"""
API endpoints for agent operations (Read-only for runtime).
"""

import logging
from typing import List
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ...models.schemas import (
    AgentConfig,
    AgentListResponse,
    ErrorResponse
)
from ...database.connection import get_db_session
from ...database.repositories.agent_repository import AgentRepository

logger = logging.getLogger(__name__)

router = APIRouter()


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


@router.get("/{agent_id}", response_model=AgentConfig)
async def get_agent(
    agent_id: int,
    current_user_id: int = Depends(get_current_user_id),
    agent_repo: AgentRepository = Depends(get_agent_repository)
):
    """
    Get agent configuration by ID for runtime use.
    
    Args:
        agent_id: Agent ID
        current_user_id: ID of the current user
        agent_repo: Agent repository instance
        
    Returns:
        AgentConfig: Agent configuration
    """
    logger.info(f"Retrieving agent '{agent_id}' for runtime use by user {current_user_id}")
    
    try:
        # For runtime, we don't restrict by user - any active agent can be used
        agent_config = agent_repo.get_agent_by_id(agent_id)
        
        if not agent_config:
            raise HTTPException(
                status_code=404,
                detail=f"Agent with ID '{agent_id}' not found"
            )
        
        if not agent_config.is_active:
            raise HTTPException(
                status_code=400,
                detail=f"Agent '{agent_id}' is not active"
            )
        
        return agent_config
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving agent {agent_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve agent"
        )


@router.get("/", response_model=AgentListResponse)
async def list_available_agents(
    current_user_id: int = Depends(get_current_user_id),
    agent_repo: AgentRepository = Depends(get_agent_repository),
    limit: int = 10,
    offset: int = 0,
    department: str = None
):
    """
    List available agents for runtime use.
    
    Args:
        current_user_id: ID of the current user
        agent_repo: Agent repository instance
        limit: Maximum number of agents to return
        offset: Number of agents to skip
        department: Optional department filter
        
    Returns:
        AgentListResponse: List of available agent configurations
    """
    logger.info(f"Listing available agents for runtime (limit={limit}, offset={offset})")
    
    try:
        # For runtime, we can list all active agents or filter by department
        agents, total = agent_repo.list_active_agents(limit, offset, department)
        
        return AgentListResponse(
            agents=agents,
            total=total
        )
        
    except Exception as e:
        logger.error(f"Error listing available agents: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to list agents"
        )


@router.get("/department/{department}", response_model=AgentListResponse)
async def list_agents_by_department(
    department: str,
    current_user_id: int = Depends(get_current_user_id),
    agent_repo: AgentRepository = Depends(get_agent_repository),
    limit: int = 10,
    offset: int = 0
):
    """
    List agents by department for runtime routing.
    
    Args:
        department: Department name
        current_user_id: ID of the current user
        agent_repo: Agent repository instance
        limit: Maximum number of agents to return
        offset: Number of agents to skip
        
    Returns:
        AgentListResponse: List of agents in the department
    """
    logger.info(f"Listing agents for department '{department}' (limit={limit}, offset={offset})")
    
    try:
        agents, total = agent_repo.list_active_agents(limit, offset, department)
        
        return AgentListResponse(
            agents=agents,
            total=total
        )
        
    except Exception as e:
        logger.error(f"Error listing agents for department {department}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to list agents by department"
        ) 