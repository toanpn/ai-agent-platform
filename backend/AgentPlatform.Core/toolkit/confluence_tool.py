"""
Confluence Tool Module

This module provides Confluence functionality using LangChain's Confluence toolkit.
Based on: https://python.langchain.com/docs/integrations/tools/confluence/
"""

import os
import logging
import json
import ast
from typing import Optional, Type, List, Union
from langchain.tools import BaseTool
from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)

# Try to import Confluence toolkit
try:
    from langchain_community.agent_toolkits.confluence.toolkit import ConfluenceToolkit
    from langchain_community.utilities.confluence import ConfluenceAPIWrapper
    CONFLUENCE_AVAILABLE = True
except ImportError:
    CONFLUENCE_AVAILABLE = False
    logger.warning("Confluence toolkit không khả dụng. Cài đặt với: pip install langchain-community atlassian-python-api")

class ConfluenceToolInput(BaseModel):
    """Input schema for Confluence tool."""
    action: Optional[str] = Field(default=None, description="Hành động Confluence cần thực hiện (ví dụ: 'page_search', 'get_page_content', 'create_page', 'update_page')")
    parameters: Union[dict, str, None] = Field(default_factory=dict, description="Tham số cho hành động Confluence, dưới dạng dictionary hoặc JSON string.")

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
    """Unified Confluence tool for agents using LangChain's ConfluenceToolkit."""

    name: str = "confluence"
    description: str = """
    Công cụ Confluence tích hợp để quản lý các trang.
    Sử dụng khi cần:
    - Tìm kiếm trang trong Confluence (action: 'page_search')
    - Lấy nội dung của một trang cụ thể (action: 'get_page_content')
    - Tạo một trang mới (action: 'create_page')
    - Cập nhật một trang đã có (action: 'update_page')

    Hướng dẫn sử dụng:
    - Để tìm kiếm trang: action="page_search", parameters={{"query": "tiêu đề trang hoặc từ khóa", "space_key": "SPACEKEY"}}
    - Để lấy nội dung trang: action="get_page_content", parameters={{"page_id": 12345}}
    - Để tạo trang mới: action="create_page", parameters={{"space_key": "SPACEKEY", "title": "Tiêu đề trang mới", "content": "Nội dung trang..."}}
    - Để cập nhật trang: action="update_page", parameters={{"page_id": 12345, "title": "Tiêu đề mới", "content": "Nội dung mới..."}}
    """
    args_schema: Type[BaseModel] = ConfluenceToolInput

    confluence_url: Optional[str] = None
    confluence_username: Optional[str] = None
    confluence_api_token: Optional[str] = None
    confluence_toolkit: Optional[ConfluenceToolkit] = None
    initialization_error: Optional[str] = None

    def __init__(self, confluence_base_url: str = None, confluence_username: str = None, confluence_api_token: str = None, **kwargs):
        super().__init__(**kwargs)

        self.confluence_url = confluence_base_url or os.getenv("CONFLUENCE_BASE_URL")
        self.confluence_username = confluence_username or os.getenv("CONFLUENCE_USERNAME")
        self.confluence_api_token = confluence_api_token or os.getenv("CONFLUENCE_API_TOKEN")

        if CONFLUENCE_AVAILABLE and all([self.confluence_url, self.confluence_username, self.confluence_api_token]):
            try:
                confluence_api = ConfluenceAPIWrapper(
                    confluence_url=self.confluence_url,
                    username=self.confluence_username,
                    api_key=self.confluence_api_token
                )
                self.confluence_toolkit = ConfluenceToolkit.from_confluence_api_wrapper(confluence_api)
            except Exception as e:
                error_message = f"Không thể khởi tạo Confluence toolkit. Vui lòng kiểm tra lại thông tin cấu hình (URL, username, token). Lỗi: {e}"
                logger.error(error_message)
                self.initialization_error = error_message
                self.confluence_toolkit = None

    def _run(self, action: Optional[str] = None, parameters: Optional[dict] = None) -> str:
        """Execute Confluence action using the unified toolkit."""
        if not action:
            return f"❌ Thiếu tham số 'action'. Các hành động khả dụng:\n{self.description}"

        params = parameters or {}

        print(f"CONFLUENCE_TOOL: Executing action='{action}' with parameters={params}")
        try:
            if not CONFLUENCE_AVAILABLE:
                return "❌ Confluence toolkit không khả dụng. Cần cài đặt: pip install langchain-community atlassian-python-api"

            if self.initialization_error:
                return f"❌ {self.initialization_error}"

            if not self.confluence_toolkit:
                return self._mock_result(action, **params)

            tools = self.confluence_toolkit.get_tools()

            if action == "page_search":
                return self._page_search(tools, params)
            elif action == "get_page_content":
                return self._get_page_content(tools, params)
            elif action == "create_page":
                return self._create_page(tools, params)
            elif action == "update_page":
                return self._update_page(tools, params)
            else:
                return f"❌ Hành động không được hỗ trợ: {action}. Các hành động khả dụng: page_search, get_page_content, create_page, update_page"

        except Exception as e:
            logger.error(f"Error in Confluence tool: {e}")
            print(f"CONFLUENCE_TOOL: Error during _run: {e}")
            return f"❌ Lỗi khi thực hiện Confluence action '{action}': {str(e)}"

    def _find_tool(self, tools: List[BaseTool], tool_name: str) -> Optional[BaseTool]:
        for tool in tools:
            if tool.name.lower() == tool_name.lower():
                return tool
        return None

    def _page_search(self, tools: List[BaseTool], parameters: dict) -> str:
        """Search for pages in Confluence."""
        search_tool = self._find_tool(tools, "Search pages")
        if not search_tool:
            return "❌ Không tìm thấy công cụ tìm kiếm trang"

        try:
            query = parameters.get("query")
            if not query:
                return "❌ Thiếu tham số 'query' để tìm kiếm."
            
            space_key = parameters.get("space_key")
            limit = parameters.get("limit", 5)
            
            tool_input = {"query": query, "space_key": space_key, "limit": limit}
            # Filter out None values
            tool_input = {k: v for k, v in tool_input.items() if v is not None}
            
            result = search_tool.run(tool_input)
            return f"🔍 Kết quả tìm kiếm trang Confluence cho '{query}':\n\n{result}"
        except Exception as e:
            return f"❌ Lỗi khi tìm kiếm trang Confluence: {str(e)}"

    def _get_page_content(self, tools: List[BaseTool], parameters: dict) -> str:
        """Get content of a Confluence page."""
        get_tool = self._find_tool(tools, "Get page content by page id")
        if not get_tool:
            return "❌ Không tìm thấy công cụ lấy nội dung trang"

        try:
            page_id = parameters.get("page_id")
            if not page_id:
                return "❌ Thiếu 'page_id' để lấy nội dung trang"

            result = get_tool.run({"page_id": page_id})
            return f"📄 Nội dung trang Confluence (ID: {page_id}):\n\n{result}"
        except Exception as e:
            return f"❌ Lỗi khi lấy nội dung trang Confluence: {str(e)}"
            
    def _create_page(self, tools: List[BaseTool], parameters: dict) -> str:
        """Create a new Confluence page."""
        create_tool = self._find_tool(tools, "Create Page")
        if not create_tool:
            return "❌ Không tìm thấy công cụ tạo trang"

        try:
            space_key = parameters.get("space_key")
            title = parameters.get("title")
            content = parameters.get("content")
            parent_id = parameters.get("parent_id")
            
            if not all([space_key, title, content]):
                return "❌ Thiếu các trường bắt buộc: 'space_key', 'title', 'content'"

            tool_input = {"space_key": space_key, "title": title, "content": content, "parent_id": parent_id}
            tool_input = {k: v for k, v in tool_input.items() if v is not None}
            
            result = create_tool.run(tool_input)
            return f"✅ Trang Confluence đã được tạo thành công!\n\n{result}"
        except Exception as e:
            return f"❌ Lỗi khi tạo trang Confluence: {str(e)}"

    def _update_page(self, tools: List[BaseTool], parameters: dict) -> str:
        """Update an existing Confluence page."""
        update_tool = self._find_tool(tools, "Update Page")
        if not update_tool:
            return "❌ Không tìm thấy công cụ cập nhật trang"

        try:
            page_id = parameters.get("page_id")
            title = parameters.get("title")
            content = parameters.get("content")
            
            if not page_id or not title or not content:
                 return "❌ Thiếu các trường bắt buộc: 'page_id', 'title', 'content'"

            tool_input = {"page_id": page_id, "title": title, "content": content}
            
            result = update_tool.run(tool_input)
            return f"✅ Trang Confluence (ID: {page_id}) đã được cập nhật thành công!\n\n{result}"
        except Exception as e:
            return f"❌ Lỗi khi cập nhật trang Confluence: {str(e)}"

    def _mock_result(self, action: str, **parameters: dict) -> str:
        """Return mock results when Confluence is not configured."""
        if action == "page_search":
            query = parameters.get('query', 'Test Query')
            return f"""🔍 Kết quả tìm kiếm Confluence mô phỏng cho '{query}':

📄 **Page ID: 12345** - Project Plan Q3
   Không gian: DEV
   Tác giả: john.doe
   Cập nhật lần cuối: 2024-07-20

📄 **Page ID: 67890** - API Documentation
   Không gian: DEV
   Tác giả: jane.smith
   Cập nhật lần cuối: 2024-07-19

💡 **Lưu ý:** Để tìm kiếm Confluence thực, cần cấu hình CONFLUENCE_BASE_URL, CONFLUENCE_USERNAME, và CONFLUENCE_API_TOKEN"""

        elif action == "get_page_content":
            page_id = parameters.get('page_id', 98765)
            return f"""📄 Nội dung trang Confluence mô phỏng (ID: {page_id}):

**Tiêu đề:** Onboarding new developers

**Nội dung:**
Chào mừng đến với team! Dưới đây là các bước để bắt đầu:
1. Thiết lập môi trường phát triển...
2. Đọc tài liệu kiến trúc...
3. Tham gia cuộc họp team hàng ngày...

💡 **Lưu ý:** Để lấy nội dung trang thực, cần cấu hình CONFLUENCE_BASE_URL, CONFLUENCE_USERNAME, và CONFLUENCE_API_TOKEN"""
            
        elif action == "create_page":
            title = parameters.get('title', 'Trang Test')
            space = parameters.get('space_key', 'TEST')
            return f"""✅ Trang Confluence mô phỏng đã được tạo thành công!

**ID Trang:** {hash(title) % 100000 + 50000}
**Tiêu đề:** {title}
**Không gian:** {space}
**Nội dung:** {parameters.get('content', 'Đây là nội dung mặc định.')}

💡 **Lưu ý:** Để tạo trang Confluence thực, cần cấu hình CONFLUENCE_BASE_URL, CONFLUENCE_USERNAME, và CONFLUENCE_API_TOKEN"""

        elif action == "update_page":
            page_id = parameters.get('page_id', 11223)
            return f"""✅ Trang Confluence mô phỏng (ID: {page_id}) đã được cập nhật thành công!

**ID Trang:** {page_id}
**Tiêu đề mới:** {parameters.get('title', 'Tiêu đề đã cập nhật')}
**Nội dung mới đã được lưu.**

💡 **Lưu ý:** Để cập nhật trang Confluence thực, cần cấu hình CONFLUENCE_BASE_URL, CONFLUENCE_USERNAME, và CONFLUENCE_API_TOKEN"""
        
        else:
            return f"❌ Hành động không được hỗ trợ: {action}"

    async def _arun(self, action: Optional[str] = None, parameters: Optional[dict] = None) -> str:
        """Async version of the _run method."""
        return self._run(action, parameters)

def create_confluence_tool(confluence_base_url: str = None, confluence_username: str = None, confluence_api_token: str = None) -> ConfluenceTool:
    """Create a Confluence tool instance with configuration."""
    return ConfluenceTool(
        confluence_base_url=confluence_base_url,
        confluence_username=confluence_username,
        confluence_api_token=confluence_api_token
    )

# Export the tool
__all__ = ['ConfluenceTool', 'create_confluence_tool'] 
