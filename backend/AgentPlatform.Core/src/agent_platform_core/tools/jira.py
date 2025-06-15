"""
Jira tool functions for creating and managing Jira tickets.
"""

import logging
from typing import Dict, Any, Optional, List
from .common.http_client import create_authenticated_client
from .registry import get_tool_registry

logger = logging.getLogger(__name__)


def create_jira_ticket(
    jira_url: str,
    jira_username: str,
    jira_api_token: str,
    project_key: str,
    summary: str,
    description: str,
    issue_type: str = "Task",
    priority: str = "Medium",
    assignee: str = None,
    labels: List[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Create a new Jira ticket.
    
    Args:
        jira_url: Jira instance URL (e.g., https://company.atlassian.net)
        jira_username: Jira username/email
        jira_api_token: Jira API token
        project_key: Jira project key (e.g., "PROJ")
        summary: Issue summary/title
        description: Issue description
        issue_type: Issue type (default: "Task")
        priority: Issue priority (default: "Medium")
        assignee: Assignee username (optional)
        labels: List of labels (optional)
        **kwargs: Additional fields
        
    Returns:
        Dict[str, Any]: Created ticket information
        
    Raises:
        Exception: If ticket creation fails
    """
    logger.info(f"Creating Jira ticket in project {project_key}: {summary}")
    
    try:
        # Create authenticated client
        client = create_authenticated_client(
            base_url=f"{jira_url}/rest/api/3",
            auth_type="basic",
            username=jira_username,
            password=jira_api_token
        )
        
        # Prepare issue data
        issue_data = {
            "fields": {
                "project": {"key": project_key},
                "summary": summary,
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": description
                                }
                            ]
                        }
                    ]
                },
                "issuetype": {"name": issue_type},
                "priority": {"name": priority}
            }
        }
        
        # Add assignee if provided
        if assignee:
            issue_data["fields"]["assignee"] = {"name": assignee}
        
        # Add labels if provided
        if labels:
            issue_data["fields"]["labels"] = labels
        
        # Add any additional fields
        for key, value in kwargs.items():
            if key not in ["jira_url", "jira_username", "jira_api_token", "project_key", 
                          "summary", "description", "issue_type", "priority", "assignee", "labels"]:
                issue_data["fields"][key] = value
        
        # Create the issue
        response = client.post("/issue", json_data=issue_data)
        
        # Get the created issue details
        issue_key = response.get("key")
        if issue_key:
            # Fetch full issue details
            issue_details = client.get(f"/issue/{issue_key}")
            
            result = {
                "success": True,
                "issue_key": issue_key,
                "issue_id": response.get("id"),
                "summary": issue_details.get("fields", {}).get("summary"),
                "status": issue_details.get("fields", {}).get("status", {}).get("name"),
                "assignee": issue_details.get("fields", {}).get("assignee", {}).get("displayName"),
                "priority": issue_details.get("fields", {}).get("priority", {}).get("name"),
                "url": f"{jira_url}/browse/{issue_key}",
                "created": issue_details.get("fields", {}).get("created")
            }
            
            logger.info(f"Successfully created Jira ticket: {issue_key}")
            return result
        else:
            raise Exception("Failed to get issue key from response")
            
    except Exception as e:
        logger.error(f"Error creating Jira ticket: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to create Jira ticket: {str(e)}"
        }


def read_jira_ticket(
    jira_url: str,
    jira_username: str,
    jira_api_token: str,
    issue_key: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Read a Jira ticket by issue key.
    
    Args:
        jira_url: Jira instance URL
        jira_username: Jira username/email
        jira_api_token: Jira API token
        issue_key: Issue key (e.g., "PROJ-123")
        **kwargs: Additional parameters
        
    Returns:
        Dict[str, Any]: Ticket information
        
    Raises:
        Exception: If ticket retrieval fails
    """
    logger.info(f"Reading Jira ticket: {issue_key}")
    
    try:
        # Create authenticated client
        client = create_authenticated_client(
            base_url=f"{jira_url}/rest/api/3",
            auth_type="basic",
            username=jira_username,
            password=jira_api_token
        )
        
        # Get issue details
        response = client.get(f"/issue/{issue_key}")
        
        fields = response.get("fields", {})
        
        result = {
            "success": True,
            "issue_key": issue_key,
            "issue_id": response.get("id"),
            "summary": fields.get("summary"),
            "description": _extract_description_text(fields.get("description")),
            "status": fields.get("status", {}).get("name"),
            "assignee": fields.get("assignee", {}).get("displayName") if fields.get("assignee") else None,
            "reporter": fields.get("reporter", {}).get("displayName") if fields.get("reporter") else None,
            "priority": fields.get("priority", {}).get("name") if fields.get("priority") else None,
            "issue_type": fields.get("issuetype", {}).get("name") if fields.get("issuetype") else None,
            "labels": fields.get("labels", []),
            "url": f"{jira_url}/browse/{issue_key}",
            "created": fields.get("created"),
            "updated": fields.get("updated"),
            "resolution": fields.get("resolution", {}).get("name") if fields.get("resolution") else None
        }
        
        logger.info(f"Successfully read Jira ticket: {issue_key}")
        return result
        
    except Exception as e:
        logger.error(f"Error reading Jira ticket {issue_key}: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to read Jira ticket {issue_key}: {str(e)}"
        }


def search_jira_tickets(
    jira_url: str,
    jira_username: str,
    jira_api_token: str,
    jql_query: str,
    max_results: int = 10,
    **kwargs
) -> Dict[str, Any]:
    """
    Search Jira tickets using JQL.
    
    Args:
        jira_url: Jira instance URL
        jira_username: Jira username/email
        jira_api_token: Jira API token
        jql_query: JQL query string
        max_results: Maximum number of results (default: 10)
        **kwargs: Additional parameters
        
    Returns:
        Dict[str, Any]: Search results
        
    Raises:
        Exception: If search fails
    """
    logger.info(f"Searching Jira tickets with JQL: {jql_query}")
    
    try:
        # Create authenticated client
        client = create_authenticated_client(
            base_url=f"{jira_url}/rest/api/3",
            auth_type="basic",
            username=jira_username,
            password=jira_api_token
        )
        
        # Search using JQL
        search_data = {
            "jql": jql_query,
            "maxResults": max_results,
            "fields": ["summary", "status", "assignee", "priority", "issuetype", "created", "updated"]
        }
        
        response = client.post("/search", json_data=search_data)
        
        issues = []
        for issue in response.get("issues", []):
            fields = issue.get("fields", {})
            issues.append({
                "issue_key": issue.get("key"),
                "summary": fields.get("summary"),
                "status": fields.get("status", {}).get("name"),
                "assignee": fields.get("assignee", {}).get("displayName") if fields.get("assignee") else None,
                "priority": fields.get("priority", {}).get("name") if fields.get("priority") else None,
                "issue_type": fields.get("issuetype", {}).get("name") if fields.get("issuetype") else None,
                "url": f"{jira_url}/browse/{issue.get('key')}",
                "created": fields.get("created"),
                "updated": fields.get("updated")
            })
        
        result = {
            "success": True,
            "total": response.get("total", 0),
            "issues": issues,
            "jql_query": jql_query
        }
        
        logger.info(f"Found {len(issues)} Jira tickets")
        return result
        
    except Exception as e:
        logger.error(f"Error searching Jira tickets: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to search Jira tickets: {str(e)}"
        }


def _extract_description_text(description_obj: Dict[str, Any]) -> str:
    """
    Extract plain text from Jira description object.
    
    Args:
        description_obj: Jira description object
        
    Returns:
        str: Plain text description
    """
    if not description_obj:
        return ""
    
    if isinstance(description_obj, str):
        return description_obj
    
    # Handle Atlassian Document Format (ADF)
    if isinstance(description_obj, dict) and "content" in description_obj:
        text_parts = []
        for content in description_obj.get("content", []):
            if content.get("type") == "paragraph":
                for text_content in content.get("content", []):
                    if text_content.get("type") == "text":
                        text_parts.append(text_content.get("text", ""))
        return " ".join(text_parts)
    
    return str(description_obj)


# Register tools in the registry
def _register_jira_tools():
    """Register Jira tools in the tool registry."""
    registry = get_tool_registry()
    
    # Create Jira ticket tool
    registry.register_tool(
        name="create_jira_ticket",
        function=create_jira_ticket,
        description="Create a new Jira ticket with specified details",
        required_credentials=["jira_url", "jira_username", "jira_api_token"],
        parameters_schema={
            "type": "object",
            "properties": {
                "project_key": {"type": "string", "description": "Jira project key"},
                "summary": {"type": "string", "description": "Issue summary/title"},
                "description": {"type": "string", "description": "Issue description"},
                "issue_type": {"type": "string", "description": "Issue type", "default": "Task"},
                "priority": {"type": "string", "description": "Issue priority", "default": "Medium"},
                "assignee": {"type": "string", "description": "Assignee username (optional)"},
                "labels": {"type": "array", "items": {"type": "string"}, "description": "List of labels"}
            },
            "required": ["project_key", "summary", "description"]
        },
        category="jira"
    )
    
    # Read Jira ticket tool
    registry.register_tool(
        name="read_jira_ticket",
        function=read_jira_ticket,
        description="Read a Jira ticket by issue key",
        required_credentials=["jira_url", "jira_username", "jira_api_token"],
        parameters_schema={
            "type": "object",
            "properties": {
                "issue_key": {"type": "string", "description": "Jira issue key (e.g., PROJ-123)"}
            },
            "required": ["issue_key"]
        },
        category="jira"
    )
    
    # Search Jira tickets tool
    registry.register_tool(
        name="search_jira_tickets",
        function=search_jira_tickets,
        description="Search Jira tickets using JQL query",
        required_credentials=["jira_url", "jira_username", "jira_api_token"],
        parameters_schema={
            "type": "object",
            "properties": {
                "jql_query": {"type": "string", "description": "JQL query string"},
                "max_results": {"type": "integer", "description": "Maximum number of results", "default": 10}
            },
            "required": ["jql_query"]
        },
        category="jira"
    )


# Register tools when module is imported
_register_jira_tools() 