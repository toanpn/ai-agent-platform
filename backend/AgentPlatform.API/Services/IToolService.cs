using AgentPlatform.API.DTOs;

namespace AgentPlatform.API.Services
{
    public interface IToolService
    {
        Task<List<ToolDto>> GetToolsAsync();
        Task<string> GetToolsJsonContentAsync();
    }
} 