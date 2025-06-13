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
    }

    public class ChatSessionDto
    {
        public int Id { get; set; }
        public string? Title { get; set; }
        public bool IsActive { get; set; }
        public DateTime CreatedAt { get; set; }
        public List<ChatMessageDto> Messages { get; set; } = new();
    }

    public class ChatResponseDto
    {
        public string Response { get; set; } = string.Empty;
        public string AgentName { get; set; } = string.Empty;
        public int SessionId { get; set; }
        public DateTime Timestamp { get; set; }
    }

    public class ChatHistoryDto
    {
        public List<ChatSessionDto> Sessions { get; set; } = new();
        public int TotalCount { get; set; }
        public int Page { get; set; }
        public int PageSize { get; set; }
    }
} 