"""
JIRA Tool Module

This module provides JIRA functionality using LangChain's JIRA toolkit.
Based on: https://python.langchain.com/docs/integrations/tools/jira/
"""

import os
import logging
import json
import ast
from typing import Optional, Type, List, Union
from langchain.tools import BaseTool
from pydantic import BaseModel, Field, validator

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
    action: Optional[str] = Field(default=None, description="Hành động JIRA cần thực hiện (ví dụ: 'create_issue', 'search_issues', 'get_issue', 'get_projects')")
    parameters: Union[dict, str, None] = Field(default_factory=dict, description="Tham số cho hành động JIRA, dưới dạng dictionary hoặc JSON string.")

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

class JiraTool(BaseTool):
    """Unified JIRA tool for agents using LangChain's JiraToolkit."""
    
    name: str = "jira"
    description: str = """
    Công cụ JIRA tích hợp cho quản lý issues và projects.
    Sử dụng khi cần:
    - Tạo issues/tickets mới trong JIRA (action: 'create_issue')
    - Tìm kiếm issues bằng JQL (action: 'search_issues')
    - Lấy thông tin chi tiết của một issue (action: 'get_issue')
    - Lấy danh sách các project (action: 'get_projects')
    
    Hướng dẫn sử dụng:
    - Để tạo issue: action="create_issue", parameters={{"summary": "tiêu đề", "description": "mô tả", "project": {{"key": "PROJECT_KEY"}}, "issuetype": {{"name": "Task"}}}}
    - Để tìm kiếm: action="search_issues", parameters={{"jql": "project = KEY AND status = 'Open'"}}
    - Để lấy chi tiết issue: action="get_issue", parameters={{"issue_key": "PROJECT-123"}} (cũng chấp nhận "issue_id")
    - Để lấy danh sách projects: action="get_projects", parameters={{}}
    """
    args_schema: Type[BaseModel] = JiraToolInput
    
    jira_instance_url: Optional[str] = None
    jira_username: Optional[str] = None
    jira_api_token: Optional[str] = None
    jira_cloud: bool = False
    jira_toolkit: Optional[JiraToolkit] = None
    jira_api_wrapper: Optional[JiraAPIWrapper] = None
    initialization_error: Optional[str] = None
    
    def __init__(self, jira_instance_url: str = None, jira_username: str = None, jira_api_token: str = None, **kwargs):
        super().__init__(**kwargs)
        
        self.jira_instance_url = jira_instance_url or os.getenv("JIRA_INSTANCE_URL")
        self.jira_username = jira_username or os.getenv("JIRA_USERNAME")
        self.jira_api_token = jira_api_token or os.getenv("JIRA_API_TOKEN")
        
        # Automatically determine if it's Jira Cloud from the URL
        if self.jira_instance_url and ".atlassian.net" in self.jira_instance_url.lower():
            self.jira_cloud = True
        
        if JIRA_AVAILABLE and all([self.jira_instance_url, self.jira_username, self.jira_api_token]):
            try:
                self.jira_api_wrapper = JiraAPIWrapper(
                    jira_instance_url=self.jira_instance_url,
                    jira_username=self.jira_username,
                    jira_api_token=self.jira_api_token,
                    jira_cloud=self.jira_cloud,
                )
                self.jira_toolkit = JiraToolkit.from_jira_api_wrapper(self.jira_api_wrapper)
            except Exception as e:
                error_message = f"Không thể khởi tạo JIRA toolkit. Vui lòng kiểm tra lại thông tin cấu hình (URL, username, token). Lỗi: {e}"
                logger.error(error_message)
                self.initialization_error = error_message
                self.jira_toolkit = None
                self.jira_api_wrapper = None
        
    def _run(self, action: Optional[str] = None, parameters: Optional[dict] = None) -> str:
        """Execute JIRA action using the unified toolkit."""
        if not action:
            return f"❌ Thiếu tham số 'action'. Các hành động khả dụng:\n{self.description}"

        # Ensure parameters is a dict
        params = parameters or {}
        
        print(f"JIRA_TOOL: Executing action='{action}' with parameters={params}")
        try:
            if not JIRA_AVAILABLE:
                return "❌ JIRA toolkit không khả dụng. Cần cài đặt: pip install langchain-community atlassian-python-api"
            
            # If initialization failed, return the error
            if self.initialization_error:
                return f"❌ {self.initialization_error}"
                
            # Check if toolkit was initialized (no credentials provided) -> use mock
            if not self.jira_toolkit:
                return self._mock_result(action, **params)

            tools = self.jira_toolkit.get_tools()
            
            # Execute based on action
            if action == "create_issue":
                return self._create_issue(tools, params)
            elif action == "search_issues":
                return self._search_issues(tools, params)
            elif action == "get_issue":
                return self._get_issue(tools, params)
            elif action == "get_projects":
                return self._get_projects(tools, params)
            else:
                return f"❌ Hành động không được hỗ trợ: {action}. Các hành động khả dụng: create_issue, search_issues, get_issue, get_projects"
            
        except Exception as e:
            logger.error(f"Error in JIRA tool: {e}")
            print(f"JIRA_TOOL: Error during _run: {e}")
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
        """Search JIRA issues using JQL, with smart query building."""
        if not self.jira_api_wrapper:
            return self._mock_result("search_issues", **parameters)

        try:
            jql = parameters.get("jql")
            if not jql:
                jql_parts = []
                project = parameters.get("project")

                if project:
                    all_projects = self.jira_api_wrapper.get_projects()
                    project_keys = [p["key"].lower() for p in all_projects]
                    if project.lower() not in project_keys:
                        project_list_str = ", ".join(p["key"] for p in all_projects)
                        return f'❌ Project "{project}" không tồn tại. Các project khả dụng: {project_list_str}'
                    jql_parts.append(f'project = "{project}"')

                # Handle natural language query
                query = parameters.get("query") or parameters.get("text") or parameters.get("summary")
                if query:
                    jql_parts.append(f'text ~ "{query.strip()}"')
                
                # Handle other potential fields
                for field in ["status", "component", "assignee", "issuetype"]:
                    if field in parameters:
                        jql_parts.append(f'{field} = "{parameters[field]}"')

                if not jql_parts:
                    return "❌ Thiếu truy vấn JQL hoặc tham số tìm kiếm (ví dụ: 'query', 'project', 'status'). Vui lòng cung cấp thêm thông tin."

                jql = " AND ".join(jql_parts)
            
            # Use limit or a default
            limit = parameters.get("limit", 10)
            
            # Use the underlying client for more control
            search_results = self.jira_api_wrapper.jira.jql(jql, limit=limit)

            # Format the results
            if not search_results or not search_results.get("issues"):
                return f"ℹ️ Không tìm thấy issue nào với truy vấn JQL: '{jql}'"

            issues = search_results["issues"]
            formatted_issues = []
            for issue in issues:
                fields = issue.get("fields", {})
                summary = fields.get("summary", "N/A")
                status = fields.get("status", {}).get("name", "N/A")
                priority = fields.get("priority", {}).get("name", "N/A")
                assignee = fields.get("assignee")
                assignee_name = assignee.get("displayName", "Unassigned") if assignee else "Unassigned"
                issue_str = f'Issue Key: {issue["key"]}, Summary: "{summary}", Status: "{status}", Priority: "{priority}", Assignee: "{assignee_name}"'
                formatted_issues.append(issue_str)
            
            result = "\n".join(formatted_issues)

            return f"🔍 Kết quả tìm kiếm JIRA với JQL '{jql}':\n\n{result}"

        except Exception as e:
            logger.error(f"Error in JIRA search: {e}", exc_info=True)
            return f"❌ Lỗi khi tìm kiếm JIRA: {str(e)}"
    
    def _get_issue(self, tools: List[BaseTool], parameters: dict) -> str:
        """Get JIRA issue details."""
        if not self.jira_api_wrapper:
            return self._mock_result("get_issue", **parameters)

        try:
            issue_key = parameters.get("issue_key") or parameters.get("issue_id")
            if not issue_key:
                return "❌ Thiếu 'issue_key' hoặc 'issue_id' để lấy thông tin issue"

            jql = f'key = "{issue_key.strip()}"'
            search_results = self.jira_api_wrapper.jira.jql(jql, limit=1)

            if not search_results or not search_results.get("issues"):
                return f"❌ Không tìm thấy thông tin cho issue '{issue_key}'. Vui lòng kiểm tra lại mã ticket."

            issue = search_results["issues"][0]
            fields = issue.get("fields", {})

            summary = fields.get("summary", "N/A")
            status = fields.get("status", {}).get("name", "N/A")
            priority = fields.get("priority", {}).get("name", "N/A")
            assignee = fields.get("assignee")
            assignee_name = assignee.get("displayName", "Unassigned") if assignee else "Unassigned"
            reporter = fields.get("reporter")
            reporter_name = reporter.get("displayName", "N/A") if reporter else "N/A"
            description = fields.get("description", "No description available.")
            created = fields.get("created", "N/A")
            updated = fields.get("updated", "N/A")

            # Formatting the output nicely
            details = [
                f"**Summary:** {summary}",
                f"**Status:** {status}",
                f"**Priority:** {priority}",
                f"**Assignee:** {assignee_name}",
                f"**Reporter:** {reporter_name}",
                f"**Created:** {created}",
                f"**Updated:** {updated}",
                "**Description:**",
                str(description) if description else ""
            ]

            result = "\n".join(details)

            return f"🎫 Chi tiết JIRA issue {issue_key}:\n\n{result}"

        except Exception as e:
            logger.error(f"Error in JIRA get_issue: {e}", exc_info=True)
            return f"❌ Lỗi khi lấy JIRA issue '{issue_key}': {str(e)}"
    
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
            result = projects_tool.run(parameters or "")
            return f"📂 Danh sách JIRA projects:\n\n{result}"
            
        except Exception as e:
            return f"❌ Lỗi khi lấy danh sách projects: {str(e)}"
    
    def _mock_result(self, action: str, **parameters: dict) -> str:
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

