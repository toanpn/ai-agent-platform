using System.Text.Json;
using AgentPlatform.API.DTOs;

namespace AgentPlatform.API.Services
{
    public class ToolService : IToolService
    {
        private readonly IWebHostEnvironment _environment;
        private readonly ILogger<ToolService> _logger;
        private readonly string _toolsJsonPath;

        public ToolService(IWebHostEnvironment environment, ILogger<ToolService> logger)
        {
            _environment = environment;
            _logger = logger;
            
            // Try multiple paths in order of preference with better Docker support
            var possiblePaths = new[]
            {
                // Docker production paths (exact mount points)
                "/AgentPlatform.Core/toolkit/tools.json",     // Main API container mount
                "/app/shared/tools.json",                     // Shared volume mount (preferred)
                "/app/AgentPlatform.Core/toolkit/tools.json", // Agent-Core mount point
                "/app/toolkit/tools.json",                    // Legacy mount (if exists)
                
                // Local development paths
                Path.Combine(_environment.ContentRootPath, "..", "AgentPlatform.Core", "toolkit", "tools.json"),
                Path.Combine(Directory.GetCurrentDirectory(), "..", "AgentPlatform.Core", "toolkit", "tools.json"),
                
                // Fallback paths
                Path.Combine(_environment.ContentRootPath, "AgentPlatform.Core", "toolkit", "tools.json"),
                "toolkit/tools.json"
            };

            // Log all possible paths for debugging
            _logger.LogInformation("Checking possible paths for tools.json:");
            foreach (var path in possiblePaths)
            {
                var exists = File.Exists(path);
                var canAccess = CanAccessPath(path);
                _logger.LogInformation("Path: {Path} - Exists: {Exists}, Accessible: {CanAccess}", path, exists, canAccess);
            }

            // Find the first existing and accessible path
            _toolsJsonPath = possiblePaths.FirstOrDefault(path => File.Exists(path) && CanAccessPath(path)) 
                             ?? possiblePaths[0]; // Fallback to first Docker path
            
            _logger.LogInformation("Selected tools.json path: {ToolsJsonPath}", _toolsJsonPath);
            
            // Initialize file with better error handling
            InitializeToolsFile();
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

        private void InitializeToolsFile()
        {
            // Only validate if file exists, don't create it
            if (File.Exists(_toolsJsonPath))
            {
                try
                {
                    var content = File.ReadAllText(_toolsJsonPath);
                    if (string.IsNullOrWhiteSpace(content))
                    {
                        _logger.LogWarning("tools.json file exists but is empty at: {ToolsJsonPath}", _toolsJsonPath);
                    }
                    else
                    {
                        _logger.LogInformation("tools.json file found and validated at: {ToolsJsonPath}", _toolsJsonPath);
                    }
                }
                catch (Exception ex)
                {
                    _logger.LogError(ex, "Failed to read existing tools.json file at: {ToolsJsonPath}", _toolsJsonPath);
                }
            }
            else
            {
                _logger.LogWarning("tools.json file not found at: {ToolsJsonPath}. Tools will not be available until the file is provided.", _toolsJsonPath);
            }
        }

        public async Task<List<ToolDto>> GetToolsAsync()
        {
            if (!File.Exists(_toolsJsonPath))
            {
                _logger.LogWarning("Tools JSON file not found at path: {ToolsJsonPath}, returning empty list", _toolsJsonPath);
                return [];
            }
            
            try
            {
                var json = await File.ReadAllTextAsync(_toolsJsonPath);
                var tools = JsonSerializer.Deserialize<List<ToolDto>>(json, new JsonSerializerOptions
                {
                    PropertyNameCaseInsensitive = true
                });

                var result = tools ?? new List<ToolDto>();
                _logger.LogDebug("Successfully loaded {Count} tools from {ToolsJsonPath}", result.Count, _toolsJsonPath);
                return result;
            }
            catch (UnauthorizedAccessException ex)
            {
                _logger.LogError(ex, "Access denied when reading tools.json from: {ToolsJsonPath}", _toolsJsonPath);
                throw;
            }
            catch (JsonException ex)
            {
                _logger.LogError(ex, "Invalid JSON format in tools.json at: {ToolsJsonPath}", _toolsJsonPath);
                throw;
            }
            catch (IOException ex)
            {
                _logger.LogError(ex, "IO error when reading tools.json from: {ToolsJsonPath}", _toolsJsonPath);
                throw;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Unexpected error reading or parsing tools JSON file from path: {ToolsJsonPath}", _toolsJsonPath);
                throw;
            }
        }

        public async Task<string> GetToolsJsonContentAsync()
        {
            if (!File.Exists(_toolsJsonPath))
            {
                throw new FileNotFoundException($"Tools JSON file not found at path: {_toolsJsonPath}");
            }
            
            try
            {
                var content = await File.ReadAllTextAsync(_toolsJsonPath);
                return content;
            }
            catch (UnauthorizedAccessException ex)
            {
                _logger.LogError(ex, "Access denied when reading tools.json from: {ToolsJsonPath}", _toolsJsonPath);
                throw;
            }
            catch (IOException ex)
            {
                _logger.LogError(ex, "IO error when reading tools.json from: {ToolsJsonPath}", _toolsJsonPath);
                throw;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Unexpected error reading tools JSON file from path: {ToolsJsonPath}", _toolsJsonPath);
                throw;
            }
        }
    }
} 