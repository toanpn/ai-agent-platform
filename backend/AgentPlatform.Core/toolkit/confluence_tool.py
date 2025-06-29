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
    action: Optional[str] = Field(default=None, description="Hành động Confluence cần thực hiện (ví dụ: 'page_search', 'get_page_content', 'create_page', 'update_page').")
    parameters: Union[dict, str, None] = Field(default_factory=dict, description="Các tham số cho hành động Confluence dưới dạng dictionary hoặc JSON string.")

    @validator("parameters", pre=True)
    def parameters_must_be_dict(cls, v):
        if v is None:
            return {}
        if isinstance(v, str):
            if not v.strip():
                return {}
            try:
                # First, try to parse as JSON, which is stricter
                return json.loads(v)
            except json.JSONDecodeError:
                # If JSON parsing fails, try to evaluate as a Python literal
                # This can handle dicts with single quotes, etc.
                try:
                    parsed_v = ast.literal_eval(v)
                    if isinstance(parsed_v, dict):
                        return parsed_v
                    else:
                        raise ValueError("Evaluated string is not a dictionary")
                except (ValueError, SyntaxError, MemoryError, TypeError) as e:
                    raise ValueError(f"parameters string is not a valid JSON or Python dictionary literal: {e}")
        return v

class ConfluenceTool(BaseTool):
    """Unified Confluence tool for agents using atlassian-python-api."""
    
    name: str = "confluence"
    description: str = """
    Công cụ toàn diện để tương tác với Confluence.
    **Quan trọng:** Để tìm và đọc một trang, hãy sử dụng action `get_page_content` với `title` và `space_key`. 
    Công cụ sẽ tự động tìm kiếm trang và trả về nội dung nếu tìm thấy một kết quả duy nhất.

    **Hành động và Cách dùng:**

    - **Lấy nội dung trang theo tiêu đề (Cách được khuyến khích):**
      action: "get_page_content"
      parameters: {{"title": "Tiêu đề trang gần đúng", "space_key": "KEY"}}

    - **Tìm kiếm trang (Nâng cao):**
      action: "page_search"
      parameters: {{"cql": "space.key = 'KEY' and title ~ 'tiêu đề'"}}

    - **Lấy nội dung trang theo ID (Nếu đã biết):**
      action: "get_page_content"
      parameters: {{"page_id": "12345"}}

    - **Tạo trang mới:**
      action: "create_page"
      parameters: {{"space_key": "KEY", "title": "Tiêu đề trang", "content": "Nội dung HTML", "parent_page_id": "12345" (Tùy chọn)}}

    - **Cập nhật trang:**
      action: "update_page"
      parameters: {{"page_id": "12345", "title": "Tiêu đề mới", "content": "Nội dung HTML mới"}}
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
            cql = parameters.get('cql', 'test query')
            return f"""🔍 Kết quả tìm kiếm Confluence mô phỏng với CQL '{cql}':

- **Mock Page 1**: ID 12345, Space: MOCK
- **Mock Page 2**: ID 67890, Space: MOCK

💡 **Lưu ý:** Để tìm kiếm thực, cần cấu hình CONFLUENCE_URL, CONFLUENCE_USERNAME, và CONFLUENCE_API_TOKEN"""
        
        elif action == "get_page_content":
            page_id = parameters.get('page_id', '12345')
            return f"""📄 Nội dung trang Confluence mô phỏng (ID: {page_id}):

<h1>Tiêu đề trang mô phỏng</h1>
<p>Đây là nội dung của một trang Confluence mô phỏng.</p>

