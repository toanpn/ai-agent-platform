"""
RAG Tool Module

This module provides a RAG (Retrieval-Augmented Generation) lookup tool that agents
can use to search their knowledge base and retrieve relevant information.
"""

import logging
from typing import List, Dict, Any, Optional, Type
from langchain.tools import BaseTool, tool
from pydantic import BaseModel, Field

from core.rag_service import RAGService

logger = logging.getLogger(__name__)

class KnowledgeSearchInput(BaseModel):
    """Input schema for knowledge search tool."""
    query: str = Field(description="The search query to find relevant information")
    agent_id: Optional[str] = Field(default=None, description="Filter results by specific agent ID")
    max_results: Optional[int] = Field(default=5, description="Maximum number of results to return")

class KnowledgeSearchTool(BaseTool):
    """RAG-based knowledge search tool for agents."""
    
    name: str = "knowledge_search"
    description: str = """
    Công cụ tìm kiếm thông tin từ cơ sở tri thức của agent sử dụng RAG.
    Sử dụng công cụ này khi bạn cần:
    - Tìm thông tin từ các tài liệu đã tải lên
    - Trả lời câu hỏi dựa trên nội dung tài liệu
    - Tham khảo các chính sách, hướng dẫn đã lưu trữ
    - Tra cứu thông tin chi tiết từ cơ sở dữ liệu tri thức
    """
    args_schema: Type[BaseModel] = KnowledgeSearchInput
    rag_service: Optional[RAGService] = None
    
    def __init__(self, rag_service: RAGService = None, **kwargs):
        super().__init__(**kwargs)
        self.rag_service = rag_service or RAGService()
    
    def _run(self, query: str, agent_id: Optional[str] = None, max_results: Optional[int] = 5) -> str:
        """Execute the knowledge search."""
        try:
            # Perform the search
            results = self.rag_service.search_knowledge(
                query=query,
                agent_id=agent_id,
                n_results=max_results or 5
            )
            
            if not results:
                return f"Không tìm thấy thông tin liên quan đến: {query}"
            
            # Format the results
            formatted_response = f"🔍 Tìm thấy {len(results)} thông tin liên quan đến câu hỏi: '{query}'\n\n"
            
            for i, result in enumerate(results, 1):
                content = result.get('content', '')
                metadata = result.get('metadata', {})
                
                # Add result header
                formatted_response += f"📄 **Kết quả {i}:**\n"
                
                # Add source information if available
                if 'file_name' in metadata:
                    formatted_response += f"📁 Nguồn: {metadata['file_name']}\n"
                elif 'source_url' in metadata:
                    formatted_response += f"🌐 Nguồn: {metadata['source_url']}\n"
                elif 'source' in metadata:
                    formatted_response += f"📂 Nguồn: {metadata['source']}\n"
                
                # Add content
                formatted_response += f"📝 Nội dung: {content}\n"
                
                # Add separator
                if i < len(results):
                    formatted_response += "\n" + "─" * 50 + "\n\n"
            
            return formatted_response
            
        except Exception as e:
            logger.error(f"Error in knowledge search: {e}")
            return f"❌ Lỗi khi tìm kiếm thông tin: {str(e)}"
    
    async def _arun(self, query: str, agent_id: Optional[str] = None, max_results: Optional[int] = 5) -> str:
        """Async version of the knowledge search."""
        return self._run(query, agent_id, max_results)

# Tool factory function for easy integration
def create_knowledge_search_tool(rag_service: RAGService = None) -> KnowledgeSearchTool:
    """Create a knowledge search tool instance."""
    return KnowledgeSearchTool(rag_service=rag_service)

# Export the tools for agent manager
__all__ = ['KnowledgeSearchTool', 'create_knowledge_search_tool'] 