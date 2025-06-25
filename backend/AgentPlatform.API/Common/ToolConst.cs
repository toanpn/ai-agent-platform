using AgentPlatform.API.DTOs;

namespace AgentPlatform.API.Common
{
    public static class ToolConst
    {
        public static List<ToolDto> Tools()
        {
            return
            [
                new ToolDto { Name = "jira_ticket_creator", Description = "Creates a Jira ticket for technical support issues." },
                new ToolDto { Name = "it_knowledge_base_search", Description = "Searches the IT knowledge base for solutions." },
                new ToolDto { Name = "policy_document_search", Description = "Searches for HR policy documents." },
                new ToolDto { Name = "leave_request_tool", Description = "Handles leave requests and procedures." },
                new ToolDto { Name = "google_search", Description = "Performs a Google search for general information." },
                new ToolDto { Name = "check_calendar", Description = "Checks for calendar events and schedules." },
                new ToolDto { Name = "check_weather", Description = "Checks the current weather information." },
                new ToolDto { Name = "adk_search", Description = "Advanced web search using Google ADK." },
                new ToolDto { Name = "adk_http_request", Description = "Makes HTTP requests to external APIs." },
                new ToolDto { Name = "adk_workflow", Description = "Executes multi-agent workflows." }
            ];
        }
    }
}
    