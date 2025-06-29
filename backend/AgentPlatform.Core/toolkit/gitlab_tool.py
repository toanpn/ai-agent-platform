"""
GitLab Tool Module

This module provides GitLab functionality using LangChain's GitLab toolkit.
Based on: https://python.langchain.com/docs/integrations/tools/gitlab/
"""

import os
import logging
import json
import ast
from typing import Optional, Type, List, Union
from langchain.tools import BaseTool
from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)

# Try to import GitLab toolkit
try:
    from langchain_community.agent_toolkits.gitlab.toolkit import GitLabToolkit
    from langchain_community.utilities.gitlab import GitLabAPIWrapper
    GITLAB_AVAILABLE = True
except ImportError:
    GITLAB_AVAILABLE = False
    logger.warning("GitLab toolkit không khả dụng. Cài đặt với: pip install langchain-community python-gitlab")

class GitLabToolInput(BaseModel):
    """Input schema for GitLab tool."""
    action: Optional[str] = Field(default=None, description="Hành động GitLab cần thực hiện")
    parameters: Union[dict, str, None] = Field(default_factory=dict, description="Tham số cho hành động GitLab")

    @validator("parameters", pre=True)
    def parameters_must_be_dict(cls, v):
        if v is None:
            return {}
        if isinstance(v, str):
            if not v.strip():
                return {}
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                try:
                    parsed_v = ast.literal_eval(v)
                    if isinstance(parsed_v, dict):
                        return parsed_v
                    else:
                        raise ValueError("Evaluated string is not a dictionary")
                except (ValueError, SyntaxError, MemoryError, TypeError) as e:
                    raise ValueError(f"parameters string is not a valid JSON or Python dictionary literal: {e}")
        return v