💡 **Lưu ý:** Để lấy nội dung thực, cần cấu hình CONFLUENCE_URL, CONFLUENCE_USERNAME, và CONFLUENCE_API_TOKEN"""
            
        elif action == "create_page":
            title = parameters.get('title', 'New Mock Page')
            space = parameters.get('space_key', 'MOCK')
            return f"✅ Trang Confluence mô phỏng đã được tạo thành công trong không gian '{space}' với tiêu đề: {title}"
        
        elif action == "update_page":
            page_id = parameters.get('page_id', '12345')
            return f"✅ Trang Confluence mô phỏng với ID '{page_id}' đã được cập nhật thành công."
            
        return "Mock result for unknown action."

    def _page_search(self, parameters: dict) -> str:
        """Searches for pages in Confluence using CQL."""
        cql = parameters.get("cql")
        if not cql:
            return "❌ Thiếu tham số 'cql' (Confluence Query Language) để tìm kiếm."
        
        try:
            results = self.confluence_client.cql(cql, limit=25)
            if not results or 'results' not in results or not results['results']:
                 return f"ℹ️ Không tìm thấy kết quả nào cho CQL: {cql}"
            
            # Format for display, keeping only key info
            formatted_results = [
                {"id": r.get("content", {}).get("id"), "title": r.get("content", {}).get("title"), "space": r.get("space", {}).get("key")}
                for r in results["results"]
            ]
            return f"🔍 Kết quả tìm kiếm Confluence với CQL '{cql}':\n\n{json.dumps(formatted_results, indent=2, ensure_ascii=False)}"
        except Exception as e:
            logger.error(f"Lỗi khi tìm kiếm Confluence với CQL '{cql}': {e}")
            return f"❌ Lỗi khi tìm kiếm Confluence: {str(e)}"

    def _get_page_content(self, parameters: dict) -> str:
        """Retrieves the content of a specific Confluence page by ID, or by finding the ID first using title and space."""
        target_page_id = parameters.get("page_id")
        title = parameters.get("title")
        space_key = parameters.get("space_key")

        if not target_page_id and not title:
            return "❌ Cần cung cấp `page_id` hoặc `title` để lấy nội dung trang."

        # If no page_id is provided, search by title and space to find it
        if not target_page_id and title:
            print(f"CONFLUENCE_TOOL: No page_id. Searching for page with title '{title}' in space '{space_key or 'any'}'")
            # Use contains (~) for more flexible search, but still prioritize exact match.
            # Escaping double quotes inside the CQL query string
            escaped_title = title.replace('"', '\\"')
            cql = f'title ~ "{escaped_title}"'
            if space_key:
                cql += f' and space.key = "{space_key}"'
            
            try:
                search_response = self.confluence_client.cql(cql, limit=50)
                # The actual page results are in the 'results' list, each containing a 'content' object
                search_results = [r.get('content', {}) for r in search_response.get('results', [])]

                # Filter for exact title match, as CQL search is 'contains'
                exact_matches = [r for r in search_results if r.get('title') == title]

                if len(exact_matches) == 1:
                    target_page_id = exact_matches[0]['id']
                    print(f"CONFLUENCE_TOOL: Found exact match page ID '{target_page_id}' for title '{title}'")
                elif len(exact_matches) > 1:
                    # If multiple exact matches, return them for user to select
                    formatted_results = json.dumps([{"id": r['id'], "title": r['title']} for r in exact_matches], indent=2, ensure_ascii=False)
                    return f"✅ Tìm thấy nhiều trang có cùng tiêu đề chính xác '{title}'. Vui lòng cung cấp `page_id` từ danh sách sau:\n\n{formatted_results}"
                
                # If no exact match, check fuzzy results from the 'title ~' search
                elif len(search_results) == 1:
                    # If only one fuzzy match, assume it's the correct one.
                    target_page_id = search_results[0]['id']
                    page_title = search_results[0].get('title', 'N/A')
                    print(f"CONFLUENCE_TOOL: No exact match found. Found a single related page. Assuming it's correct. ID: '{target_page_id}', Title: '{page_title}'")
                elif len(search_results) > 1:
                    # If multiple fuzzy matches, return them for user to select
                    formatted_results = json.dumps([{"id": r['id'], "title": r['title']} for r in search_results], indent=2, ensure_ascii=False)
                    return f"✅ Không tìm thấy trang nào có tiêu đề chính xác là '{title}', nhưng đã tìm thấy các trang liên quan sau. Vui lòng cung cấp `page_id` từ danh sách:\n\n{formatted_results}"
                else:
                    # If no results at all
                    return f"❌ Không tìm thấy trang nào trong Confluence có tiêu đề chứa '{title}' trong không gian '{space_key or 'bất kỳ'}'. CQL đã dùng: {cql}"
            except Exception as e:
                logger.error(f"Lỗi khi tìm kiếm trang Confluence: {e}")
                return f"❌ Đã xảy ra lỗi không mong muốn khi tìm kiếm trang: {e}"

        if not target_page_id:
            return "❌ Không thể xác định page_id để lấy nội dung. Vui lòng cung cấp ID trang hoặc tiêu đề chính xác hơn."

        try:
            # Use expand='body.storage' to get the content in HTML format
            page = self.confluence_client.get_page_by_id(str(target_page_id), expand='body.storage')
            content = page.get('body', {}).get('storage', {}).get('value', '')
            return f"📄 Nội dung trang Confluence (ID: {target_page_id}):\n\n{content}"
        except Exception as e:
            logger.error(f"Lỗi khi lấy nội dung trang Confluence (ID: {target_page_id}): {e}")
            return f"❌ Lỗi khi lấy nội dung trang Confluence (ID: {target_page_id}): {str(e)}"

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
