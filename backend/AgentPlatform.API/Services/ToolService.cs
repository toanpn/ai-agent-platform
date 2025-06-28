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
            
            // Try multiple paths in order of preference
            var possiblePaths = new[]
            {
                // Docker paths (production)
                "/AgentPlatform.Core/toolkit/tools.json",
                "/app/AgentPlatform.Core/toolkit/tools.json",
                
                // Local development paths
                Path.Combine(_environment.ContentRootPath, "..", "AgentPlatform.Core", "toolkit", "tools.json"),
                Path.Combine(Directory.GetCurrentDirectory(), "..", "AgentPlatform.Core", "toolkit", "tools.json"),
                
                // Fallback paths
                Path.Combine(_environment.ContentRootPath, "AgentPlatform.Core", "toolkit", "tools.json"),
                "toolkit/tools.json"
            };

            // Find the first existing path or use the first Docker path as default for production
            _toolsJsonPath = possiblePaths.FirstOrDefault(File.Exists) ?? possiblePaths[0];
            
            _logger.LogInformation("Using tools.json path: {ToolsJsonPath}", _toolsJsonPath);
            
            // Create the file if it doesn't exist to ensure the path is valid
            if (!File.Exists(_toolsJsonPath))
            {
                try
                {
                    var directory = Path.GetDirectoryName(_toolsJsonPath);
                    if (!string.IsNullOrEmpty(directory) && !Directory.Exists(directory))
                    {
                        Directory.CreateDirectory(directory);
                        _logger.LogInformation("Created directory: {Directory}", directory);
                    }
                    
                    File.WriteAllText(_toolsJsonPath, "[]");
                    _logger.LogInformation("Created empty tools.json file at: {ToolsJsonPath}", _toolsJsonPath);
                }
                catch (Exception ex)
                {
                    _logger.LogError(ex, "Failed to create tools.json file at: {ToolsJsonPath}", _toolsJsonPath);
                }
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