using System.Text.Json.Serialization;
using System.Collections.Generic;

namespace AgentPlatform.API.DTOs
{
    public class ToolDto
    {
        [JsonPropertyName("id")]
        public string Id { get; set; } = string.Empty;

        [JsonPropertyName("name")]
        public string Name { get; set; } = string.Empty;

        [JsonPropertyName("description")]
        public string? Description { get; set; }

        [JsonPropertyName("file")]
        public string? File { get; set; }

        [JsonPropertyName("instruction")]
        public string? Instruction { get; set; }

        [JsonPropertyName("parameters")]
        public Dictionary<string, ToolParameterDto>? Parameters { get; set; }
    }

    public class ToolParameterDto
    {
        [JsonPropertyName("type")]
        public string? Type { get; set; }

        [JsonPropertyName("description")]
        public string? Description { get; set; }

        [JsonPropertyName("required")]
        public bool? Required { get; set; }

        [JsonPropertyName("default")]
        public object? Default { get; set; }

        [JsonPropertyName("is_credential")]
        public bool? IsCredential { get; set; }
    }
}