using Microsoft.EntityFrameworkCore;
using AutoMapper;
using AgentPlatform.API.Data;
using AgentPlatform.API.DTOs;
using AgentPlatform.API.Models;
using System.Text.Json;
using Microsoft.Extensions.Logging;

namespace AgentPlatform.API.Services
{
    public class AgentService : IAgentService
    {
        private readonly ApplicationDbContext _context;
        private readonly IMapper _mapper;
        private readonly IToolService _toolService;
        private readonly IAgentRuntimeClient _agentRuntimeClient;
        private readonly ILogger<AgentService> _logger;

        public AgentService(ApplicationDbContext context, IMapper mapper, IToolService toolService, IAgentRuntimeClient agentRuntimeClient, ILogger<AgentService> logger)
        {
            _context = context;
            _mapper = mapper;
            _toolService = toolService;
            _agentRuntimeClient = agentRuntimeClient;
            _logger = logger;
        }



        public async Task<List<AgentDto>> GetAgentsAsync(int userId)
        {
            var agents = await _context.Agents
                .Include(a => a.CreatedBy)
                .Include(a => a.Files)
                .Include(a => a.Functions)
                .Where(a => a.CreatedById == userId && a.IsActive)
                .ToListAsync();

            return _mapper.Map<List<AgentDto>>(agents);
        }

        public async Task<AgentDto?> GetAgentByIdAsync(int agentId, int userId)
        {
            var agent = await _context.Agents
                .Include(a => a.CreatedBy)
                .Include(a => a.Files)
                .Include(a => a.Functions)
                .FirstOrDefaultAsync(a => a.Id == agentId && a.CreatedById == userId);

            return agent == null ? null : _mapper.Map<AgentDto>(agent);
        }

        public async Task<AgentDto> CreateAgentAsync(CreateAgentRequestDto request, int userId)
        {
            var agent = new Agent
            {
                Name = request.Name,
                Department = request.Department,
                Description = request.Description,
                Instructions = request.Instructions,
                ToolsArray = request.Tools ?? Array.Empty<string>(),
                ToolConfigs = request.ToolConfigs,
                LlmModelName = request.LlmConfig?.ModelName,
                LlmTemperature = request.LlmConfig?.Temperature,
                CreatedById = userId,
                CreatedAt = DateTime.UtcNow
            };

            _context.Agents.Add(agent);
            await _context.SaveChangesAsync();

            // Load the created agent with includes
            agent = await _context.Agents
                .Include(a => a.CreatedBy)
                .Include(a => a.Files)
                .Include(a => a.Functions)
                .FirstAsync(a => a.Id == agent.Id);

            // Sync with agents.json
            await SyncAgentsJsonAsync();

            return _mapper.Map<AgentDto>(agent);
        }

        public async Task<AgentDto?> UpdateAgentAsync(int agentId, UpdateAgentRequestDto request, int userId)
        {
            var agent = await _context.Agents
                .FirstOrDefaultAsync(a => a.Id == agentId && a.CreatedById == userId);

            if (agent == null)
            {
                return null;
            }

            if (!string.IsNullOrEmpty(request.Name))
                agent.Name = request.Name;
            
            if (!string.IsNullOrEmpty(request.Department))
                agent.Department = request.Department;
            
            if (request.Description != null)
                agent.Description = request.Description;
            
            if (request.Instructions != null)
                agent.Instructions = request.Instructions;
                
            if (request.Tools != null)
                agent.ToolsArray = request.Tools;
                
            if (request.ToolConfigs != null)
                agent.ToolConfigs = request.ToolConfigs;
                
            if (request.LlmConfig != null)
            {
                agent.LlmModelName = request.LlmConfig.ModelName;
                agent.LlmTemperature = request.LlmConfig.Temperature;
            }
            
            if (request.IsActive.HasValue)
                agent.IsActive = request.IsActive.Value;

            agent.UpdatedAt = DateTime.UtcNow;

            await _context.SaveChangesAsync();

            // Reload with includes
            agent = await _context.Agents
                .Include(a => a.CreatedBy)
                .Include(a => a.Files)
                .Include(a => a.Functions)
                .FirstAsync(a => a.Id == agent.Id);

            // Sync with agents.json
            await SyncAgentsJsonAsync();

            return _mapper.Map<AgentDto>(agent);
        }

        public async Task<bool> DeleteAgentAsync(int agentId, int userId)
        {
            var agent = await _context.Agents
                .FirstOrDefaultAsync(a => a.Id == agentId && a.CreatedById == userId);

            if (agent == null)
            {
                return false;
            }

            // Soft delete
            agent.IsActive = false;
            agent.UpdatedAt = DateTime.UtcNow;

            await _context.SaveChangesAsync();
            
            // Sync with agents.json
            await SyncAgentsJsonAsync();
            
            return true;
        }

