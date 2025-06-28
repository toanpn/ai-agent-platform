"""
Google Search Tool Module

This module provides Google search functionality using LangChain's GoogleSearchAPIWrapper.
Based on: https://python.langchain.com/docs/integrations/tools/google_search/
"""

import os
import logging
from typing import Optional, Type
from langchain.tools import BaseTool, tool
from langchain_core.tools import Tool
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Try to import Google Search API wrapper
try:
    from langchain_google_community import GoogleSearchAPIWrapper
    GOOGLE_SEARCH_AVAILABLE = True
except ImportError:
    GOOGLE_SEARCH_AVAILABLE = False
    logger.warning("Google Search API not available. Install with: pip install langchain-google-community")

class GoogleSearchInput(BaseModel):
    """Input schema for Google search tool."""
    query: str = Field(description="The search query string")
    num_results: Optional[int] = Field(default=5, description="Number of search results to return")

class GoogleSearchTool(BaseTool):
    """Google search tool for agents."""
    
    name: str = "google_search"
    description: str = """
    Công cụ tìm kiếm Google để tìm thông tin hiện tại trên internet.
    Sử dụng khi cần:
    - Tìm thông tin mới nhất trên internet
    - Tìm tin tức, sự kiện hiện tại
    - Nghiên cứu chủ đề cụ thể
    - Kiểm tra thông tin cập nhật
    """
    args_schema: Type[BaseModel] = GoogleSearchInput
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    def _run(self, query: str, num_results: Optional[int] = 5) -> str:
        """Execute Google search."""
        try:
            if not GOOGLE_SEARCH_AVAILABLE:
                return "❌ Google Search API không khả dụng. Cần cài đặt: pip install langchain-google-community"
            
            # Enhanced query validation
            if query is None:
                return "❌ Lỗi: Tham số query là bắt buộc"
            
            if not isinstance(query, str):
                return "❌ Lỗi: Query phải là chuỗi văn bản"
            
            query = query.strip()
            if not query:
                return "❌ Lỗi: Câu truy vấn tìm kiếm không thể để trống hoặc chỉ chứa khoảng trắng"
            
            if len(query) < 2:
                return "❌ Lỗi: Câu truy vấn tìm kiếm phải có ít nhất 2 ký tự"
            
            # Validate num_results
            if num_results is not None and (not isinstance(num_results, int) or num_results < 1 or num_results > 10):
                num_results = 5
                
            logger.info(f"Executing Google search for query: '{query}' with {num_results} results")
            
            # Check for required environment variables
            api_key = os.getenv("GOOGLE_API_KEY")
            cse_id = os.getenv("GOOGLE_CSE_ID")
            
            if not api_key or not cse_id:
                # Return mock results for demo
                return self._mock_search_results(query, num_results)
            
            # Final validation before API call
            if not query or len(query.strip()) == 0:
                return "❌ Lỗi: Không thể thực hiện tìm kiếm với query rỗng"
            
            # Initialize Google Search API wrapper
            search = GoogleSearchAPIWrapper(k=num_results or 5)
            
            # Perform search and get detailed results
            # Double-check query before sending to API
            final_query = query.strip()
            if not final_query:
                return "❌ Lỗi: Query bị rỗng sau khi xử lý"
                
            results = search.results(final_query, num_results or 5)
            
            if not results:
                return f"Không tìm thấy kết quả cho: {query}"
            
            # Format results
            formatted_response = f"🔍 Kết quả tìm kiếm Google cho '{query}':\n\n"
            
            for i, result in enumerate(results, 1):
                title = result.get('title', 'Không có tiêu đề')
                snippet = result.get('snippet', 'Không có mô tả')
                link = result.get('link', '#')
                
                formatted_response += f"**{i}. {title}**\n"
                formatted_response += f"📝 {snippet}\n"
                formatted_response += f"🔗 {link}\n\n"
            
            return formatted_response
            
        except Exception as e:
            logger.error(f"Error in Google search: {e}")
            return f"❌ Lỗi khi tìm kiếm Google: {str(e)}"
    
    def _mock_search_results(self, query: str, num_results: int) -> str:
        """Return mock search results when API is not configured."""
        mock_results = [
            {
                "title": f"Thông tin mới nhất về {query}",
                "snippet": f"Hướng dẫn toàn diện và cập nhật gần đây về {query}. Bao gồm các khía cạnh quan trọng và xu hướng hiện tại.",
                "link": "https://example.com/search-1"
            },
            {
                "title": f"Cách thực hiện {query} - Hướng dẫn đầy đủ",
                "snippet": f"Hướng dẫn từng bước và thực tiễn tốt nhất cho {query}. Học từ chuyên gia và nhận mẹo thực tế.",
                "link": "https://example.com/guide-2"
            },
            {
                "title": f"{query} - Tin tức và Cập nhật",
                "snippet": f"Tin tức gần đây và phát triển liên quan đến {query}. Cập nhật thông tin mới nhất.",
                "link": "https://example.com/news-3"
            }
        ]
        
        formatted_response = f"🔍 Kết quả tìm kiếm mô phỏng cho '{query}' (API chưa được cấu hình):\n\n"
        
        for i, result in enumerate(mock_results[:num_results], 1):
            formatted_response += f"**{i}. {result['title']}**\n"
            formatted_response += f"📝 {result['snippet']}\n"
            formatted_response += f"🔗 {result['link']}\n\n"
        
        formatted_response += "\n💡 **Lưu ý:** Để sử dụng tìm kiếm Google thực, cần cấu hình GOOGLE_API_KEY và GOOGLE_CSE_ID"
        
        return formatted_response
    
    async def _arun(self, query: str, num_results: Optional[int] = 5) -> str:
        """Async version of Google search."""
        return self._run(query, num_results)

# Simple function-based tool for backward compatibility
@tool
def google_search_simple(query: str) -> str:
    """
    Tìm kiếm Google đơn giản.
    
    Args:
        query: Câu truy vấn tìm kiếm
        
    Returns:
        Kết quả tìm kiếm từ Google
    """
    tool = GoogleSearchTool()
    return tool._run(query)

# Tool factory function
def create_google_search_tool() -> GoogleSearchTool:
    """Create a Google search tool instance."""
    return GoogleSearchTool()

# Export the tools
__all__ = ['GoogleSearchTool', 'create_google_search_tool', 'google_search_simple'] 