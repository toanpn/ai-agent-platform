"""
JIRA Tool Module

This module provides JIRA functionality using LangChain's JIRA toolkit.
Based on: https://python.langchain.com/docs/integrations/tools/jira/
"""

import os
import logging
from typing import Optional, Type, List
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Try to import JIRA toolkit
try:
    from langchain_community.agent_toolkits.jira.toolkit import JiraToolkit
    from langchain_community.utilities.jira import JiraAPIWrapper
    JIRA_AVAILABLE = True
except ImportError:
    JIRA_AVAILABLE = False
    logger.warning("JIRA toolkit không khả dụng. Cài đặt với: pip install langchain-community atlassian-python-api")

class JiraToolInput(BaseModel):
    """Input schema for JIRA tool."""
    action: str = Field(description="Hành động JIRA cần thực hiện (create_issue, search_issues, get_issue)")
    parameters: dict = Field(description="Tham số cho hành động JIRA")

class JiraTool(BaseTool):
    """Unified JIRA tool for agents using LangChain's JiraToolkit."""
    
    name: str = "jira"
    description: str = """
    Công cụ JIRA tích hợp cho quản lý issues và projects.
    Sử dụng khi cần:
    - Tạo issues/tickets mới trong JIRA
    - Tìm kiếm issues bằng JQL (JIRA Query Language)
    - Lấy thông tin chi tiết của issues
    - Lấy danh sách projects
    - Thực hiện các thao tác JIRA khác
    
    Hướng dẫn sử dụng:
    - Để tạo issue: action="create_issue", parameters={"summary": "tiêu đề", "description": "mô tả", "project": {"key": "PROJECT_KEY"}, "issuetype": {"name": "Task"}}
    - Để tìm kiếm: action="search_issues", parameters={"jql": "project = KEY AND status = 'Open'"}
    - Để lấy chi tiết issue: action="get_issue", parameters={"issue_key": "PROJECT-123"}
    """
    args_schema: Type[BaseModel] = JiraToolInput
    
    def __init__(self, jira_base_url: str = None, jira_username: str = None, jira_api_token: str = None, **kwargs):
        super().__init__(**kwargs)
        self.jira_base_url = jira_base_url or os.getenv("JIRA_BASE_URL")
        self.jira_username = jira_username or os.getenv("JIRA_USERNAME")
        self.jira_api_token = jira_api_token or os.getenv("JIRA_API_TOKEN")
        
    def _run(self, action: str, parameters: dict) -> str:
        """Execute JIRA action using the unified toolkit."""
        try:
            if not JIRA_AVAILABLE:
                return "❌ JIRA toolkit không khả dụng. Cần cài đặt: pip install langchain-community atlassian-python-api"
            
            # Check for JIRA configuration
            if not all([self.jira_base_url, self.jira_username, self.jira_api_token]):
                return self._mock_result(action, parameters)
            
            # Initialize JIRA API wrapper
            jira = JiraAPIWrapper(
                jira_base_url=self.jira_base_url,
                jira_username=self.jira_username,
                jira_api_token=self.jira_api_token,
            )
            
            # Create JIRA toolkit
            toolkit = JiraToolkit.from_jira_api_wrapper(jira)
            tools = toolkit.get_tools()
            
            # Execute based on action
            if action == "create_issue":
                return self._create_issue(tools, parameters)
            elif action == "search_issues":
                return self._search_issues(tools, parameters)
            elif action == "get_issue":
                return self._get_issue(tools, parameters)
            elif action == "get_projects":
                return self._get_projects(tools, parameters)
            else:
                return f"❌ Hành động không được hỗ trợ: {action}. Các hành động khả dụng: create_issue, search_issues, get_issue, get_projects"
            
        except Exception as e:
            logger.error(f"Error in JIRA tool: {e}")
            return f"❌ Lỗi khi thực hiện JIRA action '{action}': {str(e)}"
    
    def _create_issue(self, tools: List[BaseTool], parameters: dict) -> str:
        """Create a new JIRA issue."""
        create_tool = None
        for tool in tools:
            if tool.name == "Create Issue":
                create_tool = tool
                break
        
        if not create_tool:
            return "❌ Không tìm thấy công cụ tạo issue"
        
        try:
            # Ensure required fields are present
            if "summary" not in parameters:
                return "❌ Thiếu trường 'summary' để tạo issue"
            
            # Set default values if not provided
            if "project" not in parameters:
                parameters["project"] = {"key": "IT"}
            if "issuetype" not in parameters:
                parameters["issuetype"] = {"name": "Task"}
            if "priority" not in parameters:
                parameters["priority"] = {"name": "Medium"}
            
            result = create_tool.run(parameters)
            return f"✅ JIRA issue đã được tạo thành công!\n\n{result}"
            
        except Exception as e:
            return f"❌ Lỗi khi tạo JIRA issue: {str(e)}"
    
    def _search_issues(self, tools: List[BaseTool], parameters: dict) -> str:
        """Search JIRA issues using JQL."""
        search_tool = None
        for tool in tools:
            if tool.name == "JQL Query":
                search_tool = tool
                break
        
        if not search_tool:
            return "❌ Không tìm thấy công cụ tìm kiếm"
        
        try:
            jql = parameters.get("jql", "")
            if not jql:
                return "❌ Thiếu truy vấn JQL để tìm kiếm"
            
            result = search_tool.run(jql)
            return f"🔍 Kết quả tìm kiếm JIRA với JQL '{jql}':\n\n{result}"
            
        except Exception as e:
            return f"❌ Lỗi khi tìm kiếm JIRA: {str(e)}"
    
    def _get_issue(self, tools: List[BaseTool], parameters: dict) -> str:
        """Get JIRA issue details."""
        # Use the generic API call tool for getting issue details
        api_tool = None
        for tool in tools:
            if tool.name == "Catch all Jira API call":
                api_tool = tool
                break
        
        if not api_tool:
            return "❌ Không tìm thấy công cụ API"
        
        try:
            issue_key = parameters.get("issue_key", "")
            if not issue_key:
                return "❌ Thiếu issue_key để lấy thông tin issue"
            
            api_params = {
                "function": "issue",
                "args": [issue_key]
            }
            result = api_tool.run(api_params)
            return f"🎫 Chi tiết JIRA issue {issue_key}:\n\n{result}"
            
        except Exception as e:
            return f"❌ Lỗi khi lấy JIRA issue: {str(e)}"
    
    def _get_projects(self, tools: List[BaseTool], parameters: dict) -> str:
        """Get all JIRA projects."""
        projects_tool = None
        for tool in tools:
            if tool.name == "Get Projects":
                projects_tool = tool
                break
        
        if not projects_tool:
            return "❌ Không tìm thấy công cụ lấy projects"
        
        try:
            result = projects_tool.run("")
            return f"📂 Danh sách JIRA projects:\n\n{result}"
            
        except Exception as e:
            return f"❌ Lỗi khi lấy danh sách projects: {str(e)}"
    
    def _mock_result(self, action: str, parameters: dict) -> str:
        """Return mock results when JIRA is not configured."""
        if action == "create_issue":
            summary = parameters.get("summary", "Test Issue")
            project_key = parameters.get("project", {}).get("key", "IT")
            issue_key = f"{project_key}-{hash(summary) % 9999 + 1000}"
            
            return f"""✅ JIRA issue mô phỏng đã được tạo thành công!

🎫 **Chi tiết issue:**
Issue Key: {issue_key}
Dự án: {project_key}
Tóm tắt: {summary}
Mô tả: {parameters.get('description', 'Không có mô tả')}
Loại: {parameters.get('issuetype', {}).get('name', 'Task')}
Ưu tiên: {parameters.get('priority', {}).get('name', 'Medium')}

💡 **Lưu ý:** Để tạo JIRA issue thực, cần cấu hình JIRA_BASE_URL, JIRA_USERNAME, và JIRA_API_TOKEN"""
            
        elif action == "search_issues":
            jql = parameters.get("jql", "")
            return f"""🔍 Kết quả tìm kiếm JIRA mô phỏng với JQL '{jql}':

🎫 **Issue 1: IT-1234**
Tóm tắt: Sample bug report
Trạng thái: In Progress
Người được giao: john.doe@company.com
Ưu tiên: High

🎫 **Issue 2: IT-1235**
Tóm tắt: Feature request for new functionality
Trạng thái: To Do
Người được giao: jane.smith@company.com
Ưu tiên: Medium

🎫 **Issue 3: IT-1236**
Tóm tắt: System maintenance task
Trạng thái: Done
Người được giao: admin@company.com
Ưu tiên: Low

💡 **Lưu ý:** Để tìm kiếm JIRA thực, cần cấu hình JIRA_BASE_URL, JIRA_USERNAME, và JIRA_API_TOKEN"""
            
        elif action == "get_issue":
            issue_key = parameters.get("issue_key", "IT-123")
            return f"""🎫 Chi tiết JIRA issue mô phỏng {issue_key}:

**Tóm tắt:** Sample Issue for Testing
**Trạng thái:** In Progress
**Loại:** Task
**Ưu tiên:** Medium
**Người được giao:** developer@company.com
**Người báo cáo:** manager@company.com
**Ngày tạo:** 2024-01-15 09:00
**Ngày cập nhật:** 2024-01-16 14:30

**Mô tả:**
Đây là mô tả chi tiết của issue mẫu. Issue này bao gồm các yêu cầu cụ thể và cần được hoàn thành trong thời gian quy định.

💡 **Lưu ý:** Để lấy JIRA issue thực, cần cấu hình JIRA_BASE_URL, JIRA_USERNAME, và JIRA_API_TOKEN"""
            
        elif action == "get_projects":
            return f"""📂 Danh sách JIRA projects mô phỏng:

**IT** - IT Support Project
**SALES** - Sales Support Project  
**DEV** - Development Project
**QA** - Quality Assurance Project

💡 **Lưu ý:** Để lấy danh sách projects thực, cần cấu hình JIRA_BASE_URL, JIRA_USERNAME, và JIRA_API_TOKEN"""
        
        else:
            return f"❌ Hành động không được hỗ trợ: {action}"
    
    async def _arun(self, action: str, parameters: dict) -> str:
        """Async version of JIRA tool."""
        return self._run(action, parameters)

# Tool factory function
def create_jira_tool(jira_base_url: str = None, jira_username: str = None, jira_api_token: str = None) -> JiraTool:
    """Create a JIRA tool instance with configuration."""
    return JiraTool(
        jira_base_url=jira_base_url,
        jira_username=jira_username,
        jira_api_token=jira_api_token
    )

# Export the tool
__all__ = ['JiraTool', 'create_jira_tool'] 