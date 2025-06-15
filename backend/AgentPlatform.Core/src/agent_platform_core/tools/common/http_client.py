"""
Common HTTP client utility for tool functions.

NOTE: This custom HTTP client is maintained for legacy tool compatibility
(Jira, Calendar, Confluence integrations). In the future, these tools could
potentially be migrated to use ADK's built-in HttpTool for consistency.

For new tools, consider using ADK's HttpTool directly through adk_tools.py.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, Union
import httpx
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)


class HTTPClient:
    """
    HTTP client for making API requests from tools.
    """
    
    def __init__(self, base_url: str = None, default_headers: Dict[str, str] = None, timeout: int = 30):
        """
        Initialize HTTP client.
        
        Args:
            base_url: Base URL for API requests
            default_headers: Default headers to include in all requests
            timeout: Request timeout in seconds
        """
        self.base_url = base_url
        self.default_headers = default_headers or {}
        self.timeout = timeout
        self.client = httpx.Client(timeout=timeout)
        self.async_client = httpx.AsyncClient(timeout=timeout)
    
    def _build_url(self, endpoint: str) -> str:
        """
        Build full URL from endpoint.
        
        Args:
            endpoint: API endpoint
            
        Returns:
            str: Full URL
        """
        if self.base_url:
            return urljoin(self.base_url, endpoint)
        return endpoint
    
    def _prepare_headers(self, headers: Dict[str, str] = None) -> Dict[str, str]:
        """
        Prepare headers by merging default and request-specific headers.
        
        Args:
            headers: Request-specific headers
            
        Returns:
            Dict[str, str]: Merged headers
        """
        merged_headers = self.default_headers.copy()
        if headers:
            merged_headers.update(headers)
        return merged_headers
    
    def get(
        self,
        endpoint: str,
        params: Dict[str, Any] = None,
        headers: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """
        Make a GET request.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            headers: Request headers
            
        Returns:
            Dict[str, Any]: Response data
            
        Raises:
            Exception: If request fails
        """
        url = self._build_url(endpoint)
        headers = self._prepare_headers(headers)
        
        logger.debug(f"GET {url} with params: {params}")
        
        try:
            response = self.client.get(url, params=params, headers=headers)
            response.raise_for_status()
            
            logger.debug(f"GET {url} successful: {response.status_code}")
            
            # Try to parse as JSON, fall back to text
            try:
                return response.json()
            except Exception:
                return {"content": response.text, "status_code": response.status_code}
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error for GET {url}: {e.response.status_code} - {e.response.text}")
            raise Exception(f"API request failed: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            logger.error(f"Request error for GET {url}: {e}")
            raise Exception(f"Request failed: {str(e)}")
    
    def post(
        self,
        endpoint: str,
        data: Dict[str, Any] = None,
        json_data: Dict[str, Any] = None,
        headers: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """
        Make a POST request.
        
        Args:
            endpoint: API endpoint
            data: Form data
            json_data: JSON data
            headers: Request headers
            
        Returns:
            Dict[str, Any]: Response data
            
        Raises:
            Exception: If request fails
        """
        url = self._build_url(endpoint)
        headers = self._prepare_headers(headers)
        
        logger.debug(f"POST {url} with json: {json_data is not None}, form: {data is not None}")
        
        try:
            if json_data:
                response = self.client.post(url, json=json_data, headers=headers)
            elif data:
                response = self.client.post(url, data=data, headers=headers)
            else:
                response = self.client.post(url, headers=headers)
            
            response.raise_for_status()
            
            logger.debug(f"POST {url} successful: {response.status_code}")
            
            # Try to parse as JSON, fall back to text
            try:
                return response.json()
            except Exception:
                return {"content": response.text, "status_code": response.status_code}
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error for POST {url}: {e.response.status_code} - {e.response.text}")
            raise Exception(f"API request failed: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            logger.error(f"Request error for POST {url}: {e}")
            raise Exception(f"Request failed: {str(e)}")
    
    def put(
        self,
        endpoint: str,
        data: Dict[str, Any] = None,
        json_data: Dict[str, Any] = None,
        headers: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """
        Make a PUT request.
        
        Args:
            endpoint: API endpoint
            data: Form data
            json_data: JSON data
            headers: Request headers
            
        Returns:
            Dict[str, Any]: Response data
            
        Raises:
            Exception: If request fails
        """
        url = self._build_url(endpoint)
        headers = self._prepare_headers(headers)
        
        logger.debug(f"PUT {url}")
        
        try:
            if json_data:
                response = self.client.put(url, json=json_data, headers=headers)
            elif data:
                response = self.client.put(url, data=data, headers=headers)
            else:
                response = self.client.put(url, headers=headers)
            
            response.raise_for_status()
            
            logger.debug(f"PUT {url} successful: {response.status_code}")
            
            try:
                return response.json()
            except Exception:
                return {"content": response.text, "status_code": response.status_code}
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error for PUT {url}: {e.response.status_code} - {e.response.text}")
            raise Exception(f"API request failed: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            logger.error(f"Request error for PUT {url}: {e}")
            raise Exception(f"Request failed: {str(e)}")
    
    def delete(
        self,
        endpoint: str,
        headers: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """
        Make a DELETE request.
        
        Args:
            endpoint: API endpoint
            headers: Request headers
            
        Returns:
            Dict[str, Any]: Response data
            
        Raises:
            Exception: If request fails
        """
        url = self._build_url(endpoint)
        headers = self._prepare_headers(headers)
        
        logger.debug(f"DELETE {url}")
        
        try:
            response = self.client.delete(url, headers=headers)
            response.raise_for_status()
            
            logger.debug(f"DELETE {url} successful: {response.status_code}")
            
            try:
                return response.json()
            except Exception:
                return {"content": response.text, "status_code": response.status_code}
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error for DELETE {url}: {e.response.status_code} - {e.response.text}")
            raise Exception(f"API request failed: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            logger.error(f"Request error for DELETE {url}: {e}")
            raise Exception(f"Request failed: {str(e)}")
    
    def close(self):
        """Close the HTTP client."""
        self.client.close()
        asyncio.create_task(self.async_client.aclose())


def create_authenticated_client(
    base_url: str,
    auth_type: str = "bearer",
    token: str = None,
    username: str = None,
    password: str = None,
    api_key: str = None,
    api_key_header: str = "X-API-Key",
    timeout: int = 30
) -> HTTPClient:
    """
    Create an authenticated HTTP client.
    
    Args:
        base_url: Base URL for API requests
        auth_type: Authentication type ('bearer', 'basic', 'api_key')
        token: Bearer token
        username: Username for basic auth
        password: Password for basic auth
        api_key: API key
        api_key_header: Header name for API key
        timeout: Request timeout in seconds
        
    Returns:
        HTTPClient: Configured HTTP client
        
    Raises:
        ValueError: If authentication parameters are invalid
    """
    headers = {}
    
    if auth_type == "bearer":
        if not token:
            raise ValueError("Bearer token is required for bearer authentication")
        headers["Authorization"] = f"Bearer {token}"
    
    elif auth_type == "basic":
        if not username or not password:
            raise ValueError("Username and password are required for basic authentication")
        import base64
        credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
        headers["Authorization"] = f"Basic {credentials}"
    
    elif auth_type == "api_key":
        if not api_key:
            raise ValueError("API key is required for API key authentication")
        headers[api_key_header] = api_key
    
    else:
        raise ValueError(f"Unsupported authentication type: {auth_type}")
    
    return HTTPClient(base_url=base_url, default_headers=headers, timeout=timeout) 