class GitLabTool(BaseTool):
    """Unified GitLab tool for agents using LangChain's GitLabToolkit."""

    name: str = "gitlab"
    description: str = """
    Công cụ GitLab tích hợp để quản lý repository, issues và merge requests.
    
    Các hành động khả dụng:
    - get_issues: Lấy danh sách tất cả issues
    - get_issue: Lấy chi tiết issue cụ thể (cần issue_number)
    - comment_issue: Bình luận trên issue (cần issue_number và comment)
    - create_merge_request: Tạo merge request (cần title, có thể có description)
    - create_file: Tạo file mới (cần file_path và file_contents)
    - read_file: Đọc nội dung file (cần file_path)
    - update_file: Cập nhật file (cần file_path và file_contents)
    - delete_file: Xóa file (cần file_path)
    
    Ví dụ sử dụng:
    - Lấy issues: action="get_issues"
    - Lấy issue #5: action="get_issue", parameters={"issue_number": 5}
    - Bình luận: action="comment_issue", parameters={"issue_number": 5, "comment": "Fixed!"}
    - Tạo MR: action="create_merge_request", parameters={"title": "Bug fix", "description": "Fix login bug"}
    """
    args_schema: Type[BaseModel] = GitLabToolInput

    gitlab_url: Optional[str] = None
    gitlab_token: Optional[str] = None
    gitlab_repository: Optional[str] = None
    gitlab_branch: Optional[str] = None
    gitlab_base_branch: Optional[str] = None
    gitlab_toolkit: Optional[GitLabToolkit] = None
    initialization_error: Optional[str] = None

    def __init__(self, gitlab_url: str = None, gitlab_personal_access_token: str = None, 
                 gitlab_repository: str = None, gitlab_branch: str = None, 
                 gitlab_base_branch: str = None, **kwargs):
        super().__init__(**kwargs)

        self.gitlab_url = gitlab_url or os.getenv("GITLAB_URL") or "https://gitlab.com"
        self.gitlab_token = gitlab_personal_access_token or os.getenv("GITLAB_PERSONAL_ACCESS_TOKEN")
        self.gitlab_repository = gitlab_repository or os.getenv("GITLAB_REPOSITORY")
        self.gitlab_branch = gitlab_branch or os.getenv("GITLAB_BRANCH") or "main"
        self.gitlab_base_branch = gitlab_base_branch or os.getenv("GITLAB_BASE_BRANCH") or "main"

        if GITLAB_AVAILABLE and all([self.gitlab_url, self.gitlab_token, self.gitlab_repository]):
            try:
                os.environ["GITLAB_URL"] = self.gitlab_url
                os.environ["GITLAB_PERSONAL_ACCESS_TOKEN"] = self.gitlab_token
                os.environ["GITLAB_REPOSITORY"] = self.gitlab_repository
                os.environ["GITLAB_BRANCH"] = self.gitlab_branch
                os.environ["GITLAB_BASE_BRANCH"] = self.gitlab_base_branch
                
                gitlab_api = GitLabAPIWrapper()
                self.gitlab_toolkit = GitLabToolkit.from_gitlab_api_wrapper(gitlab_api)
            except Exception as e:
                error_message = f"Không thể khởi tạo GitLab toolkit: {e}"
                logger.error(error_message)
                self.initialization_error = error_message
                self.gitlab_toolkit = None

    def _run(self, action: Optional[str] = None, parameters: Optional[dict] = None) -> str:
        """Execute GitLab action using the unified toolkit."""
        
        # List of supported actions
        supported_actions = [
            "get_issues", "get_issue", "comment_issue", "create_merge_request",
            "create_file", "read_file", "update_file", "delete_file"
        ]
        
        if not action:
            actions_list = "\n".join([f"  - {act}" for act in supported_actions])
            return f"""❌ Thiếu tham số 'action'. Các hành động khả dụng:

{actions_list}

Ví dụ: 
- action="get_issues" 
- action="get_issue", parameters={{"issue_number": 1}}
- action="comment_issue", parameters={{"issue_number": 1, "comment": "test"}}"""

        params = parameters or {}

        try:
            if not GITLAB_AVAILABLE:
                return "❌ GitLab toolkit không khả dụng. Cần cài đặt: pip install langchain-community python-gitlab"

            if self.initialization_error:
                return f"❌ {self.initialization_error}"

            # Validate action
            if action not in supported_actions:
                actions_list = ", ".join(supported_actions)
                return f"❌ Hành động '{action}' không được hỗ trợ. Các hành động khả dụng: {actions_list}"

            if not self.gitlab_toolkit:
                return self._mock_result(action, **params)

            tools = self.gitlab_toolkit.get_tools()

            # Execute action using action mapping
            action_map = {
                "get_issues": self._get_issues,
                "get_issue": self._get_issue,
                "comment_issue": self._comment_issue,
                "create_merge_request": self._create_merge_request,
                "create_file": self._create_file,
                "read_file": self._read_file,
                "update_file": self._update_file,
                "delete_file": self._delete_file
            }
            
            return action_map[action](tools, params)

        except Exception as e:
            logger.error(f"Error in GitLab tool: {e}")
            return f"❌ Lỗi khi thực hiện GitLab action '{action}': {str(e)}"

    def _find_tool(self, tools: List[BaseTool], tool_name: str) -> Optional[BaseTool]:
        """Find a tool by name (case-insensitive)."""
        for tool in tools:
            if tool.name.lower() == tool_name.lower():
                return tool
        return None

    def _get_issues(self, tools: List[BaseTool], parameters: dict) -> str:
        """Get issues from the repository."""
        get_issues_tool = self._find_tool(tools, "Get Issues")
        if not get_issues_tool:
            return "❌ Không tìm thấy công cụ lấy danh sách issues"

        try:
            result = get_issues_tool.run({})
            return f"📋 Danh sách Issues:\n\n{result}"
        except Exception as e:
            return f"❌ Lỗi khi lấy danh sách issues: {str(e)}"

    def _get_issue(self, tools: List[BaseTool], parameters: dict) -> str:
        """Get details of a specific issue."""
        get_issue_tool = self._find_tool(tools, "Get Issue")
        if not get_issue_tool:
            return "❌ Không tìm thấy công cụ lấy chi tiết issue"

        try:
            issue_number = parameters.get("issue_number")
            if not issue_number:
                return "❌ Thiếu 'issue_number'"

            result = get_issue_tool.run({"issue_number": issue_number})
            return f"📄 Chi tiết Issue #{issue_number}:\n\n{result}"
        except Exception as e:
            return f"❌ Lỗi khi lấy chi tiết issue: {str(e)}"

    def _comment_issue(self, tools: List[BaseTool], parameters: dict) -> str:
        """Comment on a specific issue."""
        comment_tool = self._find_tool(tools, "Comment on Issue")
        if not comment_tool:
            return "❌ Không tìm thấy công cụ bình luận issue"

        try:
            issue_number = parameters.get("issue_number")
            comment = parameters.get("comment")
            
            if not issue_number or not comment:
                return "❌ Thiếu 'issue_number' hoặc 'comment'"

            result = comment_tool.run({"issue_number": issue_number, "comment": comment})
            return f"💬 Đã bình luận trên Issue #{issue_number}:\n\n{result}"
        except Exception as e:
            return f"❌ Lỗi khi bình luận issue: {str(e)}"

    def _create_merge_request(self, tools: List[BaseTool], parameters: dict) -> str:
        """Create a merge request."""
        mr_tool = self._find_tool(tools, "Create Merge Request")
        if not mr_tool:
            return "❌ Không tìm thấy công cụ tạo merge request"

        try:
            title = parameters.get("title")
            description = parameters.get("description", "")
            
            if not title:
                return "❌ Thiếu 'title'"

            tool_input = {"title": title, "description": description}
            result = mr_tool.run(tool_input)
            return f"🔀 Đã tạo Merge Request:\n\n{result}"
        except Exception as e:
            return f"❌ Lỗi khi tạo merge request: {str(e)}"

    def _create_file(self, tools: List[BaseTool], parameters: dict) -> str:
        """Create a new file in the repository."""
        create_tool = self._find_tool(tools, "Create File")
        if not create_tool:
            return "❌ Không tìm thấy công cụ tạo file"

        try:
            file_path = parameters.get("file_path")
            file_contents = parameters.get("file_contents")
            
            if not file_path or file_contents is None:
                return "❌ Thiếu 'file_path' hoặc 'file_contents'"

            tool_input = {"file_path": file_path, "file_contents": file_contents}
            result = create_tool.run(tool_input)
            return f"📝 Đã tạo file '{file_path}':\n\n{result}"
        except Exception as e:
            return f"❌ Lỗi khi tạo file: {str(e)}"

    def _read_file(self, tools: List[BaseTool], parameters: dict) -> str:
        """Read file content from the repository."""
        read_tool = self._find_tool(tools, "Read File")
        if not read_tool:
            return "❌ Không tìm thấy công cụ đọc file"

        try:
            file_path = parameters.get("file_path")
            if not file_path:
                return "❌ Thiếu 'file_path'"

            result = read_tool.run({"file_path": file_path})
            return f"📖 Nội dung file '{file_path}':\n\n{result}"
        except Exception as e:
            return f"❌ Lỗi khi đọc file: {str(e)}"

    def _update_file(self, tools: List[BaseTool], parameters: dict) -> str:
        """Update an existing file in the repository."""
        update_tool = self._find_tool(tools, "Update File")
        if not update_tool:
            return "❌ Không tìm thấy công cụ cập nhật file"

        try:
            file_path = parameters.get("file_path")
            file_contents = parameters.get("file_contents")
            
            if not file_path or file_contents is None:
                return "❌ Thiếu 'file_path' hoặc 'file_contents'"

            tool_input = {"file_path": file_path, "file_contents": file_contents}
            result = update_tool.run(tool_input)
            return f"✏️ Đã cập nhật file '{file_path}':\n\n{result}"
        except Exception as e:
            return f"❌ Lỗi khi cập nhật file: {str(e)}"

    def _delete_file(self, tools: List[BaseTool], parameters: dict) -> str:
        """Delete a file from the repository."""
        delete_tool = self._find_tool(tools, "Delete File")
        if not delete_tool:
            return "❌ Không tìm thấy công cụ xóa file"

        try:
            file_path = parameters.get("file_path")
            if not file_path:
                return "❌ Thiếu 'file_path'"

            result = delete_tool.run({"file_path": file_path})
            return f"🗑️ Đã xóa file '{file_path}':\n\n{result}"
        except Exception as e:
            return f"❌ Lỗi khi xóa file: {str(e)}"

    def _mock_result(self, action: str, **parameters: dict) -> str:
        """Return mock results when GitLab is not configured."""
        if action == "get_issues":
            return """📋 Danh sách Issues mô phỏng:

🔴 **Issue #1** - Bug trong tính năng login
   📅 Ngày tạo: 2024-01-15
   👤 Tác giả: developer1
   🏷️ Labels: bug, urgent
   📝 Trạng thái: Open

🟡 **Issue #2** - Cập nhật documentation cho API
   📅 Ngày tạo: 2024-01-14
   👤 Tác giả: writer1
   🏷️ Labels: documentation, enhancement
   📝 Trạng thái: Open

🟢 **Issue #3** - Thêm unit tests cho module auth
   📅 Ngày tạo: 2024-01-13
   👤 Tác giả: tester1
   🏷️ Labels: testing, improvement
   📝 Trạng thái: Closed

💡 **Lưu ý:** Đây là dữ liệu mô phỏng. Để lấy issues thực từ GitLab, cần cấu hình credentials."""

        elif action == "get_issue":
            issue_number = parameters.get('issue_number', 1)
            return f"""📄 Chi tiết Issue #{issue_number}:

**🏷️ Tiêu đề:** Bug trong tính năng login
**📝 Trạng thái:** Open
**👤 Tác giả:** developer1
**📅 Ngày tạo:** 2024-01-15 10:30:00
**🔖 Labels:** bug, urgent, frontend
**👥 Assignees:** developer2, qa-team

**📋 Mô tả:**
Khi người dùng nhập sai mật khẩu 3 lần liên tiếp, hệ thống không hiển thị thông báo lỗi rõ ràng. 
Thay vào đó, trang web bị treo và người dùng không biết phải làm gì tiếp theo.

**💬 Bình luận gần đây:**
- developer2 (2024-01-16): "Đang điều tra vấn đề này, có thể liên quan đến rate limiting"
- qa-team (2024-01-16): "Đã reproduce được bug, xảy ra trên cả Chrome và Firefox"

💡 **Lưu ý:** Đây là dữ liệu mô phỏng. Để lấy issue thực từ GitLab, cần cấu hình credentials."""

        elif action == "comment_issue":
            issue_number = parameters.get('issue_number', 1)
            comment = parameters.get('comment', 'Test comment')
            return f"""💬 Đã thêm bình luận mô phỏng trên Issue #{issue_number}:

**📝 Nội dung:** {comment}
**👤 Tác giả:** gitlab-bot
**⏰ Thời gian:** 2024-01-17 14:25:00
**🔗 Link:** https://gitlab.com/username/repository/-/issues/{issue_number}#note_123456

💡 **Lưu ý:** Đây là mô phỏng. Để bình luận thực trên GitLab, cần cấu hình credentials."""

        elif action == "create_merge_request":
            title = parameters.get('title', 'Fix login bug')
            description = parameters.get('description', 'Sửa lỗi đăng nhập cho người dùng')
            return f"""🔀 Đã tạo Merge Request mô phỏng:

**🏷️ Tiêu đề:** {title}
**📋 Mô tả:** {description}
**🌿 Source Branch:** feature/fix-login-bug
**🎯 Target Branch:** main
**📝 Trạng thái:** Open
**🔗 MR #15:** https://gitlab.com/username/repository/-/merge_requests/15
**👤 Tác giả:** gitlab-bot
**📅 Ngày tạo:** 2024-01-17 14:30:00

**📊 Thống kê:**
- ✅ 3 files changed
- ➕ 25 additions
- ➖ 8 deletions

💡 **Lưu ý:** Đây là mô phỏng. Để tạo MR thực trên GitLab, cần cấu hình credentials."""

        elif action == "create_file":
            file_path = parameters.get('file_path', 'test.txt')
            file_contents = parameters.get('file_contents', 'Test content')
            return f"""📝 Đã tạo file mô phỏng:

**📁 Đường dẫn:** {file_path}
**📄 Nội dung:**
```
{file_contents}
```
**🌿 Branch:** feature/add-new-file
**💾 Commit:** "Add {file_path} with initial content"
**🔗 Link:** https://gitlab.com/username/repository/-/blob/main/{file_path}

💡 **Lưu ý:** Đây là mô phỏng. Để tạo file thực trên GitLab, cần cấu hình credentials."""

        elif action == "read_file":
            file_path = parameters.get('file_path', 'README.md')
            return f"""📖 Nội dung file mô phỏng '{file_path}':

```markdown
# 🚀 Project Title

Đây là một dự án mẫu sử dụng GitLab CI/CD.

## 📋 Tính năng chính

- ✅ Authentication system
- ✅ User management
- ✅ API endpoints
- 🔄 Real-time notifications

## 🔧 Cài đặt

1. Clone repository
2. Install dependencies: `npm install`
3. Start development server: `npm run dev`

## 🤝 Đóng góp

Vui lòng tạo issue hoặc merge request để đóng góp.
```

**📊 Thông tin file:**
- 📏 Kích thước: 1.2 KB
- 📅 Cập nhật lần cuối: 2024-01-16 09:15:00
- 👤 Tác giả: developer1

💡 **Lưu ý:** Đây là nội dung mô phỏng. Để đọc file thực từ GitLab, cần cấu hình credentials."""

        elif action == "update_file":
            file_path = parameters.get('file_path', 'README.md')
            file_contents = parameters.get('file_contents', 'Updated content')
            return f"""✏️ Đã cập nhật file mô phỏng:

**📁 Đường dẫn:** {file_path}
**📄 Nội dung mới:**
```
{file_contents}
```
**🌿 Branch:** feature/update-readme
**💾 Commit:** "Update {file_path} with new information"
**🔗 Link:** https://gitlab.com/username/repository/-/blob/main/{file_path}
**📅 Thời gian:** 2024-01-17 14:35:00

💡 **Lưu ý:** Đây là mô phỏng. Để cập nhật file thực trên GitLab, cần cấu hình credentials."""

        elif action == "delete_file":
            file_path = parameters.get('file_path', 'old_file.txt')
            return f"""🗑️ Đã xóa file mô phỏng:

**📁 Đường dẫn đã xóa:** {file_path}
**🌿 Branch:** feature/cleanup-old-files
**💾 Commit:** "Remove obsolete file {file_path}"
**📅 Thời gian:** 2024-01-17 14:40:00
**🔗 Commit Link:** https://gitlab.com/username/repository/-/commit/abc123def456

⚠️ **Lưu ý:** File đã được xóa khỏi repository và không thể khôi phục.

💡 **Lưu ý:** Đây là mô phỏng. Để xóa file thực trên GitLab, cần cấu hình credentials."""

        else:
            supported_actions = ["get_issues", "get_issue", "comment_issue", "create_merge_request", "create_file", "read_file", "update_file", "delete_file"]
            return f"❌ Hành động '{action}' không được hỗ trợ. Các hành động khả dụng: {', '.join(supported_actions)}"

    async def _arun(self, action: Optional[str] = None, parameters: Optional[dict] = None) -> str:
        """Async version of the _run method."""
        return self._run(action, parameters)

def create_gitlab_tool(gitlab_url: str = None, gitlab_personal_access_token: str = None,
                      gitlab_repository: str = None, gitlab_branch: str = None,
                      gitlab_base_branch: str = None) -> GitLabTool:
    """Create a GitLab tool instance with configuration."""
    return GitLabTool(
        gitlab_url=gitlab_url,
        gitlab_personal_access_token=gitlab_personal_access_token,
        gitlab_repository=gitlab_repository,
        gitlab_branch=gitlab_branch,
        gitlab_base_branch=gitlab_base_branch
    )

# Export the tool
__all__ = ['GitLabTool', 'create_gitlab_tool'] 