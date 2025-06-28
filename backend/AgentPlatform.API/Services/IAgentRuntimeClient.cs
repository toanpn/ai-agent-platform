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
        Task<AgentSyncResponse?> SyncAgentsAsync(List<AgentJsonDto> agents);
        Task<ToolsResponse?> GetToolsAsync();
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

    // DTOs for Agent Sync operations
    public class AgentSyncResponse
    {
        public bool Success { get; set; }
        public string Message { get; set; } = string.Empty;
        public int AgentsSynced { get; set; }
        public int AgentsLoaded { get; set; }
        public string? Error { get; set; }
    }

    // DTOs for Tools operations
    public class ToolsResponse
    {
        public bool Success { get; set; }
        public List<ToolInfo> Data { get; set; } = new();
        public int TotalTools { get; set; }
        public string? Error { get; set; }
    }

    public class ToolInfo
    {
        public string Id { get; set; } = string.Empty;
        public string Name { get; set; } = string.Empty;
        public string? Description { get; set; }
        public string? File { get; set; }
        public Dictionary<string, object>? Parameters { get; set; }
    }
} 