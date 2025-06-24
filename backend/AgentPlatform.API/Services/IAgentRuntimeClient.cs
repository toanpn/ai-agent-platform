using AgentPlatform.Shared.Models;
using AgentPlatform.API.DTOs;

namespace AgentPlatform.API.Services
{
    public interface IAgentRuntimeClient
    {
        Task<AgentRuntimeResponse> SendMessageAsync(AgentRuntimeRequest request);
        Task<PromptEnhancementResponseDto?> EnhancePromptAsync(string query);
        Task<bool> IsHealthyAsync();
    }
} 