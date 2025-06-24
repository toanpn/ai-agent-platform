using System;

namespace AgentPlatform.API.DTOs
{
    public class ToolConfigDto
    {
        public int Id { get; set; }
        public string ToolName { get; set; } = string.Empty;
        public int AgentId { get; set; }
        public string ConfigSchema { get; set; } = string.Empty; // JSON schema as a string
        public DateTime CreatedAt { get; set; }
        public DateTime UpdatedAt { get; set; }
    }

    public class CreateToolConfigDto
    {
        public string ToolName { get; set; } = string.Empty;
        public int AgentId { get; set; }
        public string ConfigSchema { get; set; } = string.Empty; // JSON schema as a string
    }

    public class UpdateToolConfigDto
    {
        public string ConfigSchema { get; set; } = string.Empty; // JSON schema as a string
    }
}
