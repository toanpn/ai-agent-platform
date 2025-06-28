using Microsoft.EntityFrameworkCore;
using AutoMapper;
using Microsoft.Extensions.Options;
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
        private readonly IWebHostEnvironment _environment;
        private readonly IToolService _toolService;
        private readonly ILogger<AgentService> _logger;
        private readonly string _agentsJsonPath;

        public AgentService(ApplicationDbContext context, IMapper mapper, IWebHostEnvironment environment, IToolService toolService, ILogger<AgentService> logger, IOptions<AgentManagementConfig> agentConfig)
        {
            _context = context;
            _mapper = mapper;
            _environment = environment;
            _toolService = toolService;
            _logger = logger;
            
            // Try multiple paths in order of preference with better Docker support
            var possiblePaths = new[]
            {
                // Docker production paths (exact mount points from docker-compose.yml)
                "/AgentPlatform.Core/agents.json",                    // API container mount (preferred)
                "/app/shared/agents.json",                            // Shared volume mount
                "/app/AgentPlatform.Core/agents.json",               // Agent-Core mount point
                
                // Local development paths
                Path.Combine(_environment.ContentRootPath, "..", "AgentPlatform.Core", "agents.json"),
                Path.Combine(Directory.GetCurrentDirectory(), "..", "AgentPlatform.Core", "agents.json"),
                
                // Configuration-based path
                agentConfig.Value?.AgentsJsonPath,
                
                // Fallback paths with explicit directory creation
                Path.Combine(_environment.WebRootPath ?? _environment.ContentRootPath, "agents.json"),
                Path.Combine("/tmp", "agents.json"), // Temporary fallback
                "agents.json"
            };

            // Log environment info for debugging
            _logger.LogInformation("=== AgentService Path Resolution Debug ===");
            _logger.LogInformation("Environment: {Environment}", _environment.EnvironmentName);
            _logger.LogInformation("ContentRootPath: {ContentRootPath}", _environment.ContentRootPath);
            _logger.LogInformation("WebRootPath: {WebRootPath}", _environment.WebRootPath);
            _logger.LogInformation("Current Directory: {CurrentDirectory}", Directory.GetCurrentDirectory());
            _logger.LogInformation("Configuration AgentsJsonPath: {ConfigPath}", agentConfig.Value?.AgentsJsonPath);
            
            // Check all root directories to understand container structure
            _logger.LogInformation("=== Container Structure Analysis ===");
            try
            {
                var rootDirs = Directory.GetDirectories("/").Take(20);
                _logger.LogInformation("Root directories: {RootDirs}", string.Join(", ", rootDirs));
                
                if (Directory.Exists("/AgentPlatform.Core"))
                {
                    var coreFiles = Directory.GetFiles("/AgentPlatform.Core").Take(10);
                    _logger.LogInformation("Files in /AgentPlatform.Core: {Files}", string.Join(", ", coreFiles));
                }
                
                if (Directory.Exists("/app"))
                {
                    var appDirs = Directory.GetDirectories("/app").Take(10);
                    _logger.LogInformation("Directories in /app: {Dirs}", string.Join(", ", appDirs));
                }
            }
            catch (Exception ex)
            {
                _logger.LogWarning(ex, "Failed to analyze container structure");
            }

            // Log all possible paths for debugging
            _logger.LogInformation("=== Path Resolution Attempts ===");
            foreach (var path in possiblePaths.Where(p => !string.IsNullOrEmpty(p)))
            {
                try
                {
                    var exists = File.Exists(path);
                    var dirExists = Directory.Exists(Path.GetDirectoryName(path) ?? "");
                    var canAccess = CanAccessPath(path);
                    
                    _logger.LogInformation("Path: {Path}", path);
                    _logger.LogInformation("  - File Exists: {Exists}", exists);
                    _logger.LogInformation("  - Directory Exists: {DirExists}", dirExists);
                    _logger.LogInformation("  - Can Access: {CanAccess}", canAccess);
                    
                    if (exists)
                    {
                        var fileInfo = new FileInfo(path);
                        _logger.LogInformation("  - File Size: {Size} bytes", fileInfo.Length);
                        _logger.LogInformation("  - Last Modified: {LastModified}", fileInfo.LastWriteTime);
                    }
                }
                catch (Exception ex)
                {
                    _logger.LogWarning(ex, "Error checking path: {Path}", path);
                }
            }

            // Find the first existing and accessible path
            _agentsJsonPath = possiblePaths
                .Where(path => !string.IsNullOrEmpty(path))
                .FirstOrDefault(path => File.Exists(path) && CanAccessPath(path));
            
            // If no existing file found, use the first preferred path and try to create it
            if (string.IsNullOrEmpty(_agentsJsonPath))
            {
                _agentsJsonPath = possiblePaths.First(p => !string.IsNullOrEmpty(p));
                _logger.LogWarning("No existing agents.json found. Will use fallback path: {FallbackPath}", _agentsJsonPath);
                
                // Try to create the directory and a default file synchronously
                EnsureAgentsJsonExists();
            }
            else
            {
                _logger.LogInformation("✓ Successfully found agents.json at: {AgentsJsonPath}", _agentsJsonPath);
            }
        }

        private void EnsureAgentsJsonExists()
        {
            try
            {
                var directory = Path.GetDirectoryName(_agentsJsonPath);
                if (!string.IsNullOrEmpty(directory) && !Directory.Exists(directory))
                {
                    _logger.LogInformation("Creating directory: {Directory}", directory);
                    Directory.CreateDirectory(directory);
                }

                if (!File.Exists(_agentsJsonPath))
                {
                    _logger.LogInformation("Creating default agents.json at: {Path}", _agentsJsonPath);
                    var defaultContent = "[]"; // Empty JSON array
                    File.WriteAllText(_agentsJsonPath, defaultContent);
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to ensure agents.json exists at: {Path}", _agentsJsonPath);
            }
        }

        private bool CanAccessPath(string path)
        {
            try
            {
                var directory = Path.GetDirectoryName(path);
                if (string.IsNullOrEmpty(directory)) return true;
                
                // Check if we can access the directory
                var dirInfo = new DirectoryInfo(directory);
                return dirInfo.Exists || Directory.Exists(directory) || CanCreateDirectory(directory);
            }
            catch
            {
                return false;
            }
        }

        private bool CanCreateDirectory(string directory)
        {
            try
            {
                // Check parent directory permissions
                var parent = Directory.GetParent(directory);
                return parent != null && parent.Exists;
            }
            catch
            {
                return false;
            }
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
            var maxRetries = 3;
            var tempPath = _agentsJsonPath + ".tmp";
            
            for (int attempt = 1; attempt <= maxRetries; attempt++)
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
                        _logger.LogInformation("Creating directory for sync: {Directory}", directory);
                        Directory.CreateDirectory(directory);
                    }

                    // Validate path accessibility before writing
                    if (!string.IsNullOrEmpty(directory))
                    {
                        var directoryInfo = new DirectoryInfo(directory);
                        if (!directoryInfo.Exists)
                        {
                            _logger.LogError("Directory does not exist after creation attempt: {Directory}", directory);
                            if (attempt < maxRetries)
                            {
                                await Task.Delay(1000 * attempt);
                                continue;
                            }
                            return;
                        }
                    }

                    // Write to temporary file first, then rename (atomic operation)
                    await File.WriteAllTextAsync(tempPath, jsonContent);
                    
                    // Atomic move
                    if (File.Exists(_agentsJsonPath))
                    {
                        File.Delete(_agentsJsonPath);
                    }
                    File.Move(tempPath, _agentsJsonPath);
                    
                    _logger.LogInformation("Successfully synced agents.json with {Count} agents (attempt {Attempt})", activeAgents.Count, attempt);
                    return; // Success, exit retry loop
                }
                catch (UnauthorizedAccessException ex)
                {
                    _logger.LogWarning(ex, "Access denied when trying to write agents.json to: {AgentsJsonPath} (attempt {Attempt}/{MaxRetries})", _agentsJsonPath, attempt, maxRetries);
                }
                catch (DirectoryNotFoundException ex)
                {
                    _logger.LogWarning(ex, "Directory not found when trying to write agents.json to: {AgentsJsonPath} (attempt {Attempt}/{MaxRetries})", _agentsJsonPath, attempt, maxRetries);
                }
                catch (IOException ex)
                {
                    _logger.LogWarning(ex, "IO error when trying to write agents.json to: {AgentsJsonPath} (attempt {Attempt}/{MaxRetries})", _agentsJsonPath, attempt, maxRetries);
                }
                catch (Exception ex)
                {
                    _logger.LogWarning(ex, "Failed to sync agents.json to path: {AgentsJsonPath} (attempt {Attempt}/{MaxRetries})", _agentsJsonPath, attempt, maxRetries);
                }

                // Clean up temp file if it exists
                if (File.Exists(tempPath))
                {
                    try
                    {
                        File.Delete(tempPath);
                    }
                    catch
                    {
                        // Ignore cleanup errors
                    }
                }

                // Wait before retry (except on last attempt)
                if (attempt < maxRetries)
                {
                    await Task.Delay(1000 * attempt);
                }
            }

            // If we get here, all retries failed
            _logger.LogError("Failed to sync agents.json after {MaxRetries} attempts. JSON sync is disabled until next operation.", maxRetries);
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
                _logger.LogError(ex, "Failed to sync agents from JSON");
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

        public async Task<string> GetAgentsJsonContentAsync()
        {
            if (!File.Exists(_agentsJsonPath))
            {
                throw new FileNotFoundException($"Agents JSON file not found at path: {_agentsJsonPath}");
            }
            
            return await File.ReadAllTextAsync(_agentsJsonPath);
        }
    }
} 