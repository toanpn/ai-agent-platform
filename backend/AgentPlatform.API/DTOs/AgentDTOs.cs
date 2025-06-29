using System.ComponentModel.DataAnnotations;
using System.Text.Json.Serialization;

namespace AgentPlatform.API.DTOs
{
    public class CreateAgentRequestDto
    {
        [Required]
        public string Name { get; set; } = string.Empty;

        [Required]
        public string Department { get; set; } = string.Empty;

        public string? Description { get; set; }

        public string? Instructions { get; set; }

        public string[]? Tools { get; set; }

        public string? ToolConfigs { get; set; }

        public LlmConfigDto? LlmConfig { get; set; }
        
        public bool? IsPublic { get; set; }
    }
    
    public class SetToolsRequestDto
    {
        public List<string> Tools { get; set; } = [];
    }

    public class UpdateAgentRequestDto
    {
        public string? Name { get; set; }

        public string? Department { get; set; }

        public string? Description { get; set; }

        public string? Instructions { get; set; }

        public string[]? Tools { get; set; }

        public string? ToolConfigs { get; set; }

        public LlmConfigDto? LlmConfig { get; set; }

        public bool? IsActive { get; set; }

        public bool? IsPublic { get; set; }
    }

    public class AgentDto
    {
        public int Id { get; set; }
        public string Name { get; set; } = string.Empty;
        public string Department { get; set; } = string.Empty;
        public string? Description { get; set; }
        public string? Instructions { get; set; }
        public string[]? Tools { get; set; }
        public string? ToolConfigs { get; set; }
        public LlmConfigDto? LlmConfig { get; set; }
        public bool IsActive { get; set; }
        public bool IsMainRouter { get; set; }
        public bool IsPublic { get; set; }
        public UserDto CreatedBy { get; set; } = null!;
        public DateTime CreatedAt { get; set; }
        public DateTime? UpdatedAt { get; set; }
        public List<AgentFileDto> Files { get; set; } = new();
        public List<AgentFunctionDto> Functions { get; set; } = new();
    }

    public class LlmConfigDto
    {
        [JsonPropertyName("modelName")]
        public string? ModelName { get; set; }
        
        [JsonPropertyName("temperature")]
        public double? Temperature { get; set; }
    }

    // LLM configuration for agents.json file synchronization (Python backend format)
    public class AgentJsonLlmConfigDto
    {
        [JsonPropertyName("model_name")]
        public string? ModelName { get; set; }
        
        [JsonPropertyName("temperature")]
        public double? Temperature { get; set; }
    }

    // Agent JSON representation for agents.json file synchronization
    public class AgentJsonDto
    {
        [JsonPropertyName("agent_name")]
        public string AgentName { get; set; } = string.Empty;

        [JsonPropertyName("description")]
        public string? Description { get; set; }

        [JsonPropertyName("instruction")]
        public string? Instruction { get; set; }

        [JsonPropertyName("tools")]
        public string[]? Tools { get; set; }

        [JsonPropertyName("tool_configs")]
        public object? ToolConfigs { get; set; }

        [JsonPropertyName("llm_config")]
        public AgentJsonLlmConfigDto? LlmConfig { get; set; }

        [JsonPropertyName("is_public")]
        public bool IsPublic { get; set; }

        [JsonPropertyName("owner_id")]
        public string? OwnerId { get; set; }
    }

    public class AgentFileDto
    {
        public int Id { get; set; }
        public string FileName { get; set; } = string.Empty;
        public string? ContentType { get; set; }
        public long FileSize { get; set; }
        public bool IsIndexed { get; set; }
        public DateTime CreatedAt { get; set; }
    }

    public class AgentFunctionDto
    {
        public int Id { get; set; }
        public string Name { get; set; } = string.Empty;
        public string? Description { get; set; }
        public string? Schema { get; set; }
        public string? EndpointUrl { get; set; }
        public string? HttpMethod { get; set; }
        public bool IsActive { get; set; }
        public DateTime CreatedAt { get; set; }
    }

    public class CreateAgentFunctionRequestDto
    {
        [Required]
        public string Name { get; set; } = string.Empty;
        
        public string? Description { get; set; }
        
        public string? Schema { get; set; }
        
        [Required]
        public string EndpointUrl { get; set; } = string.Empty;
        
        public string HttpMethod { get; set; } = "POST";
        
        public string? Headers { get; set; }
    }
}