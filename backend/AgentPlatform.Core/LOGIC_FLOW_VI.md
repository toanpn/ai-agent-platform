# Luồng Hoạt Động và Kiến Trúc Hệ Thống Agent

Tài liệu này giải thích chi tiết về kiến trúc và luồng hoạt động của hệ thống agent trong dự án `AgentPlatform.Core`. Hệ thống được xây dựng theo một kiến trúc phân cấp, cho phép quản lý và điều phối các agent chuyên biệt một cách hiệu quả và linh hoạt.

## 1. Tổng Quan Kiến Trúc

Hệ thống được thiết kế theo mô hình phân cấp gồm 3 lớp chính:

1.  **Master Agent (Agent Điều Phối)**: Đóng vai trò là "bộ não" trung tâm, nhận tất cả yêu cầu từ người dùng và quyết định agent chuyên biệt nào sẽ xử lý.
2.  **Sub-Agents (Agent Chuyên Biệt)**: Mỗi agent được thiết kế để thực hiện một nhóm nhiệm vụ cụ thể (ví dụ: quản lý Jira, tìm kiếm thông tin, RAG). Chúng hoạt động như những chuyên gia trong lĩnh vực của mình.
3.  **Tools (Công Cụ)**: Là các hàm hoặc lớp thực thi những hành động cụ thể, như gọi API của một dịch vụ bên ngoài (Google Search, Gmail) hoặc truy vấn cơ sở dữ liệu.

Kiến trúc này mang lại sự linh hoạt cao, cho phép dễ dàng mở rộng hệ thống bằng cách thêm các file cấu hình JSON cho agent và tool mới mà không cần can thiệp sâu vào mã nguồn.

## 2. Các Thành Phần Chính

Dưới đây là mô tả vai trò của các module quan trọng trong hệ thống:

### `api_server.py` (Lớp API)

-   **Vai trò**: Là cổng giao tiếp chính của hệ thống thông qua REST API.
-   **Endpoint chính**: `/api/chat` nhận các yêu cầu trò chuyện từ người dùng.
-   **Luồng hoạt động**: Khi nhận một yêu cầu, nó sẽ chuyển tiếp đến `AgentSystemManager` để xử lý.

### `AgentSystemManager` (Trong `api_server.py`)

-   **Vai trò**: Quản lý vòng đời và trạng thái của toàn bộ hệ thống agent.
-   **Luồng hoạt động**: Chịu trách nhiệm khởi tạo `MasterAgent` và các `Sub-Agent` khi hệ thống khởi động. Nó đóng vai trò trung gian, nhận yêu cầu từ lớp API và điều phối đến `MasterAgent`.

### `master_agent.py` (Master Agent)

-   **Vai trò**: Là agent điều phối thông minh.
-   **Luồng hoạt động**:
    1.  Sử dụng một Mô hình Ngôn ngữ Lớn (LLM) để phân tích và hiểu sâu yêu cầu của người dùng.
    2.  Dựa trên mô tả chức năng của các `Sub-Agent` có sẵn, nó sẽ chọn ra agent phù hợp nhất để giải quyết yêu cầu.
    3.  Nó coi mỗi `Sub-Agent` như một "công cụ" (Tool) và gọi agent đó để thực thi nhiệm vụ.

### `agent_manager.py` (Agent Manager)

-   **Vai trò**: Chịu trách nhiệm tạo và quản lý các `Sub-Agent`.
-   **Luồng hoạt động**:
    1.  Đọc file cấu hình `agents.json` để lấy thông tin về các `Sub-Agent` cần tạo.
    2.  Đối với mỗi agent, nó sẽ tạo một `AgentExecutor` của LangChain, trang bị cho agent đó LLM, prompt (kịch bản), và một bộ công cụ riêng.
    3.  Các công cụ này được tạo ra bởi `DynamicToolManager`.
    4.  Cuối cùng, nó "gói" mỗi `Sub-Agent` đã được tạo thành một đối tượng `BaseTool` để `MasterAgent` có thể sử dụng.

### `dynamic_tool_manager.py` (Dynamic Tool Manager)

-   **Vai trò**: Tạo và cấu hình các công cụ (tools) một cách linh hoạt.
-   **Luồng hoạt động**:
    1.  Đọc file `toolkit/tools.json` để biết danh sách các công cụ có sẵn.
    2.  Khi một `Sub-Agent` cần một công cụ, manager này sẽ tạo một instance của công cụ đó và truyền vào các cấu hình riêng của agent (ví dụ: API keys, credentials).
    3.  Nó tự động tạo ra một schema (lược đồ) đầu vào cho mỗi công cụ, giúp LLM hiểu rõ cần những tham số nào để gọi công cụ đó.

### `toolkit/` (Thư Mục Công Cụ)

-   **Vai trò**: Chứa mã nguồn thực thi logic của từng công cụ.
-   **Luồng hoạt động**: Các file Python trong thư mục này định nghĩa các hàm hoặc lớp để tương tác với dịch vụ bên ngoài như Jira, Google, Gmail, hoặc các hệ thống nội bộ khác.

## 3. Luồng Xử Lý Yêu Cầu (`/api/chat`)

Đây là luồng xử lý chi tiết khi người dùng gửi một tin nhắn:

1.  **Request**: Người dùng gửi yêu cầu `POST` đến endpoint `/api/chat`.
2.  **API Server**: `api_server.py` nhận yêu cầu và chuyển cho `AgentSystemManager`.
3.  **System Manager**: `AgentSystemManager` chuyển tiếp yêu cầu đến `MasterAgent.process_request_with_details()`.
4.  **Master Agent**: `MasterAgent` phân tích yêu cầu và sử dụng LLM để chọn `Sub-Agent` phù hợp nhất.
5.  **Sub-Agent Execution**: `AgentExecutor` của `Sub-Agent` được chọn sẽ được kích hoạt. Agent này tiếp tục phân tích yêu cầu và chọn công cụ (tool) phù hợp nhất từ bộ công cụ của mình.
6.  **Tool Execution**: `DynamicToolManager` tạo một instance của công cụ được chọn với cấu hình cần thiết. Công cụ được thực thi (ví dụ: gọi API Google Search).
7.  **Response**: Kết quả từ công cụ được trả về cho `Sub-Agent`, sau đó được tổng hợp và trả về cho `MasterAgent`, và cuối cùng được gửi lại cho người dùng thông qua API response.

## 4. Cấu Hình

Hệ thống được điều khiển chủ yếu qua hai file JSON:

-   **`agents.json`**: Định nghĩa các `Sub-Agent`. Mỗi object trong file này mô tả tên, chức năng (description), và danh sách các `tool_id` mà agent đó có quyền sử dụng.
-   **`toolkit/tools.json`**: Là một "registry" (sổ đăng ký) cho tất cả các công cụ. Nó định nghĩa `id`, tên, mô tả, các tham số đầu vào, và file Python chứa logic thực thi của mỗi công cụ.

## Kết Luận

Kiến trúc phân cấp này tạo ra một hệ thống agent mạnh mẽ, có tổ chức và dễ dàng mở rộng. Việc tách biệt giữa logic (code) và cấu hình (JSON) cho phép các nhà phát triển và quản trị viên có thể thay đổi hoặc thêm mới các chức năng của hệ thống một cách nhanh chóng mà không cần sửa đổi code lõi. 