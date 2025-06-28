using System.Text.Json;
using AgentPlatform.API.DTOs;

namespace AgentPlatform.API.Services
{
    public class ToolService : IToolService
    {
        private readonly IWebHostEnvironment _environment;
        private readonly string _toolsJsonPath;

        public ToolService(IWebHostEnvironment environment)
        {
            _environment = environment;
            _toolsJsonPath = Path.Combine(_environment.ContentRootPath, "..", "AgentPlatform.Core", "toolkit", "tools.json");
        }

        public async Task<List<ToolDto>> GetToolsAsync()
        {
            if (!File.Exists(_toolsJsonPath))
            {
                return [];
            }
            
            var json = await File.ReadAllTextAsync(_toolsJsonPath);
            var tools = JsonSerializer.Deserialize<List<ToolDto>>(json, new JsonSerializerOptions
            {
                PropertyNameCaseInsensitive = true
            });

            return tools ?? new List<ToolDto>();
        }

        public async Task<string> GetToolsJsonContentAsync()
        {
            if (!File.Exists(_toolsJsonPath))
            {
                throw new FileNotFoundException($"Tools JSON file not found at path: {_toolsJsonPath}");
            }
            
            return await File.ReadAllTextAsync(_toolsJsonPath);
        }
    }
} 