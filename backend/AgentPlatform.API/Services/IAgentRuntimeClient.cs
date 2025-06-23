using AgentPlatform.Shared.Models;

namespace AgentPlatform.API.Services
{
    public interface IAgentRuntimeClient
    {
        Task<AgentRuntimeResponse> SendMessageAsync(AgentRuntimeRequest request);
        Task<string?> EnhancePromptAsync(string query);
        Task<bool> IsHealthyAsync();
    }
} 