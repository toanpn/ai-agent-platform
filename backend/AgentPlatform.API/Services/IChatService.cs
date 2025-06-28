using AgentPlatform.API.DTOs;

namespace AgentPlatform.API.Services
{
    public interface IChatService
    {
        Task<ChatResponseDto> SendMessageAsync(int userId, SendMessageRequestDto request);
        Task<ChatHistoryDto> GetChatHistoryAsync(int userId, int page = 1, int pageSize = 10);
        Task<ChatHistoryDto> SearchChatHistoryAsync(int userId, string query, int page = 1, int pageSize = 10);
        Task<ChatSessionDto?> GetChatSessionAsync(int userId, int sessionId);
        Task<bool> DeleteChatSessionAsync(int userId, int sessionId);
        Task<PromptEnhancementResponseDto?> EnhancePromptAsync(string query);
    }
} 