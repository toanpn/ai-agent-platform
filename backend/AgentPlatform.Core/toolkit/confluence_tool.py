"""
Confluence Tool Module

This module provides Confluence functionality using LangChain's Confluence toolkit.
Based on: https://python.langchain.com/docs/integrations/tools/confluence/
"""

import os
from langchain.tools import BaseTool
from pydantic import BaseModel, Field, validator
from typing import Optional, Type, Union, List, Dict
import json
import logging
import ast

logger = logging.getLogger(__name__)

# Try to import atlassian-python-api
try:
    from atlassian import Confluence
    ATLASSIAN_AVAILABLE = True
except ImportError:
    ATLASSIAN_AVAILABLE = False
    # Define a dummy class to satisfy the type hint when the library is not installed.
    class Confluence:
        pass
    logger.warning("Thư viện atlassian-python-api không khả dụng. Cài đặt với: pip install atlassian-python-api")

class ConfluenceToolInput(BaseModel):
    """Input schema for Confluence tool."""
    action: Optional[str] = Field(default="get_page_content", description="Hành động Confluence cần thực hiện (ví dụ: 'page_search', 'get_page_content', 'create_page', 'update_page').")
    parameters: Union[dict, str, None] = Field(default_factory=dict, description="Các tham số cho hành động Confluence dưới dạng dictionary hoặc JSON string.")

    @validator("parameters", pre=True)
    def handle_flexible_parameters(cls, v):
        """
        Handles flexible parameter inputs.

        If the input is a string that is not a valid JSON or dict literal,
        it assumes the string is a direct search query.
        """
        if v is None:
            return {}
        if isinstance(v, str):
            if not v.strip():
                return {}
            try:
                # Try to parse as JSON first.
                return json.loads(v)
            except json.JSONDecodeError:
                try:
                    # If JSON fails, try to evaluate as a Python literal.
                    parsed_v = ast.literal_eval(v)
                    if isinstance(parsed_v, dict):
                        return parsed_v
                    else:
                        # Parsed, but not a dict. Assume it's a query.
                        logger.info(f"Input '{v}' evaluated to a non-dict type. Treating as a query.")
                        return {"query": v}
                except (ValueError, SyntaxError, MemoryError, TypeError):
                    # If all parsing fails, it's likely a raw query string.
                    logger.info(f"Could not parse '{v}' as a dict. Assuming it is a direct query.")
                    return {"query": v}
        return v  # Return dictionaries and other types as is.

