using AgentPlatform.API.DTOs;

namespace AgentPlatform.API.Services
{
    public interface IAgentService
    {
        Task<List<AgentDto>> GetAgentsAsync(int userId);
        Task<AgentDto?> GetAgentByIdAsync(int agentId, int userId);
        Task<AgentDto> CreateAgentAsync(CreateAgentRequestDto request, int userId);
        Task<AgentDto?> UpdateAgentAsync(int agentId, UpdateAgentRequestDto request, int userId);
        Task<bool> DeleteAgentAsync(int agentId, int userId);
        Task<bool> AddFunctionToAgentAsync(int agentId, CreateAgentFunctionRequestDto request, int userId);
        Task SyncAgentsJsonAsync();
        Task SyncAgentsFromJsonAsync();
        Task<bool> SetAgentToolsAsync(int agentId, List<string> tools, int userId);
        Task<List<string>?> GetAgentToolsAsync(int agentId, int userId);
        Task<string> GetAgentsJsonContentAsync();
        Task<bool> UpdateAgentsFromJsonAsync(List<AgentJsonDto> agents, int userId);
    }
}