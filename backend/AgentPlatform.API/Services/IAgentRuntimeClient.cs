using AgentPlatform.Shared.Models;
using AgentPlatform.API.DTOs;

namespace AgentPlatform.API.Services
{
    public interface IAgentRuntimeClient
    {
        Task<AgentRuntimeResponse> SendMessageAsync(AgentRuntimeRequest request);
        Task<string?> GetSessionSummaryAsync(List<MessageHistory> messages);
        Task<PromptEnhancementResponseDto?> EnhancePromptAsync(string query);
        Task<bool> IsHealthyAsync();
        Task<RagUploadResponse?> UploadFileForProcessingAsync(string filePath, int agentId, Dictionary<string, object>? metadata = null);
        Task<bool> DeleteAgentDocumentsAsync(string agentId);
    }

    // DTOs for RAG operations
    public class RagUploadResponse
    {
        public bool Success { get; set; }
        public RagUploadResult? Result { get; set; }
        public string? Error { get; set; }
    }

    public class RagUploadResult
    {
        public string DocumentId { get; set; } = string.Empty;
        public int ChunksCreated { get; set; }
        public string AgentId { get; set; } = string.Empty;
        public string FileName { get; set; } = string.Empty;
        public long FileSize { get; set; }
        public string ProcessedAt { get; set; } = string.Empty;
    }
} 