class ConfluenceTool(BaseTool):
    """Unified Confluence tool for agents using atlassian-python-api."""
    
    name: str = "confluence"
    description: str = """
    Công cụ thông minh để tìm kiếm và đọc nội dung từ Confluence.
    **Cách dùng chính:** Sử dụng action `get_page_content` với một truy vấn tìm kiếm.

    **Hành động và Cách dùng:**

    - **Tìm và đọc trang (Khuyến khích):**
      action: "get_page_content"
      parameters: {{"query": "nội dung cần tìm, ví dụ: 'chính sách hoàn tiền'", "space_key": "KEY" (Tùy chọn)}}
      => Công cụ sẽ tìm kiếm toàn văn (tiêu đề và nội dung) và:
         - Nếu tìm thấy 1 trang, trả về nội dung trang đó.
         - Nếu tìm thấy nhiều trang, trả về danh sách để bạn chọn `page_id`.
         - Nếu không tìm thấy, sẽ báo không có kết quả.

    - **Lấy nội dung trang theo ID (Khi đã biết ID):**
      action: "get_page_content"
      parameters: {{"page_id": "12345"}}

    - **Tạo trang mới:**
      action: "create_page"
      parameters: {{"space_key": "KEY", "title": "Tiêu đề trang", "content": "Nội dung HTML", "parent_page_id": "12345" (Tùy chọn)}}

    - **Cập nhật trang:**
      action: "update_page"
      parameters: {{"page_id": "12345", "title": "Tiêu đề mới", "content": "Nội dung HTML mới"}}

    - **Tìm kiếm nâng cao (dùng CQL):**
      action: "page_search"
      parameters: {{"cql": "space.key = 'KEY' and text ~ 'nội dung'"}}
    """
    args_schema: Type[BaseModel] = ConfluenceToolInput
    
    confluence_url: Optional[str] = None
    username: Optional[str] = None
    api_token: Optional[str] = None
    confluence_client: Optional[Confluence] = None
    initialization_error: Optional[str] = None

    def __init__(self, confluence_url: Optional[str] = None, username: Optional[str] = None, api_token: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        # Allow CONFLUENCE_BASE_URL for backward compatibility
        self.confluence_url = (confluence_url or os.getenv("CONFLUENCE_URL") or os.getenv("CONFLUENCE_BASE_URL") or "").rstrip('/')
        self.username = username or os.getenv("CONFLUENCE_USERNAME")
        self.api_token = api_token or os.getenv("CONFLUENCE_API_TOKEN")

        if not ATLASSIAN_AVAILABLE:
            self.initialization_error = "Thư viện atlassian-python-api chưa được cài đặt. Vui lòng chạy: pip install atlassian-python-api"
            self.confluence_client = None
            return

        if all([self.confluence_url, self.username, self.api_token]):
            try:
                # For Atlassian Cloud, the API token is passed as the 'password'.
                self.confluence_client = Confluence(
                    url=self.confluence_url,
                    username=self.username,
                    password=self.api_token,
                    cloud=True
                )
                # The connection will be verified on the first actual API call.
                # Removing the problematic and incorrect verification check.
            except Exception as e:
                error_message = f"Không thể khởi tạo Confluence client. Vui lòng kiểm tra lại thông tin cấu hình (URL, username, token). Lỗi: {e}"
                logger.error(error_message)
                self.initialization_error = error_message
                self.confluence_client = None
        else:
            # Not an error, will operate in mock mode.
            self.confluence_client = None

    def _run(self, action: Optional[str] = None, parameters: Optional[dict] = None) -> str:
        """Execute a Confluence action."""
        if not action:
            return f"❌ Thiếu tham số 'action'. Các hành động khả dụng:\n{self.description}"

        # Ensure parameters is a dict
        params = parameters or {}
        
        print(f"CONFLUENCE_TOOL: Executing action='{action}' with parameters={params}")
        try:
            if self.initialization_error:
                return f"❌ {self.initialization_error}"
            
            if not self.confluence_client:
                return self._mock_result(action, **params)

            if action == "page_search":
                return self._page_search(params)
            elif action == "get_page_content":
                return self._get_page_content(params)
            elif action == "create_page":
                return self._create_page(params)
            elif action == "update_page":
                return self._update_page(params)
            else:
                return f"❌ Hành động không được hỗ trợ: {action}. Các hành động khả dụng: page_search, get_page_content, create_page, update_page"

        except Exception as e:
            logger.error(f"Error executing Confluence action '{action}': {e}", exc_info=True)
            print(f"CONFLUENCE_TOOL: Error during _run: {e}")
            return f"❌ Lỗi khi thực hiện Confluence action '{action}': {str(e)}"

    def _mock_result(self, action: str, **parameters: dict) -> str:
        """Return mock results when Confluence is not configured."""
        if action == "page_search":
            cql = parameters.get('cql')
            if not cql:
                query = parameters.get('query') or parameters.get('title')
                space = parameters.get('space_key')
                cql_parts = [f'text ~ "{query}"']
                if space:
                    cql_parts.append(f'space.key = "{space.upper()}"')
                cql = " and ".join(cql_parts)

            return f"""🔍 Kết quả tìm kiếm Confluence mô phỏng với CQL '{cql}':

- **Mock Page 1**: ID 12345, Space: MOCK, Title: Mock Page about stuff
- **Mock Page 2**: ID 67890, Space: MOCK, Title: Another Mock Page

💡 **Lưu ý:** Để tìm kiếm thực, cần cấu hình CONFLUENCE_URL, CONFLUENCE_USERNAME, và CONFLUENCE_API_TOKEN"""
        
        elif action == "get_page_content":
            page_id = parameters.get('page_id')
            query = parameters.get('query') or parameters.get('title')

            if page_id:
                metadata_str = (
                    f"**Metadata:**\n"
                    f"- ID: {page_id}\n"
                    f"- Tiêu đề: Trang mô phỏng cho ID {page_id}\n"
                    f"- Người tạo: Mock User\n"
                    f"- Ngày tạo: 2023-01-01T10:00:00Z\n"
                    f"- Cập nhật lần cuối bởi: Mock Editor\n"
                    f"- Ngày cập nhật cuối: 2023-01-10T15:30:00Z"
                )
                content = f"<h1>Tiêu đề trang mô phỏng cho ID {page_id}</h1>\n<p>Nội dung mô phỏng.</p>"
                return f"📄 **Thông tin trang Confluence (Mô phỏng)**\n\n{metadata_str}\n\n**Nội dung:**\n{content}\n\n💡 **Lưu ý:** Để lấy nội dung thực, cần cấu hình."

            if query:
                # Simulate finding multiple pages if query is generic
                if "chính sách" in query.lower():
                    mock_results = [
                        {"id": "1111", "title": "Chính sách hoàn tiền sản phẩm", "space": "SALES"},
                        {"id": "2222", "title": "Chính sách bảo mật thông tin", "space": "LEGAL"},
                    ]
                    results_json = json.dumps(mock_results, indent=2, ensure_ascii=False)
                    return f"✅ Tìm thấy nhiều trang phù hợp (mô phỏng). Vui lòng chạy lại công cụ với `page_id` cụ thể từ danh sách bên dưới:\n\n{results_json}"
                
                # Simulate finding one page
                metadata_str = (
                    f"**Metadata:**\n"
                    f"- ID: 9999\n"
                    f"- Tiêu đề: Trang về '{query}'\n"
                    f"- Người tạo: Mock User\n"
                    f"- Ngày tạo: 2023-02-01T11:00:00Z\n"
                    f"- Cập nhật lần cuối bởi: Mock Editor\n"
                    f"- Ngày cập nhật cuối: 2023-02-15T16:45:00Z"
                )
                content = f"<h1>Trang mô phỏng về {query}</h1>\n<p>Nội dung mô phỏng cho truy vấn '{query}'.</p>"
                return f"📄 **Thông tin trang Confluence (Mô phỏng)**\n\n{metadata_str}\n\n**Nội dung:**\n{content}\n\n💡 **Lưu ý:** Để lấy nội dung thực, cần cấu hình."

            return "❌ (Mô phỏng) Cần cung cấp `page_id` hoặc `query`."
            
        elif action == "create_page":
            title = parameters.get('title', 'New Mock Page')
            space = parameters.get('space_key', 'MOCK')
            return f"✅ Trang Confluence mô phỏng đã được tạo thành công trong không gian '{space}' với tiêu đề: {title}"
        
        elif action == "update_page":
            page_id = parameters.get('page_id', '12345')
            return f"✅ Trang Confluence mô phỏng với ID '{page_id}' đã được cập nhật thành công."
            
        return "Mock result for unknown action."

    def _page_search(self, parameters: dict) -> str:
        """
        Searches for pages in Confluence. 
        
        It can search directly with a CQL query if `cql` is provided. Otherwise, 
        it builds a CQL query from `query`, `title`, and `space_key`.
        """
        cql = parameters.get("cql")
        
        if not cql:
            query = parameters.get("query") or parameters.get("title")
            space_key = parameters.get("space_key")

            if not query:
                return "❌ Cần cung cấp `cql` hoặc một `query` (hay `title`) để tìm kiếm."

            escaped_query = query.replace('"', '\\"')
            cql_parts = [f'text ~ "{escaped_query}"']
            if space_key:
                cql_parts.append(f'space.key = "{space_key.upper()}"')
            
            cql = " and ".join(cql_parts)
            print(f"CONFLUENCE_TOOL: No CQL provided. Building from parameters: {cql}")

        try:
            limit = parameters.get("limit", 25)
            results = self.confluence_client.cql(cql, limit=limit)
            if not results or 'results' not in results or not results['results']:
                 return f"ℹ️ Không tìm thấy kết quả nào cho CQL: {cql}"
            
            # Format for display, keeping only key info
            formatted_results = [
                {"id": r.get("content", {}).get("id"), "title": r.get("content", {}).get("title"), "space": r.get("space", {}).get("key")}
                for r in results["results"] if r.get("content")
            ]
            return f"🔍 Kết quả tìm kiếm Confluence với CQL '{cql}':\n\n{json.dumps(formatted_results, indent=2, ensure_ascii=False)}"
        except Exception as e:
            logger.error(f"Lỗi khi tìm kiếm Confluence với CQL '{cql}': {e}")
            return f"❌ Lỗi khi tìm kiếm Confluence: {str(e)}"

    def _format_page_with_metadata(self, page: dict) -> str:
        """Helper to format page content with rich metadata."""
        page_id = page.get('id')
        title = page.get('title', 'N/A')
        content = page.get('body', {}).get('storage', {}).get('value', '')
        
        # Extract metadata
        created_by = page.get('history', {}).get('createdBy', {}).get('displayName', 'N/A')
        created_at = page.get('history', {}).get('createdDate', 'N/A')
        last_updated_by = page.get('version', {}).get('by', {}).get('displayName', 'N/A')
        last_updated_at = page.get('version', {}).get('when', 'N/A')
        
        metadata_str = (
            f"**Metadata:**\n"
            f"- ID: {page_id}\n"
            f"- Tiêu đề: {title}\n"
            f"- Người tạo: {created_by}\n"
            f"- Ngày tạo: {created_at}\n"
            f"- Cập nhật lần cuối bởi: {last_updated_by}\n"
            f"- Ngày cập nhật cuối: {last_updated_at}"
        )
        
        return f"📄 **Thông tin trang Confluence**\n\n{metadata_str}\n\n**Nội dung:**\n{content}"

    def _get_page_content(self, parameters: dict) -> str:
        """
        Retrieves Confluence page content.
        
        It can fetch by page_id directly. If no page_id is given, it performs a full-text
        search based on a query, title, or keywords. If one page is found, its content
        is returned. If multiple pages are found, a list is returned for the user to select from.
        """
        page_id = parameters.get("page_id")
        
        # If page_id is provided, fetch content directly.
        if page_id:
            try:
                page = self.confluence_client.get_page_by_id(str(page_id), expand='body.storage,history,version')
                return self._format_page_with_metadata(page)
            except Exception as e:
                logger.error(f"Lỗi khi lấy nội dung trang Confluence (ID: {page_id}): {e}")
                return f"❌ Lỗi khi lấy nội dung trang Confluence (ID: {page_id}): {str(e)}"

        # If no page_id, perform a search.
        query = parameters.get("query") or parameters.get("title")
        space_key = parameters.get("space_key")

        if not query:
            return "❌ Cần cung cấp `page_id` hoặc một `query` (hay `title`) để tìm kiếm và lấy nội dung trang."

        escaped_query = query.replace('"', '\\"')
        cql_parts = [f'text ~ "{escaped_query}"']
        if space_key:
            cql_parts.append(f'space.key = "{space_key.upper()}"')
        
        cql = " and ".join(cql_parts)
        limit = parameters.get("limit", 10) # Add a configurable limit

        print(f"CONFLUENCE_TOOL: No page_id provided. Searching with CQL: {cql}")

        try:
            search_response = self.confluence_client.cql(cql, limit=limit)
            results = search_response.get('results', [])

            if not results:
                return f"ℹ️ Không tìm thấy trang nào khớp với truy vấn của bạn. CQL đã dùng: {cql}"

            # If only one result, fetch its content directly.
            if len(results) == 1:
                found_page = results[0]['content']
                page_id = found_page['id']
                print(f"CONFLUENCE_TOOL: Found one match (ID: {page_id}). Fetching its content.")
                # Recurse or just fetch
                page_with_content = self.confluence_client.get_page_by_id(page_id, expand='body.storage,history,version')
                return self._format_page_with_metadata(page_with_content)
            
            # If multiple results, return a list for the user to choose.
            else:
                formatted_results = [
                    {"id": r['content']['id'], "title": r['content']['title'], "space": r['space']['key']}
                    for r in results if 'content' in r and 'space' in r
                ]
                results_json = json.dumps(formatted_results, indent=2, ensure_ascii=False)
                return f"✅ Tìm thấy nhiều trang phù hợp. Vui lòng chạy lại công cụ với `page_id` cụ thể từ danh sách bên dưới:\n\n{results_json}"

        except Exception as e:
            logger.error(f"Lỗi khi tìm kiếm trang Confluence với CQL '{cql}': {e}", exc_info=True)
            return f"❌ Đã xảy ra lỗi không mong muốn khi tìm kiếm trang: {str(e)}"

    def _create_page(self, parameters: dict) -> str:
        """Creates a new page in a Confluence space."""
        space_key = parameters.get("space_key")
        title = parameters.get("title")
        content = parameters.get("content")
        parent_page_id = parameters.get("parent_page_id") # Optional

        if not all([space_key, title, content]):
            return "❌ Để tạo trang, cần cung cấp đủ 'space_key', 'title', và 'content'."

        try:
            result = self.confluence_client.create_page(
                space=space_key,
                title=title,
                body=content,
                parent_id=parent_page_id,
                # type='page', representation='storage' # Defaults are usually fine
            )
            # The result is a dictionary containing information about the new page.
            page_id = result.get('id')
            page_url = result.get('_links', {}).get('webui', '')
            return f"✅ Trang Confluence đã được tạo thành công!\n- ID: {page_id}\n- URL: {self.confluence_url}{page_url}"
        except Exception as e:
            logger.error(f"Lỗi khi tạo trang Confluence: {e}")
            return f"❌ Lỗi khi tạo trang Confluence: {str(e)}"

    def _update_page(self, parameters: dict) -> str:
        """Updates an existing Confluence page."""
        page_id = parameters.get("page_id")
        title = parameters.get("title")
        content = parameters.get("content")
        
        if "page_id" not in parameters or "title" not in parameters or "content" not in parameters:
            return "❌ Để cập nhật trang, cần cung cấp đủ 'page_id', 'title', và 'content'."
            
        try:
            result = self.confluence_client.update_page(
                page_id=page_id,
                title=title,
                body=content,
            )
            page_url = result.get('_links', {}).get('webui', '')
            return f"✅ Trang Confluence (ID: {parameters['page_id']}) đã được cập nhật thành công!\n- URL: {self.confluence_url}{page_url}"
        except Exception as e:
            logger.error(f"Lỗi khi cập nhật trang Confluence: {e}")
            return f"❌ Lỗi khi cập nhật trang Confluence: {str(e)}"
            
    async def _arun(self, action: Optional[str] = None, parameters: Optional[dict] = None) -> str:
        """Asynchronous execution is not implemented, defaulting to synchronous."""
        return self._run(action, parameters)
        
def create_confluence_tool(confluence_url: str = None, username: str = None, api_token: str = None) -> ConfluenceTool:
    """Create a Confluence tool instance with configuration."""
    return ConfluenceTool(
        confluence_url=confluence_url,
        username=username,
        api_token=api_token
    )

# Export the tool
__all__ = ['ConfluenceTool', 'create_confluence_tool'] 
