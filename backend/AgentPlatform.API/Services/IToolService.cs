using AgentPlatform.API.DTOs;
using System;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace AgentPlatform.API.Services
{
    public interface IToolService
    {
        Task<List<ToolDto>> GetToolsAsync();

        Task<ToolConfigDto> GetToolConfigAsync(int id);

        Task<IEnumerable<ToolConfigDto>> GetAgentToolConfigsAsync(int agentId, int userId);

        Task<ToolConfigDto> AddToolConfigAsync(CreateToolConfigDto toolConfigDto, int userId);

        Task<bool> UpdateToolConfigAsync(int id, UpdateToolConfigDto toolConfigDto, int agentId, int userId);

        Task<bool> DeleteToolConfigAsync(int id, int agentId, int userId);
    }
} 