        public async Task<bool> AddFunctionToAgentAsync(int agentId, CreateAgentFunctionRequestDto request, int userId)
        {
            var agent = await _context.Agents
                .FirstOrDefaultAsync(a => a.Id == agentId && a.CreatedById == userId);

            if (agent == null)
            {
                return false;
            }

            var function = new AgentFunction
            {
                AgentId = agentId,
                Name = request.Name,
                Description = request.Description,
                Schema = request.Schema,
                EndpointUrl = request.EndpointUrl,
                HttpMethod = request.HttpMethod,
                Headers = request.Headers,
                CreatedAt = DateTime.UtcNow
            };

            _context.AgentFunctions.Add(function);
            await _context.SaveChangesAsync();

            return true;
        }

        public async Task<bool> SetAgentToolsAsync(int agentId, List<string> tools, int userId)
        {
            var agent = await _context.Agents
                .FirstOrDefaultAsync(a => a.Id == agentId && a.CreatedById == userId);

            if (agent == null)
            {
                return false;
            }

            var availableTools = await _toolService.GetToolsAsync();
            var availableToolNames = availableTools.Select(t => t.Name).ToHashSet();

            foreach (var tool in tools)
            {
                if (!availableToolNames.Contains(tool))
                {
                    return false;
                }
            }

            agent.ToolsArray = [.. tools];
            agent.UpdatedAt = DateTime.UtcNow;

            await _context.SaveChangesAsync();
            
            await SyncAgentsJsonAsync();

            return true;
        }

        public async Task SyncAgentsJsonAsync()
        {
            try
            {
                // Get all active agents from database
                var activeAgents = await _context.Agents
                    .Where(a => a.IsActive)
                    .ToListAsync();

                // Convert to JSON format
                var agentJsonList = _mapper.Map<List<AgentJsonDto>>(activeAgents);

                _logger.LogInformation("Syncing {Count} agents to Agent Core via HTTP API", activeAgents.Count);

                // Send to Agent Core via HTTP API
                var syncResponse = await _agentRuntimeClient.SyncAgentsAsync(agentJsonList);

                if (syncResponse?.Success == true)
                {
                    _logger.LogInformation("✅ Successfully synced agents: {Message} (Synced: {AgentsSynced}, Loaded: {AgentsLoaded})", 
                        syncResponse.Message, syncResponse.AgentsSynced, syncResponse.AgentsLoaded);
                }
                else
                {
                    var errorMessage = syncResponse?.Error ?? "Unknown error occurred";
                    _logger.LogError("❌ Failed to sync agents to Agent Core: {Error}", errorMessage);
                    throw new InvalidOperationException($"Failed to sync agents to Agent Core: {errorMessage}");
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "❌ Error syncing agents to Agent Core via HTTP API");
                throw new InvalidOperationException($"Failed to sync agents to Agent Core: {ex.Message}", ex);
            }
        }

        public async Task SyncAgentsFromJsonAsync()
        {
            // This method is now deprecated since we sync via HTTP API
            // Agents are automatically synced to Agent Core whenever they are created/updated
            // If you need to force a sync, use SyncAgentsJsonAsync instead
            _logger.LogWarning("SyncAgentsFromJsonAsync is deprecated. Agents are now synced via HTTP API automatically.");
            
            // Trigger a sync to Agent Core to ensure consistency
            await SyncAgentsJsonAsync();
        }

        public async Task<List<string>?> GetAgentToolsAsync(int agentId, int userId)
        {
            var agent = await _context.Agents
                .FirstOrDefaultAsync(a => a.Id == agentId && a.CreatedById == userId);

            if (agent == null)
            {
                return null;
            }

            return agent.ToolsArray.ToList();
        }

        public async Task<string> GetAgentsJsonContentAsync()
        {
            try
            {
                // Get all active agents from database
                var activeAgents = await _context.Agents
                    .Where(a => a.IsActive)
                    .ToListAsync();

                // Convert to JSON format
                var agentJsonList = _mapper.Map<List<AgentJsonDto>>(activeAgents);

                // Serialize with proper formatting
                var jsonOptions = new JsonSerializerOptions
                {
                    WriteIndented = true
                };

                return JsonSerializer.Serialize(agentJsonList, jsonOptions);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error generating agents JSON content");
                throw new InvalidOperationException($"Failed to generate agents JSON content: {ex.Message}", ex);
            }
        }
    }
} 