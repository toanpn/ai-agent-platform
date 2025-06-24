using AgentPlatform.API.Data;
using AgentPlatform.API.DTOs;
using AgentPlatform.API.Models;
using AutoMapper;
using Microsoft.EntityFrameworkCore;

namespace AgentPlatform.API.Services
{
    public class ToolService : IToolService
    {
        private readonly ApplicationDbContext _context;
        private readonly IMapper _mapper;

        public ToolService(ApplicationDbContext context, IMapper mapper)
        {
            _context = context;
            _mapper = mapper;
        }

        public async Task<List<ToolDto>> GetToolsAsync()
        {
            var tools = await _context.Tools.ToListAsync();
            return _mapper.Map<List<ToolDto>>(tools);
        }

        public async Task<ToolConfigDto> GetToolConfigAsync(int id)
        {
            var toolConfig = await _context.ToolConfigs.FindAsync(id);
            return _mapper.Map<ToolConfigDto>(toolConfig);
        }

        public async Task<IEnumerable<ToolConfigDto>> GetAgentToolConfigsAsync(int agentId, int userId)
        {
            var agent = await _context.Agents.FirstOrDefaultAsync(a => a.Id == agentId && a.CreatedById == userId);
            if (agent == null)
            {
                // Or throw an exception, based on desired behavior
                return new List<ToolConfigDto>();
            }

            var toolConfigs = await _context.ToolConfigs
                .Where(tc => tc.AgentId == agentId)
                .ToListAsync();
            return _mapper.Map<IEnumerable<ToolConfigDto>>(toolConfigs);
        }

        public async Task<ToolConfigDto> AddToolConfigAsync(CreateToolConfigDto toolConfigDto, int userId)
        {
            var agent = await _context.Agents.FirstOrDefaultAsync(a => a.Id == toolConfigDto.AgentId && a.CreatedById == userId);
            if (agent == null)
            {
                throw new UnauthorizedAccessException("Cannot add a tool config to an agent you don't own.");
            }

            var toolConfig = _mapper.Map<ToolConfig>(toolConfigDto);
            toolConfig.CreatedAt = DateTime.UtcNow;
            toolConfig.UpdatedAt = DateTime.UtcNow;

            _context.ToolConfigs.Add(toolConfig);
            await _context.SaveChangesAsync();

            return _mapper.Map<ToolConfigDto>(toolConfig);
        }

        public async Task<bool> UpdateToolConfigAsync(int id, UpdateToolConfigDto toolConfigDto, int agentId, int userId)
        {
            var agent = await _context.Agents.FirstOrDefaultAsync(a => a.Id == agentId && a.CreatedById == userId);
            if (agent == null)
            {
                return false; // User does not own the agent
            }

            var toolConfig = await _context.ToolConfigs.FirstOrDefaultAsync(tc => tc.Id == id && tc.AgentId == agentId);
            if (toolConfig == null)
            {
                return false;
            }

            _mapper.Map(toolConfigDto, toolConfig);
            toolConfig.UpdatedAt = DateTime.UtcNow;

            _context.ToolConfigs.Update(toolConfig);
            await _context.SaveChangesAsync();

            return true;
        }

        public async Task<bool> DeleteToolConfigAsync(int id, int agentId, int userId)
        {
            var agent = await _context.Agents.FirstOrDefaultAsync(a => a.Id == agentId && a.CreatedById == userId);
            if (agent == null)
            {
                return false; // User does not own the agent
            }

            var toolConfig = await _context.ToolConfigs.FirstOrDefaultAsync(tc => tc.Id == id && tc.AgentId == agentId);
            if (toolConfig == null)
            {
                return false;
            }

            _context.ToolConfigs.Remove(toolConfig);
            await _context.SaveChangesAsync();

            return true;
        }
    }
} 