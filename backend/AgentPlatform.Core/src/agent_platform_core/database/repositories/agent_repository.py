"""
Agent repository for database CRUD operations.
"""

import logging
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text

from ...models.schemas import AgentConfig, CreateAgentRequest, UpdateAgentRequest

logger = logging.getLogger(__name__)


class AgentRepository:
    """
    Repository for agent-related database operations.
    """
    
    def __init__(self, db_session: Session):
        """
        Initialize the repository with a database session.
        
        Args:
            db_session: SQLAlchemy database session
        """
        self.db = db_session
    
    def get_agent_by_id(self, agent_id: int, user_id: int = None) -> Optional[AgentConfig]:
        """
        Get an agent by ID.
        
        Args:
            agent_id: Agent ID
            user_id: Optional user ID for access control
            
        Returns:
            AgentConfig: Agent configuration or None if not found
        """
        try:
            # Query agent with optional user filter
            query = text("""
                SELECT Id, Name, Department, Description, Instructions, IsActive, IsMainRouter, 
                       CreatedById, CreatedAt, UpdatedAt
                FROM Agents 
                WHERE Id = :agent_id
            """)
            
            params = {"agent_id": agent_id}
            
            # Add user filter if provided
            if user_id:
                query = text("""
                    SELECT Id, Name, Department, Description, Instructions, IsActive, IsMainRouter, 
                           CreatedById, CreatedAt, UpdatedAt
                    FROM Agents 
                    WHERE Id = :agent_id AND CreatedById = :user_id
                """)
                params["user_id"] = user_id
            
            result = self.db.execute(query, params)
            row = result.fetchone()
            
            if not row:
                return None
            
            # Get associated functions
            functions = self._get_agent_functions(agent_id)
            
            return AgentConfig(
                id=row.Id,
                name=row.Name,
                department=row.Department,
                description=row.Description,
                instructions=row.Instructions,
                is_active=row.IsActive,
                is_main_router=row.IsMainRouter,
                created_by_id=row.CreatedById,
                created_at=row.CreatedAt,
                updated_at=row.UpdatedAt,
                functions=functions
            )
            
        except Exception as e:
            logger.error(f"Error getting agent {agent_id}: {e}")
            raise

    def list_active_agents(self, limit: int = 10, offset: int = 0, department: str = None) -> tuple[List[AgentConfig], int]:
        """
        List active agents for runtime use.
        
        Args:
            limit: Maximum number of agents to return
            offset: Number of agents to skip
            department: Optional department filter
            
        Returns:
            tuple: (List of active agents, total count)
        """
        try:
            # Build WHERE clause
            where_conditions = ["IsActive = 1"]
            params = {"offset": offset, "limit": limit}
            
            if department:
                where_conditions.append("Department = :department")
                params["department"] = department
            
            where_clause = " AND ".join(where_conditions)
            
            # Get total count
            count_query = text(f"SELECT COUNT(*) as total FROM Agents WHERE {where_clause}")
            count_result = self.db.execute(count_query, params)
            total = count_result.fetchone().total
            
            # Get agents with pagination
            list_query = text(f"""
                SELECT Id, Name, Department, Description, Instructions, IsActive, IsMainRouter, 
                       CreatedById, CreatedAt, UpdatedAt
                FROM Agents 
                WHERE {where_clause}
                ORDER BY IsMainRouter DESC, CreatedAt DESC
                OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY
            """)
            
            result = self.db.execute(list_query, params)
            
            agents = []
            for row in result:
                # Get functions for each agent
                functions = self._get_agent_functions(row.Id)
                
                agents.append(AgentConfig(
                    id=row.Id,
                    name=row.Name,
                    department=row.Department,
                    description=row.Description,
                    instructions=row.Instructions,
                    is_active=row.IsActive,
                    is_main_router=row.IsMainRouter,
                    created_by_id=row.CreatedById,
                    created_at=row.CreatedAt,
                    updated_at=row.UpdatedAt,
                    functions=functions
                ))
            
            return agents, total
            
        except Exception as e:
            logger.error(f"Error listing active agents: {e}")
            raise

    def list_agents_by_user(self, user_id: int, limit: int = 10, offset: int = 0) -> tuple[List[AgentConfig], int]:
        """
        List agents for a user.
        
        Args:
            user_id: User ID
            limit: Maximum number of agents to return
            offset: Number of agents to skip
            
        Returns:
            tuple: (List of agents, total count)
        """
        try:
            # Get total count
            count_query = text("SELECT COUNT(*) as total FROM Agents WHERE CreatedById = :user_id")
            count_result = self.db.execute(count_query, {"user_id": user_id})
            total = count_result.fetchone().total
            
            # Get agents with pagination
            list_query = text("""
                SELECT Id, Name, Department, Description, Instructions, IsActive, IsMainRouter, 
                       CreatedById, CreatedAt, UpdatedAt
                FROM Agents 
                WHERE CreatedById = :user_id
                ORDER BY CreatedAt DESC
                OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY
            """)
            
            result = self.db.execute(list_query, {
                "user_id": user_id,
                "offset": offset,
                "limit": limit
            })
            
            agents = []
            for row in result:
                # Get functions for each agent (consider optimizing with joins if needed)
                functions = self._get_agent_functions(row.Id)
                
                agents.append(AgentConfig(
                    id=row.Id,
                    name=row.Name,
                    department=row.Department,
                    description=row.Description,
                    instructions=row.Instructions,
                    is_active=row.IsActive,
                    is_main_router=row.IsMainRouter,
                    created_by_id=row.CreatedById,
                    created_at=row.CreatedAt,
                    updated_at=row.UpdatedAt,
                    functions=functions
                ))
            
            return agents, total
            
        except Exception as e:
            logger.error(f"Error listing agents for user {user_id}: {e}")
            raise

    # ==========================================
    # ADMIN/MANAGEMENT OPERATIONS (Optional)
    # These can be disabled if AgentPlatform.Core is used only for runtime
    # ==========================================
    
    def create_agent(self, agent_data: CreateAgentRequest, created_by_id: int) -> AgentConfig:
        """
        Create a new agent in the database.
        
        NOTE: This method should typically be used only by AgentPlatform.API
        For runtime-only deployments, this can be disabled.
        
        Args:
            agent_data: Agent creation data
            created_by_id: ID of the user creating the agent
            
        Returns:
            AgentConfig: Created agent configuration
        """
        try:
            # Insert agent into database using raw SQL to match .NET API structure
            insert_query = text("""
                INSERT INTO Agents (Name, Department, Description, Instructions, IsActive, IsMainRouter, CreatedById, CreatedAt)
                OUTPUT INSERTED.Id, INSERTED.Name, INSERTED.Department, INSERTED.Description, 
                       INSERTED.Instructions, INSERTED.IsActive, INSERTED.IsMainRouter, 
                       INSERTED.CreatedById, INSERTED.CreatedAt, INSERTED.UpdatedAt
                VALUES (:name, :department, :description, :instructions, :is_active, :is_main_router, :created_by_id, :created_at)
            """)
            
            result = self.db.execute(insert_query, {
                "name": agent_data.name,
                "department": agent_data.department,
                "description": agent_data.description,
                "instructions": agent_data.instructions,
                "is_active": agent_data.is_active,
                "is_main_router": agent_data.is_main_router,
                "created_by_id": created_by_id,
                "created_at": datetime.utcnow()
            })
            
            row = result.fetchone()
            
            # Create the agent configuration object
            agent_config = AgentConfig(
                id=row.Id,
                name=row.Name,
                department=row.Department,
                description=row.Description,
                instructions=row.Instructions,
                is_active=row.IsActive,
                is_main_router=row.IsMainRouter,
                created_by_id=row.CreatedById,
                created_at=row.CreatedAt,
                updated_at=row.UpdatedAt
            )
            
            # Insert associated functions if provided
            if agent_data.functions:
                for function in agent_data.functions:
                    self._create_agent_function(agent_config.id, function)
            
            self.db.commit()
            logger.info(f"Agent '{agent_config.name}' created with ID {agent_config.id}")
            
            return agent_config
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating agent: {e}")
            raise
    
    def update_agent(self, agent_id: int, agent_data: UpdateAgentRequest, user_id: int = None) -> Optional[AgentConfig]:
        """
        Update an agent.
        
        NOTE: This method should typically be used only by AgentPlatform.API
        For runtime-only deployments, this can be disabled.
        
        Args:
            agent_id: Agent ID
            agent_data: Update data
            user_id: Optional user ID for access control
            
        Returns:
            AgentConfig: Updated agent configuration or None if not found
        """
        try:
            # Build dynamic update query
            update_fields = []
            params = {"agent_id": agent_id, "updated_at": datetime.utcnow()}
            
            if agent_data.name is not None:
                update_fields.append("Name = :name")
                params["name"] = agent_data.name
            
            if agent_data.department is not None:
                update_fields.append("Department = :department")
                params["department"] = agent_data.department
            
            if agent_data.description is not None:
                update_fields.append("Description = :description")
                params["description"] = agent_data.description
            
            if agent_data.instructions is not None:
                update_fields.append("Instructions = :instructions")
                params["instructions"] = agent_data.instructions
            
            if agent_data.is_active is not None:
                update_fields.append("IsActive = :is_active")
                params["is_active"] = agent_data.is_active
            
            if agent_data.is_main_router is not None:
                update_fields.append("IsMainRouter = :is_main_router")
                params["is_main_router"] = agent_data.is_main_router
            
            if not update_fields:
                # No fields to update, just return current agent
                return self.get_agent_by_id(agent_id, user_id)
            
            update_fields.append("UpdatedAt = :updated_at")
            
            # Add user filter if provided
            where_clause = "WHERE Id = :agent_id"
            if user_id:
                where_clause += " AND CreatedById = :user_id"
                params["user_id"] = user_id
            
            update_query = text(f"""
                UPDATE Agents 
                SET {', '.join(update_fields)}
                {where_clause}
            """)
            
            result = self.db.execute(update_query, params)
            
            if result.rowcount == 0:
                return None
            
            self.db.commit()
            
            # Return updated agent
            return self.get_agent_by_id(agent_id, user_id)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating agent {agent_id}: {e}")
            raise
    
    def delete_agent(self, agent_id: int, user_id: int = None) -> bool:
        """
        Delete an agent.
        
        NOTE: This method should typically be used only by AgentPlatform.API
        For runtime-only deployments, this can be disabled.
        
        Args:
            agent_id: Agent ID
            user_id: Optional user ID for access control
            
        Returns:
            bool: True if deleted, False if not found
        """
        try:
            # Delete associated functions first
            delete_functions_query = text("DELETE FROM AgentFunctions WHERE AgentId = :agent_id")
            self.db.execute(delete_functions_query, {"agent_id": agent_id})
            
            # Delete agent
            where_clause = "WHERE Id = :agent_id"
            params = {"agent_id": agent_id}
            
            if user_id:
                where_clause += " AND CreatedById = :user_id"
                params["user_id"] = user_id
            
            delete_query = text(f"DELETE FROM Agents {where_clause}")
            result = self.db.execute(delete_query, params)
            
            if result.rowcount == 0:
                return False
            
            self.db.commit()
            logger.info(f"Agent {agent_id} deleted successfully")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting agent {agent_id}: {e}")
            raise
    
    def _get_agent_functions(self, agent_id: int) -> List:
        """
        Get functions associated with an agent.
        
        Args:
            agent_id: Agent ID
            
        Returns:
            List: List of agent functions
        """
        try:
            query = text("""
                SELECT Id, AgentId, Name, Description, Schema, EndpointUrl, HttpMethod, Headers, IsActive, CreatedAt, UpdatedAt
                FROM AgentFunctions 
                WHERE AgentId = :agent_id AND IsActive = 1
            """)
            
            result = self.db.execute(query, {"agent_id": agent_id})
            
            functions = []
            for row in result:
                from ...models.schemas import AgentFunction
                functions.append(AgentFunction(
                    id=row.Id,
                    agent_id=row.AgentId,
                    name=row.Name,
                    description=row.Description,
                    schema=row.Schema,
                    endpoint_url=row.EndpointUrl,
                    http_method=row.HttpMethod,
                    headers=row.Headers,
                    is_active=row.IsActive,
                    created_at=row.CreatedAt,
                    updated_at=row.UpdatedAt
                ))
            
            return functions
            
        except Exception as e:
            logger.error(f"Error getting functions for agent {agent_id}: {e}")
            return []
    
    def _create_agent_function(self, agent_id: int, function_data) -> None:
        """
        Create a function for an agent.
        
        Args:
            agent_id: Agent ID
            function_data: Function data
        """
        try:
            insert_query = text("""
                INSERT INTO AgentFunctions (AgentId, Name, Description, Schema, EndpointUrl, HttpMethod, Headers, IsActive, CreatedAt)
                VALUES (:agent_id, :name, :description, :schema, :endpoint_url, :http_method, :headers, :is_active, :created_at)
            """)
            
            self.db.execute(insert_query, {
                "agent_id": agent_id,
                "name": function_data.name,
                "description": function_data.description,
                "schema": function_data.schema,
                "endpoint_url": function_data.endpoint_url,
                "http_method": function_data.http_method or "POST",
                "headers": function_data.headers,
                "is_active": function_data.is_active,
                "created_at": datetime.utcnow()
            })
            
        except Exception as e:
            logger.error(f"Error creating function for agent {agent_id}: {e}")
            raise 