💡 **Lưu ý:** Để tạo JIRA issue thực, cần cấu hình JIRA_INSTANCE_URL, JIRA_USERNAME, và JIRA_API_TOKEN"""
            
        elif action == "search_issues":
            jql = parameters.get("jql", "")
            if not jql:
                jql_parts = []
                if "project" in parameters:
                    jql_parts.append(f"project = \"{parameters['project']}\"")
                query = parameters.get("query") or parameters.get("text") or parameters.get("summary")
                if query:
                    jql_parts.append(f"text ~ \"{query}\"")
                if "status" in parameters:
                    jql_parts.append(f"status = \"{parameters['status']}\"")
                jql = " AND ".join(jql_parts) if jql_parts else "project = IT"

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

💡 **Lưu ý:** Để tìm kiếm JIRA thực, cần cấu hình JIRA_INSTANCE_URL, JIRA_USERNAME, và JIRA_API_TOKEN"""
            
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

💡 **Lưu ý:** Để lấy JIRA issue thực, cần cấu hình JIRA_INSTANCE_URL, JIRA_USERNAME, và JIRA_API_TOKEN"""
            
        elif action == "get_projects":
            return f"""📂 Danh sách JIRA projects mô phỏng:

**IT** - IT Support Project
**SALES** - Sales Support Project  
**DEV** - Development Project
**QA** - Quality Assurance Project

💡 **Lưu ý:** Để lấy danh sách projects thực, cần cấu hình JIRA_INSTANCE_URL, JIRA_USERNAME, và JIRA_API_TOKEN"""
        
        else:
            return f"❌ Hành động không được hỗ trợ: {action}"
    
    async def _arun(self, action: Optional[str] = None, parameters: Optional[dict] = None) -> str:
        """Async version of the _run method."""
        return self._run(action, parameters)
        
def create_jira_tool(jira_instance_url: str = None, jira_username: str = None, jira_api_token: str = None) -> JiraTool:
    """Create a JIRA tool instance with configuration."""
    return JiraTool(
        jira_instance_url=jira_instance_url,
        jira_username=jira_username,
        jira_api_token=jira_api_token
    )

# Export the tool
__all__ = ['JiraTool', 'create_jira_tool'] 