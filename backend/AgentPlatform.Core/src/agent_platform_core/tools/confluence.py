"""
Confluence tool functions for searching and retrieving documents (RAG).
"""

import logging
from typing import Dict, Any, Optional, List
from .common.http_client import create_authenticated_client
from .registry import get_tool_registry

logger = logging.getLogger(__name__)


def search_confluence_documents(
    confluence_url: str,
    confluence_username: str,
    confluence_api_token: str,
    query: str,
    limit: int = 10,
    space_key: str = None,
    content_type: str = "page",
    **kwargs
) -> Dict[str, Any]:
    """
    Search Confluence documents using CQL (Confluence Query Language).
    
    Args:
        confluence_url: Confluence instance URL (e.g., https://company.atlassian.net/wiki)
        confluence_username: Confluence username/email
        confluence_api_token: Confluence API token
        query: Search query text
        limit: Maximum number of results (default: 10)
        space_key: Confluence space key to limit search (optional)
        content_type: Content type to search ("page", "blogpost", default: "page")
        **kwargs: Additional parameters
        
    Returns:
        Dict[str, Any]: Search results with document summaries
        
    Raises:
        Exception: If search fails
    """
    logger.info(f"Searching Confluence documents for: {query}")
    
    try:
        # Create authenticated client
        client = create_authenticated_client(
            base_url=f"{confluence_url}/rest/api",
            auth_type="basic",
            username=confluence_username,
            password=confluence_api_token
        )
        
        # Build CQL query
        cql_parts = [f'text ~ "{query}"', f'type = {content_type}']
        
        if space_key:
            cql_parts.append(f'space = "{space_key}"')
        
        cql_query = " AND ".join(cql_parts)
        
        # Search parameters
        params = {
            "cql": cql_query,
            "limit": limit,
            "expand": "body.storage,space,version,ancestors"
        }
        
        # Perform search
        response = client.get("/content/search", params=params)
        
        documents = []
        for result in response.get("results", []):
            # Extract document content
            content_body = ""
            if result.get("body", {}).get("storage"):
                content_body = result["body"]["storage"].get("value", "")
            
            # Get space information
            space_info = result.get("space", {})
            
            # Get ancestors (parent pages)
            ancestors = []
            for ancestor in result.get("ancestors", []):
                ancestors.append({
                    "id": ancestor.get("id"),
                    "title": ancestor.get("title"),
                    "type": ancestor.get("type")
                })
            
            documents.append({
                "id": result.get("id"),
                "title": result.get("title"),
                "type": result.get("type"),
                "status": result.get("status"),
                "url": f"{confluence_url}{result.get('_links', {}).get('webui', '')}",
                "space": {
                    "key": space_info.get("key"),
                    "name": space_info.get("name")
                },
                "content_excerpt": _extract_text_excerpt(content_body, 500),
                "last_modified": result.get("version", {}).get("when"),
                "last_modified_by": result.get("version", {}).get("by", {}).get("displayName"),
                "ancestors": ancestors
            })
        
        result = {
            "success": True,
            "query": query,
            "cql_query": cql_query,
            "total_results": len(documents),
            "documents": documents,
            "space_filter": space_key
        }
        
        logger.info(f"Found {len(documents)} Confluence documents")
        return result
        
    except Exception as e:
        logger.error(f"Error searching Confluence documents: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to search Confluence documents: {str(e)}"
        }


