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
        private readonly string _agentsJsonPath;

        public AgentService(ApplicationDbContext context, IMapper mapper, IWebHostEnvironment environment)
        {
            _context = context;
            _mapper = mapper;
            _environment = environment;
            
            // Path to agents.json in AgentPlatform.Core project
            _agentsJsonPath = Path.Combine(_environment.ContentRootPath, "..", "AgentPlatform.Core", "agents.json");
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
    }
} 