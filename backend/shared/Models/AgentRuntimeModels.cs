namespace AgentPlatform.Shared.Models
{
    public class AgentRuntimeRequest
    {
        public string Message { get; set; } = string.Empty;
        public string UserId { get; set; } = string.Empty;
        public string? SessionId { get; set; }
        public string? AgentName { get; set; }
        public List<MessageHistory> History { get; set; } = new();
        public Dictionary<string, object> Context { get; set; } = new();
    }

    public class AgentRuntimeResponse
    {
        public string Response { get; set; } = string.Empty;
        public string AgentName { get; set; } = string.Empty;
        public string? SessionId { get; set; }
        public bool Success { get; set; } = true;
        public string? Error { get; set; }
        public Dictionary<string, object> Metadata { get; set; } = new();
        
        // Enhanced response fields
        public List<string> AgentsUsed { get; set; } = new();
        public List<string> ToolsUsed { get; set; } = new();
        public AvailableAgents AvailableAgents { get; set; } = new();
        public List<AvailableTool> AvailableTools { get; set; } = new();
        public ExecutionDetails ExecutionDetails { get; set; } = new();
    }

    public class AvailableAgents
    {
        public int TotalAgents { get; set; }
        public List<AgentInfo> Agents { get; set; } = new();
    }

    public class AgentInfo
    {
        public string Name { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
    }

    public class AvailableTool
    {
        public string Name { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
    }

    public class ExecutionDetails
    {
        public List<ExecutionStep> ExecutionSteps { get; set; } = new();
        public int TotalSteps { get; set; }
    }

    public class ExecutionStep
    {
        public string ToolName { get; set; } = string.Empty;
        public string ToolInput { get; set; } = string.Empty;
        public string Observation { get; set; } = string.Empty;
    }

    public class MessageHistory
    {
        public string Role { get; set; } = string.Empty; // "user", "assistant", "system"
        public string Content { get; set; } = string.Empty;
        public string? AgentName { get; set; }
        public DateTime Timestamp { get; set; }
    }
} 