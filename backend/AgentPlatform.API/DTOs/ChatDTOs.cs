using System.ComponentModel.DataAnnotations;

namespace AgentPlatform.API.DTOs
{
    public class SendMessageRequestDto
    {
        [Required]
        public string Message { get; set; } = string.Empty;
        
        public int? SessionId { get; set; }
        
        public string? AgentName { get; set; }
    }

    public class ChatMessageDto
    {
        public int Id { get; set; }
        public string Content { get; set; } = string.Empty;
        public string Role { get; set; } = string.Empty;
        public string? AgentName { get; set; }
        public DateTime CreatedAt { get; set; }
        public string? Metadata { get; set; }
    }

    public class ChatSessionDto
    {
        public int Id { get; set; }
        public string? Title { get; set; }
        public bool IsActive { get; set; }
        public DateTime CreatedAt { get; set; }
        public DateTime? UpdatedAt { get; set; }
        public List<ChatMessageDto> Messages { get; set; } = new();
    }

    public class ChatResponseDto
    {
        public string Response { get; set; } = string.Empty;
        public string AgentName { get; set; } = string.Empty;
        public int SessionId { get; set; }
        public string? SessionTitle { get; set; }
        public DateTime Timestamp { get; set; }
        public bool Success { get; set; } = true;
        public string? Error { get; set; }
        public string? MasterAgentThinking { get; set; } // Master agent's response when execution steps are available
        
        // Enhanced response fields
        public List<string> AgentsUsed { get; set; } = new();
        public List<string> ToolsUsed { get; set; } = new();
        public AvailableAgentsDto AvailableAgents { get; set; } = new();
        public List<AvailableToolDto> AvailableTools { get; set; } = new();
        public ExecutionDetailsDto ExecutionDetails { get; set; } = new();
        public Dictionary<string, object> Metadata { get; set; } = new();
    }

    public class AvailableAgentsDto
    {
        public int TotalAgents { get; set; }
        public List<AgentInfoDto> Agents { get; set; } = new();
    }

    public class AgentInfoDto
    {
        public string Name { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
    }

    public class AvailableToolDto
    {
        public string Name { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
    }

    public class ExecutionDetailsDto
    {
        public List<ExecutionStepDto> ExecutionSteps { get; set; } = new();
        public int TotalSteps { get; set; }
    }

    public class ExecutionStepDto
    {
        public string ToolName { get; set; } = string.Empty;
        public string ToolInput { get; set; } = string.Empty;
        public string Observation { get; set; } = string.Empty;
    }

    public class EnhancePromptRequestDto
    {
        public string Message { get; set; } = string.Empty;
    }

    public class ChatHistoryDto
    {
        public List<ChatSessionDto> Sessions { get; set; } = new();
        public int TotalCount { get; set; }
        public int Page { get; set; }
        public int PageSize { get; set; }
    }
} 