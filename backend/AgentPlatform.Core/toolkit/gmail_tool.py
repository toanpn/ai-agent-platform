"""
Gmail Tool Module

This module provides Gmail functionality using LangChain's Gmail toolkit.
Based on: https://python.langchain.com/docs/integrations/tools/gmail/
"""

import os
import logging
from typing import Optional, Type, List, Dict, Any
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Try to import Gmail toolkit
try:
    from langchain_community.tools.gmail.utils import (
        build_resource_service,
        get_gmail_credentials,
    )
    from langchain_community.tools.gmail import (
        GmailCreateDraft,
        GmailGetMessage,
        GmailGetThread,
        GmailSearch,
        GmailSendMessage,
    )
    GMAIL_AVAILABLE = True
except ImportError:
    GMAIL_AVAILABLE = False
    logger.warning("Gmail toolkit không khả dụng. Cài đặt với: pip install langchain-community")

class GmailToolInput(BaseModel):
    """Input schema for Gmail tool."""
    action: str = Field(description="Hành động Gmail cần thực hiện (search, send, get_message)")
    parameters: dict = Field(description="Tham số cho hành động Gmail")

class GmailTool(BaseTool):
    """Unified Gmail tool for agents using LangChain's Gmail toolkit."""
    
    name: str = "gmail"
    description: str = """
    Công cụ Gmail tích hợp cho quản lý email.
    Sử dụng khi cần:
    - Tìm kiếm emails trong Gmail
    - Gửi emails mới
    - Lấy nội dung email cụ thể
    - Tạo draft emails
    
    Hướng dẫn sử dụng:
    - Để tìm kiếm: action="search", parameters={"query": "from:example@gmail.com", "max_results": 10}
    - Để gửi email: action="send", parameters={"to": "recipient@email.com", "subject": "chủ đề", "message": "nội dung"}
    - Để lấy email: action="get_message", parameters={"message_id": "message_id_here"}
    """
    args_schema: Type[BaseModel] = GmailToolInput
    
    def __init__(self, gmail_credentials_path: str = None, **kwargs):
        super().__init__(**kwargs)
        self.gmail_credentials_path = gmail_credentials_path or os.getenv("GMAIL_CREDENTIALS_PATH")
        
    def _run(self, action: str, parameters: dict) -> str:
        """Execute Gmail action using the unified approach."""
        try:
            if not GMAIL_AVAILABLE:
                return "❌ Gmail toolkit không khả dụng. Cần cài đặt: pip install langchain-community"
            
            # Check for Gmail configuration
            if not self.gmail_credentials_path:
                return self._mock_result(action, parameters)
            
            # Build Gmail service
            try:
                credentials = get_gmail_credentials(
                    token_file="token.json",
                    scopes=["https://www.googleapis.com/auth/gmail.modify"],
                    client_secrets_file=self.gmail_credentials_path,
                )
                api_resource = build_resource_service(credentials=credentials)
            except Exception as e:
                return self._mock_result(action, parameters)
            
            # Execute based on action
            if action == "search":
                return self._search_emails(api_resource, parameters)
            elif action == "send":
                return self._send_email(api_resource, parameters)
            elif action == "get_message":
                return self._get_message(api_resource, parameters)
            elif action == "create_draft":
                return self._create_draft(api_resource, parameters)
            else:
                return f"❌ Hành động không được hỗ trợ: {action}. Các hành động khả dụng: search, send, get_message, create_draft"
            
        except Exception as e:
            logger.error(f"Error in Gmail tool: {e}")
            return f"❌ Lỗi khi thực hiện Gmail action '{action}': {str(e)}"
    
    def _search_emails(self, api_resource, parameters: dict) -> str:
        """Search Gmail emails."""
        try:
            query = parameters.get("query", "")
            max_results = parameters.get("max_results", 10)
            
            if not query:
                return "❌ Thiếu truy vấn tìm kiếm"
            
            gmail_search = GmailSearch(api_resource=api_resource)
            results = gmail_search.run(query)
            
            return f"🔍 Kết quả tìm kiếm Gmail cho '{query}':\n\n{results}"
            
        except Exception as e:
            return f"❌ Lỗi khi tìm kiếm Gmail: {str(e)}"
    
    def _send_email(self, api_resource, parameters: dict) -> str:
        """Send Gmail email."""
        try:
            to = parameters.get("to", "")
            subject = parameters.get("subject", "")
            message = parameters.get("message", "")
            
            if not all([to, subject, message]):
                return "❌ Thiếu thông tin gửi email (to, subject, message)"
            
            gmail_send = GmailSendMessage(api_resource=api_resource)
            email_content = f"To: {to}\nSubject: {subject}\n\n{message}"
            result = gmail_send.run(email_content)
            
            return f"✅ Email đã được gửi thành công!\n\n{result}"
            
        except Exception as e:
            return f"❌ Lỗi khi gửi email: {str(e)}"
    
    def _get_message(self, api_resource, parameters: dict) -> str:
        """Get Gmail message by ID."""
        try:
            message_id = parameters.get("message_id", "")
            
            if not message_id:
                return "❌ Thiếu message_id để lấy email"
            
            gmail_get = GmailGetMessage(api_resource=api_resource)
            result = gmail_get.run(message_id)
            
            return f"📧 Nội dung email {message_id}:\n\n{result}"
            
        except Exception as e:
            return f"❌ Lỗi khi lấy email: {str(e)}"
    
    def _create_draft(self, api_resource, parameters: dict) -> str:
        """Create Gmail draft."""
        try:
            to = parameters.get("to", "")
            subject = parameters.get("subject", "")
            message = parameters.get("message", "")
            
            if not all([to, subject, message]):
                return "❌ Thiếu thông tin tạo draft (to, subject, message)"
            
            gmail_draft = GmailCreateDraft(api_resource=api_resource)
            email_content = f"To: {to}\nSubject: {subject}\n\n{message}"
            result = gmail_draft.run(email_content)
            
            return f"📝 Draft email đã được tạo thành công!\n\n{result}"
            
        except Exception as e:
            return f"❌ Lỗi khi tạo draft: {str(e)}"
    
    def _mock_result(self, action: str, parameters: dict) -> str:
        """Return mock results when Gmail is not configured."""
        if action == "search":
            query = parameters.get("query", "")
            return f"""🔍 Kết quả tìm kiếm Gmail mô phỏng cho '{query}':

📧 **Email 1:**
Từ: example@company.com
Chủ đề: Meeting reminder - {query}
Ngày: 2024-01-15 10:30
Tóm tắt: Nhắc nhở về cuộc họp liên quan đến {query}...

📧 **Email 2:**
Từ: support@service.com
Chủ đề: Update regarding {query}
Ngày: 2024-01-14 15:45
Tóm tắt: Cập nhật thông tin về {query}...

💡 **Lưu ý:** Để sử dụng Gmail thực, cần cấu hình GMAIL_CREDENTIALS_PATH và xác thực OAuth2"""
            
        elif action == "send":
            to = parameters.get("to", "recipient@example.com")
            subject = parameters.get("subject", "Test Subject")
            message = parameters.get("message", "Test Message")
            return f"""✅ Email mô phỏng đã được gửi thành công!

📧 **Chi tiết email:**
Đến: {to}
Chủ đề: {subject}
Nội dung: {message[:100]}{'...' if len(message) > 100 else ''}

💡 **Lưu ý:** Để gửi email thực, cần cấu hình GMAIL_CREDENTIALS_PATH và xác thực OAuth2"""
            
        elif action == "get_message":
            message_id = parameters.get("message_id", "msg_123")
            return f"""📧 Nội dung email mô phỏng {message_id}:

**Từ:** sender@company.com
**Đến:** recipient@company.com
**Chủ đề:** Sample Email Subject
**Ngày:** 2024-01-15 14:30

**Nội dung:**
Đây là nội dung email mẫu. Email này chứa thông tin quan trọng về dự án và cần được xử lý trong thời gian sớm nhất.

**Tệp đính kèm:**
- document.pdf (245 KB)
- image.png (120 KB)

💡 **Lưu ý:** Để lấy email thực, cần cấu hình GMAIL_CREDENTIALS_PATH và xác thực OAuth2"""
            
        elif action == "create_draft":
            to = parameters.get("to", "recipient@example.com")
            subject = parameters.get("subject", "Draft Subject")
            return f"""📝 Draft email mô phỏng đã được tạo thành công!

**Đến:** {to}
**Chủ đề:** {subject}
**Trạng thái:** Draft (Chưa gửi)

💡 **Lưu ý:** Để tạo draft thực, cần cấu hình GMAIL_CREDENTIALS_PATH và xác thực OAuth2"""
        
        else:
            return f"❌ Hành động không được hỗ trợ: {action}"
    
    async def _arun(self, action: str, parameters: dict) -> str:
        """Async version of Gmail tool."""
        return self._run(action, parameters)

# Tool factory function
def create_gmail_tool(gmail_credentials_path: str = None) -> GmailTool:
    """Create a Gmail tool instance with configuration."""
    return GmailTool(gmail_credentials_path=gmail_credentials_path)

# Export the tool
__all__ = ['GmailTool', 'create_gmail_tool'] 