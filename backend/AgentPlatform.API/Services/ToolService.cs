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
            
            // Use absolute path for Docker, fallback to relative for development
            _toolsJsonPath = File.Exists("/AgentPlatform.Core/toolkit/tools.json") 
                ? "/AgentPlatform.Core/toolkit/tools.json"
                : Path.Combine(_environment.ContentRootPath, "..", "AgentPlatform.Core", "toolkit", "tools.json");
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
                return result;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error reading or parsing tools JSON file from path: {ToolsJsonPath}", _toolsJsonPath);
                throw;
            }
        }

        public async Task<string> GetToolsJsonContentAsync()
        {
            _logger.LogDebug("Attempting to read tools JSON from path: {ToolsJsonPath}", _toolsJsonPath);
            
            if (!File.Exists(_toolsJsonPath))
            {
                throw new FileNotFoundException($"Tools JSON file not found at path: {_toolsJsonPath}. Please ensure the AgentPlatform.Core toolkit/tools.json file exists and the application has read permissions.");
            }
            
            try
            {
                var content = await File.ReadAllTextAsync(_toolsJsonPath);
                return content;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error reading tools JSON file from path: {ToolsJsonPath}", _toolsJsonPath);
                throw;
            }
        }
    }
} 