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
    }

    public class MessageHistory
    {
        public string Role { get; set; } = string.Empty; // "user", "assistant", "system"
        public string Content { get; set; } = string.Empty;
        public string? AgentName { get; set; }
        public DateTime Timestamp { get; set; }
    }
} 