using Microsoft.EntityFrameworkCore;
using AutoMapper;
using AgentPlatform.API.Data;
using AgentPlatform.API.DTOs;
using AgentPlatform.API.Models;
using System.Text.Json;

namespace AgentPlatform.API.Services
{
    public class AgentService : IAgentService
    {
        private readonly ApplicationDbContext _context;
        private readonly IMapper _mapper;
        private readonly IWebHostEnvironment _environment;
        private readonly IToolService _toolService;
        private readonly string _agentsJsonPath;

        public AgentService(ApplicationDbContext context, IMapper mapper, IWebHostEnvironment environment, IToolService toolService)
        {
            _context = context;
            _mapper = mapper;
            _environment = environment;
            _toolService = toolService;
            
            // Path to agents.json in AgentPlatform.Core project
            _agentsJsonPath = Path.Combine(_environment.ContentRootPath, "..", "AgentPlatform.Core", "agents.json");
        }

        public async Task<List<AgentDto>> GetAgentsAsync(int userId)
        {
            var agents = await _context.Agents
                .Include(a => a.CreatedBy)
                .Include(a => a.Files)
                .Include(a => a.Functions)
                .Where(a => (a.CreatedById == userId || a.IsPublic) && a.IsActive)
                .ToListAsync();

            return _mapper.Map<List<AgentDto>>(agents);
        }

        public async Task<AgentDto?> GetAgentByIdAsync(int agentId, int userId)
        {
            var agent = await _context.Agents
                .Include(a => a.CreatedBy)
                .Include(a => a.Files)
                .Include(a => a.Functions)
                .FirstOrDefaultAsync(a => a.Id == agentId && (a.CreatedById == userId || a.IsPublic));

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
                IsPublic = request.IsPublic,
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

            if (request.IsPublic.HasValue)
                agent.IsPublic = request.IsPublic.Value;

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

                // Serialize with proper formatting
                var jsonOptions = new JsonSerializerOptions
                {
                    WriteIndented = true
                };

                var jsonContent = JsonSerializer.Serialize(agentJsonList, jsonOptions);

                // Ensure directory exists
                var directory = Path.GetDirectoryName(_agentsJsonPath);
                if (!string.IsNullOrEmpty(directory) && !Directory.Exists(directory))
                {
                    Directory.CreateDirectory(directory);
                }

                // Write to file
                await File.WriteAllTextAsync(_agentsJsonPath, jsonContent);
            }
            catch (Exception ex)
            {
                // Log the error but don't throw - JSON sync shouldn't break the main operations
                Console.WriteLine($"Failed to sync agents.json: {ex.Message}");
            }
        }

        public async Task SyncAgentsFromJsonAsync()
        {
            try
            {
                // Check if agents.json file exists
                if (!File.Exists(_agentsJsonPath))
                {
                    throw new FileNotFoundException($"agents.json file not found at path: {_agentsJsonPath}");
                }

                // Read and deserialize agents.json
                var jsonContent = await File.ReadAllTextAsync(_agentsJsonPath);
                var agentJsonList = JsonSerializer.Deserialize<List<AgentJsonDto>>(jsonContent);

                if (agentJsonList == null || !agentJsonList.Any())
                {
                    return;
                }

                // Get existing agents from database
                var existingAgents = await _context.Agents.ToListAsync();
                var existingAgentNames = existingAgents.Select(a => a.Name).ToHashSet();

                // Process each agent from JSON
                foreach (var agentJson in agentJsonList)
                {
                    if (string.IsNullOrEmpty(agentJson.AgentName))
                        continue;

                    // Check if agent already exists
                    var existingAgent = existingAgents.FirstOrDefault(a => a.Name == agentJson.AgentName);

                    if (existingAgent != null)
                    {
                        // Update existing agent
                        existingAgent.Description = agentJson.Description;
                        existingAgent.ToolsArray = agentJson.Tools ?? Array.Empty<string>();
                        existingAgent.ToolConfigs = agentJson.ToolConfigs?.ToString();
                        
                        if (agentJson.LlmConfig != null)
                        {
                            existingAgent.LlmModelName = agentJson.LlmConfig.ModelName;
                            existingAgent.LlmTemperature = agentJson.LlmConfig.Temperature;
                        }
                        
                        existingAgent.IsActive = true;
                        existingAgent.UpdatedAt = DateTime.UtcNow;
                    }
                    else
                    {
                        // Create new agent
                        var newAgent = new Agent
                        {
                            Name = agentJson.AgentName,
                            Department = "Imported", // Default department for imported agents
                            Description = agentJson.Description,
                            Instructions = null, // Not available in JSON format
                            ToolsArray = agentJson.Tools ?? Array.Empty<string>(),
                            ToolConfigs = agentJson.ToolConfigs?.ToString(),
                            LlmModelName = agentJson.LlmConfig?.ModelName,
                            LlmTemperature = agentJson.LlmConfig?.Temperature,
                            IsActive = true,
                            CreatedAt = DateTime.UtcNow,
                            CreatedById = 1 // Default system user ID - you may want to adjust this
                        };

                        _context.Agents.Add(newAgent);
                    }
                }

                // Save all changes
                await _context.SaveChangesAsync();
            }
            catch (Exception ex)
            {
                // Log the error and re-throw for the controller to handle
                Console.WriteLine($"Failed to sync agents from JSON: {ex.Message}");
                throw new InvalidOperationException($"Failed to sync agents from JSON: {ex.Message}", ex);
            }
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
    }
} 