def get_confluence_page(
    confluence_url: str,
    confluence_username: str,
    confluence_api_token: str,
    page_id: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Get a specific Confluence page by ID.
    
    Args:
        confluence_url: Confluence instance URL
        confluence_username: Confluence username/email
        confluence_api_token: Confluence API token
        page_id: Confluence page ID
        **kwargs: Additional parameters
        
    Returns:
        Dict[str, Any]: Page content and metadata
        
    Raises:
        Exception: If retrieval fails
    """
    logger.info(f"Getting Confluence page: {page_id}")
    
    try:
        # Create authenticated client
        client = create_authenticated_client(
            base_url=f"{confluence_url}/rest/api",
            auth_type="basic",
            username=confluence_username,
            password=confluence_api_token
        )
        
        # Get page details
        params = {
            "expand": "body.storage,space,version,ancestors,children.page"
        }
        
        response = client.get(f"/content/{page_id}", params=params)
        
        # Extract content
        content_body = ""
        if response.get("body", {}).get("storage"):
            content_body = response["body"]["storage"].get("value", "")
        
        # Get space information
        space_info = response.get("space", {})
        
        # Get ancestors (parent pages)
        ancestors = []
        for ancestor in response.get("ancestors", []):
            ancestors.append({
                "id": ancestor.get("id"),
                "title": ancestor.get("title"),
                "type": ancestor.get("type")
            })
        
        # Get child pages
        child_pages = []
        for child in response.get("children", {}).get("page", {}).get("results", []):
            child_pages.append({
                "id": child.get("id"),
                "title": child.get("title"),
                "type": child.get("type")
            })
        
        result = {
            "success": True,
            "id": response.get("id"),
            "title": response.get("title"),
            "type": response.get("type"),
            "status": response.get("status"),
            "url": f"{confluence_url}{response.get('_links', {}).get('webui', '')}",
            "space": {
                "key": space_info.get("key"),
                "name": space_info.get("name")
            },
            "content": _extract_text_content(content_body),
            "content_html": content_body,
            "last_modified": response.get("version", {}).get("when"),
            "last_modified_by": response.get("version", {}).get("by", {}).get("displayName"),
            "version": response.get("version", {}).get("number"),
            "ancestors": ancestors,
            "child_pages": child_pages
        }
        
        logger.info(f"Successfully retrieved Confluence page: {page_id}")
        return result
        
    except Exception as e:
        logger.error(f"Error getting Confluence page {page_id}: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to get Confluence page {page_id}: {str(e)}"
        }


def search_confluence_spaces(
    confluence_url: str,
    confluence_username: str,
    confluence_api_token: str,
    query: str = None,
    limit: int = 10,
    **kwargs
) -> Dict[str, Any]:
    """
    Search or list Confluence spaces.
    
    Args:
        confluence_url: Confluence instance URL
        confluence_username: Confluence username/email
        confluence_api_token: Confluence API token
        query: Space name search query (optional)
        limit: Maximum number of results (default: 10)
        **kwargs: Additional parameters
        
    Returns:
        Dict[str, Any]: Available spaces
        
    Raises:
        Exception: If search fails
    """
    logger.info(f"Searching Confluence spaces: {query or 'all spaces'}")
    
    try:
        # Create authenticated client
        client = create_authenticated_client(
            base_url=f"{confluence_url}/rest/api",
            auth_type="basic",
            username=confluence_username,
            password=confluence_api_token
        )
        
        # Search parameters
        params = {
            "limit": limit,
            "expand": "description.plain,homepage"
        }
        
        if query:
            params["spaceKey"] = query  # Search by space key or name
        
        # Get spaces
        response = client.get("/space", params=params)
        
        spaces = []
        for space in response.get("results", []):
            # Get homepage info if available
            homepage = space.get("homepage", {})
            
            spaces.append({
                "key": space.get("key"),
                "name": space.get("name"),
                "type": space.get("type"),
                "status": space.get("status"),
                "description": space.get("description", {}).get("plain", {}).get("value", ""),
                "url": f"{confluence_url}{space.get('_links', {}).get('webui', '')}",
                "homepage": {
                    "id": homepage.get("id"),
                    "title": homepage.get("title")
                } if homepage else None
            })
        
        result = {
            "success": True,
            "query": query,
            "total_spaces": len(spaces),
            "spaces": spaces
        }
        
        logger.info(f"Found {len(spaces)} Confluence spaces")
        return result
        
    except Exception as e:
        logger.error(f"Error searching Confluence spaces: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to search Confluence spaces: {str(e)}"
        }


def _extract_text_content(html_content: str) -> str:
    """
    Extract plain text from Confluence HTML content.
    
    Args:
        html_content: HTML content from Confluence
        
    Returns:
        str: Plain text content
    """
    if not html_content:
        return ""
    
    try:
        from bs4 import BeautifulSoup
        
        # Parse HTML and extract text
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text and clean up whitespace
        text = soup.get_text()
        text = ' '.join(text.split())
        
        return text
        
    except ImportError:
        # Fallback: simple HTML tag removal
        import re
        text = re.sub('<[^<]+?>', '', html_content)
        text = ' '.join(text.split())
        return text
    except Exception as e:
        logger.warning(f"Error extracting text content: {e}")
        return html_content[:1000]  # Return first 1000 characters as fallback


def _extract_text_excerpt(html_content: str, max_length: int = 500) -> str:
    """
    Extract a text excerpt from HTML content.
    
    Args:
        html_content: HTML content
        max_length: Maximum excerpt length
        
    Returns:
        str: Text excerpt
    """
    text = _extract_text_content(html_content)
    
    if len(text) <= max_length:
        return text
    
    # Truncate and add ellipsis
    excerpt = text[:max_length].rsplit(' ', 1)[0]
    return f"{excerpt}..."


# Register tools in the registry
def _register_confluence_tools():
    """Register Confluence tools in the tool registry."""
    registry = get_tool_registry()
    
    # Search Confluence documents tool
    registry.register_tool(
        name="search_confluence_documents",
        function=search_confluence_documents,
        description="Search Confluence documents using text query with RAG capabilities",
        required_credentials=["confluence_url", "confluence_username", "confluence_api_token"],
        parameters_schema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query text"},
                "limit": {"type": "integer", "description": "Maximum results", "default": 10},
                "space_key": {"type": "string", "description": "Confluence space key (optional)"},
                "content_type": {"type": "string", "description": "Content type", "default": "page"}
            },
            "required": ["query"]
        },
        category="confluence"
    )
    
    # Get Confluence page tool
    registry.register_tool(
        name="get_confluence_page",
        function=get_confluence_page,
        description="Get a specific Confluence page by ID",
        required_credentials=["confluence_url", "confluence_username", "confluence_api_token"],
        parameters_schema={
            "type": "object",
            "properties": {
                "page_id": {"type": "string", "description": "Confluence page ID"}
            },
            "required": ["page_id"]
        },
        category="confluence"
    )
    
    # Search Confluence spaces tool
    registry.register_tool(
        name="search_confluence_spaces",
        function=search_confluence_spaces,
        description="Search or list available Confluence spaces",
        required_credentials=["confluence_url", "confluence_username", "confluence_api_token"],
        parameters_schema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Space search query (optional)"},
                "limit": {"type": "integer", "description": "Maximum results", "default": 10}
            },
            "required": []
        },
        category="confluence"
    )


# Register tools when module is imported
_register_confluence_tools() 